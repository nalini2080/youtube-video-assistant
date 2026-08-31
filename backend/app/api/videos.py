from typing import List

from fastapi import APIRouter, HTTPException
from app.schemas.summary import VideoSummary
from app.services.ai_service import summarize_video, AISummarizationError

from app.schemas.video import VideoAnalyzeRequest, VideoMetadata
from app.schemas.transcript import TranscriptResponse
from app.schemas.chunk import TranscriptChunk
from app.utils.youtube_url import extract_video_id, InvalidYouTubeURLError
from app.services.youtube_service import (
    fetch_video_metadata,
    YouTubeAPIError,
    VideoNotFoundError,
)
from app.services.transcript_service import fetch_transcript
from app.services.chunking_service import chunk_transcript
from app.schemas.relevance import RelevanceRequest, RelevanceResult
from app.services.ai_service import (
    summarize_video,
    analyze_video_relevance,
    AISummarizationError,
    AIRelevanceError,
)

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.post("/analyze", response_model=VideoMetadata)
async def analyze_video(request: VideoAnalyzeRequest):
    try:
        video_id = extract_video_id(request.url)
    except InvalidYouTubeURLError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        metadata = await fetch_video_metadata(video_id)
    except VideoNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except YouTubeAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return metadata


@router.get("/{video_id}/transcript", response_model=TranscriptResponse)
def get_transcript(video_id: str):
    return fetch_transcript(video_id)


@router.get("/{video_id}/chunks", response_model=List[TranscriptChunk])
def get_transcript_chunks(video_id: str):
    transcript = fetch_transcript(video_id)
    if not transcript.available:
        raise HTTPException(
            status_code=404,
            detail=transcript.reason or "Transcript not available",
        )
    return chunk_transcript(video_id, transcript.snippets)

@router.post("/{video_id}/summary", response_model=VideoSummary)
async def get_video_summary(video_id: str):
    transcript = fetch_transcript(video_id)
    if not transcript.available:
        raise HTTPException(
            status_code=404,
            detail=transcript.reason or "Transcript not available",
        )

    chunks = chunk_transcript(video_id, transcript.snippets)

    try:
        return await summarize_video(chunks)
    except AISummarizationError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.post("/{video_id}/relevance", response_model=RelevanceResult)
async def get_video_relevance(video_id: str, request: RelevanceRequest):
    transcript = fetch_transcript(video_id)
    if not transcript.available:
        raise HTTPException(
            status_code=404,
            detail=transcript.reason or "Transcript not available",
        )

    chunks = chunk_transcript(video_id, transcript.snippets)

    try:
        return await analyze_video_relevance(video_id, chunks, request.query)
    except AIRelevanceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))