from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.video import VideoRecord
from app.models.transcript_chunk import TranscriptChunkRecord
from app.schemas.video import VideoAnalyzeRequest, VideoMetadata
from app.schemas.transcript import TranscriptResponse
from app.schemas.chunk import TranscriptChunk
from app.schemas.summary import VideoSummary
from app.schemas.relevance import RelevanceRequest, RelevanceResult
from app.schemas.personalized_summary import PersonalizedSummaryResult
from app.schemas.embedding import EmbeddingStatus
from app.utils.youtube_url import extract_video_id, InvalidYouTubeURLError
from app.services.youtube_service import (
    fetch_video_metadata,
    YouTubeAPIError,
    VideoNotFoundError,
)
from app.services.transcript_service import fetch_transcript
from app.services.chunking_service import chunk_transcript
from app.services.ai_service import (
    summarize_video,
    analyze_video_relevance,
    generate_personalized_summary,
    answer_chat_question,
    AISummarizationError,
    AIRelevanceError,
    AIPersonalizedSummaryError,
    AIChatError,
)
from typing import Optional
from app.schemas.history import SavedVideoItem, QueryHistoryItem, HistoryResponse
from app.services.auth_service import get_optional_user_id, require_user_id
from app.services.embedding_service import generate_embeddings_for_chunks, AIEmbeddingError
from app.services import video_repository as repo

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.embedding_service import (
    generate_embeddings_for_chunks,
    embed_query_text,
    AIEmbeddingError,
)
from app.schemas.suggestion import SuggestionsRequest, SuggestedVideo, SuggestionsResponse
from app.services.youtube_service import search_videos

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.post("/analyze", response_model=VideoMetadata)
async def analyze_video(request: VideoAnalyzeRequest, db: AsyncSession = Depends(get_db)):
    try:
        video_id = extract_video_id(request.url)
    except InvalidYouTubeURLError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    existing = await repo.get_video_by_youtube_id(db, video_id)
    if existing:
        return repo.video_record_to_metadata(existing)

    try:
        metadata = await fetch_video_metadata(video_id)
    except VideoNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except YouTubeAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    await repo.create_video(db, metadata)
    return metadata


async def _get_or_create_video_record(db: AsyncSession, video_id: str) -> VideoRecord:
    try:
        record, _ = await repo.get_or_create_video(db, video_id)
        return record
    except VideoNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except YouTubeAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


async def _get_or_create_chunk_records(
    db: AsyncSession, video_record: VideoRecord, youtube_id: str
) -> List[TranscriptChunkRecord]:
    cached = await repo.get_chunks_for_video(db, video_record.id)
    if cached:
        return cached

    transcript = fetch_transcript(youtube_id)
    if not transcript.available:
        raise HTTPException(
            status_code=404,
            detail=transcript.reason or "Transcript not available",
        )

    chunks = chunk_transcript(youtube_id, transcript.snippets)
    return await repo.save_chunks(db, video_record.id, chunks)


def _records_to_schema(records: List[TranscriptChunkRecord], youtube_id: str) -> List[TranscriptChunk]:
    return [repo.chunk_record_to_schema(r, youtube_id) for r in records]


@router.get("/{video_id}/transcript", response_model=TranscriptResponse)
def get_transcript(video_id: str):
    return fetch_transcript(video_id)


@router.get("/{video_id}/chunks", response_model=List[TranscriptChunk])
async def get_transcript_chunks(video_id: str, db: AsyncSession = Depends(get_db)):
    video_record = await _get_or_create_video_record(db, video_id)
    records = await _get_or_create_chunk_records(db, video_record, video_id)
    return _records_to_schema(records, video_id)


@router.post("/{video_id}/summary", response_model=VideoSummary)
async def get_video_summary(video_id: str, db: AsyncSession = Depends(get_db)):
    video_record = await _get_or_create_video_record(db, video_id)

    cached_summary = await repo.get_summary_for_video(db, video_record.id)
    if cached_summary:
        return VideoSummary(**cached_summary.summary)

    records = await _get_or_create_chunk_records(db, video_record, video_id)
    chunks = _records_to_schema(records, video_id)

    try:
        summary = await summarize_video(chunks)
    except AISummarizationError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    await repo.save_summary(db, video_record.id, summary)
    return summary


@router.post("/{video_id}/relevance", response_model=RelevanceResult)
async def get_video_relevance(
    video_id: str, request: RelevanceRequest, user_id: Optional[str] = Depends(get_optional_user_id), db: AsyncSession = Depends(get_db)
):
    video_record = await _get_or_create_video_record(db, video_id)
    records = await _get_or_create_chunk_records(db, video_record, video_id)
    chunks = _records_to_schema(records, video_id)

    try:
        result = await analyze_video_relevance(video_id, chunks, request.query)
    except AIRelevanceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    await repo.log_user_query(
        db, video_record.id, request.query, relevance_score=result.score, answer=result.reason
    )

    return result


@router.post("/{video_id}/personalized-summary", response_model=PersonalizedSummaryResult)
async def get_personalized_summary(
    video_id: str, request: RelevanceRequest, user_id: Optional[str] = Depends(get_optional_user_id), db: AsyncSession = Depends(get_db)
):
    video_record = await _get_or_create_video_record(db, video_id)
    records = await _get_or_create_chunk_records(db, video_record, video_id)
    chunks = _records_to_schema(records, video_id)

    try:
        result = await generate_personalized_summary(video_id, chunks, request.query)
    except AIPersonalizedSummaryError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    await repo.log_user_query(
        db, video_record.id, request.query, relevance_score=None, answer=result.summary
    )

    return result


@router.post("/{video_id}/embeddings", response_model=EmbeddingStatus)
async def get_video_embeddings(video_id: str, db: AsyncSession = Depends(get_db)):
    video_record = await _get_or_create_video_record(db, video_id)
    records = await _get_or_create_chunk_records(db, video_record, video_id)

    missing = [r for r in records if r.embedding is None]
    if missing:
        try:
            await generate_embeddings_for_chunks(missing)
        except AIEmbeddingError as exc:
            raise HTTPException(status_code=502, detail=str(exc))
        await repo.save_chunk_embeddings(db, missing)

    embedded_count = sum(1 for r in records if r.embedding is not None)
    return EmbeddingStatus(video_id=video_id, total_chunks=len(records), embedded_chunks=embedded_count)

@router.post("/{video_id}/chat", response_model=ChatResponse)
async def chat_with_video(video_id: str, request: ChatRequest, user_id: Optional[str] = Depends(get_optional_user_id), db: AsyncSession = Depends(get_db)):
    video_record = await _get_or_create_video_record(db, video_id)
    records = await _get_or_create_chunk_records(db, video_record, video_id)

    missing = [r for r in records if r.embedding is None]
    if missing:
        try:
            await generate_embeddings_for_chunks(missing)
        except AIEmbeddingError as exc:
            raise HTTPException(status_code=502, detail=str(exc))
        await repo.save_chunk_embeddings(db, missing)

    try:
        query_embedding = await embed_query_text(request.message)
    except AIEmbeddingError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    top_chunks_records = await repo.vector_search_chunks(db, video_record.id, query_embedding, top_k=5)
    top_chunks = _records_to_schema(top_chunks_records, video_id)

    try:
        response = await answer_chat_question(video_id, top_chunks, request.message)
    except AIChatError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    await repo.log_user_query(
        db, video_record.id, request.message, relevance_score=None, answer=response.answer
    )

    return response

@router.post("/{video_id}/save")
async def save_video(
    video_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_user_id),
):
    video_record = await _get_or_create_video_record(db, video_id)
    await repo.save_video_for_user(db, user_id, video_record.id)
    return {"saved": True}


@router.delete("/{video_id}/save")
async def unsave_video(
    video_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_user_id),
):
    video_record = await _get_or_create_video_record(db, video_id)
    await repo.unsave_video_for_user(db, user_id, video_record.id)
    return {"saved": False}


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_user_id),
):
    saved_rows = await repo.get_saved_videos_for_user(db, user_id)
    saved_videos = [
        SavedVideoItem(video=repo.video_record_to_metadata(v), saved_at=sv.saved_at.isoformat())
        for sv, v in saved_rows
    ]

    query_rows = await repo.get_recent_queries_for_user(db, user_id)
    recent_queries = [
        QueryHistoryItem(
            video_id=youtube_id,
            query=q.query,
            relevance_score=q.relevance_score,
            answer=q.answer,
            created_at=q.created_at.isoformat(),
        )
        for q, youtube_id in query_rows
    ]

    return HistoryResponse(saved_videos=saved_videos, recent_queries=recent_queries)

MAX_SUGGESTION_TOPICS = 1
RESULTS_PER_TOPIC = 3


@router.post("/{video_id}/suggestions", response_model=SuggestionsResponse)
async def get_video_suggestions(
    video_id: str, request: SuggestionsRequest, db: AsyncSession = Depends(get_db)
):
    topics = request.topics[:MAX_SUGGESTION_TOPICS]
    if not topics:
        return SuggestionsResponse(suggestions=[])

    allowed = await repo.try_consume_search_quota(db)
    if not allowed:
        return SuggestionsResponse(suggestions=[], quota_exceeded=True)

    topic = topics[0]
    try:
        results = await search_videos(topic, max_results=RESULTS_PER_TOPIC, exclude_video_id=video_id)
    except YouTubeAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    suggestions = [SuggestedVideo(topic=topic, **r) for r in results]
    return SuggestionsResponse(suggestions=suggestions)