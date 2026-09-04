from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.video import VideoRecord
from app.models.transcript_chunk import TranscriptChunkRecord
from app.models.summary import SummaryRecord
from app.models.user_query import UserQueryRecord
from app.schemas.video import VideoMetadata
from app.schemas.chunk import TranscriptChunk
from app.schemas.summary import VideoSummary
from app.models.saved_video import SavedVideoRecord
from datetime import date as date_type
from app.models.search_quota import SearchQuotaRecord

DAILY_SEARCH_LIMIT = 3


async def get_video_by_youtube_id(db: AsyncSession, youtube_id: str) -> Optional[VideoRecord]:
    result = await db.execute(select(VideoRecord).where(VideoRecord.youtube_id == youtube_id))
    return result.scalar_one_or_none()


async def create_video(db: AsyncSession, metadata: VideoMetadata) -> VideoRecord:
    record = VideoRecord(
        youtube_id=metadata.video_id,
        title=metadata.title,
        description=metadata.description,
        channel=metadata.channel,
        duration_seconds=metadata.duration_seconds,
        thumbnail_url=metadata.thumbnail_url,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_or_create_video(db: AsyncSession, youtube_id: str) -> Tuple[VideoRecord, bool]:
    """
    Returns (record, created). If the video isn't in the DB yet, fetches its
    metadata from YouTube and stores it. Lets endpoints other than /analyze
    (e.g. calling /chunks directly) still work without a prior /analyze call.
    """
    existing = await get_video_by_youtube_id(db, youtube_id)
    if existing:
        return existing, False

    from app.services.youtube_service import fetch_video_metadata  # local import avoids a circular import

    metadata = await fetch_video_metadata(youtube_id)
    record = await create_video(db, metadata)
    return record, True


def video_record_to_metadata(record: VideoRecord) -> VideoMetadata:
    return VideoMetadata(
        video_id=record.youtube_id,
        title=record.title,
        description=record.description,
        channel=record.channel,
        duration_seconds=record.duration_seconds,
        thumbnail_url=record.thumbnail_url,
    )


async def get_chunks_for_video(db: AsyncSession, video_record_id: int) -> List[TranscriptChunkRecord]:
    result = await db.execute(
        select(TranscriptChunkRecord)
        .where(TranscriptChunkRecord.video_id == video_record_id)
        .order_by(TranscriptChunkRecord.start_time)
    )
    return list(result.scalars().all())


async def save_chunks(
    db: AsyncSession, video_record_id: int, chunks: List[TranscriptChunk]
) -> List[TranscriptChunkRecord]:
    records = [
        TranscriptChunkRecord(
            video_id=video_record_id,
            text=chunk.text,
            start_time=chunk.start_time,
            end_time=chunk.end_time,
        )
        for chunk in chunks
    ]
    db.add_all(records)
    await db.commit()
    return records


def chunk_record_to_schema(record: TranscriptChunkRecord, youtube_id: str) -> TranscriptChunk:
    return TranscriptChunk(
        video_id=youtube_id,
        text=record.text,
        start_time=record.start_time,
        end_time=record.end_time,
    )


async def get_summary_for_video(db: AsyncSession, video_record_id: int) -> Optional[SummaryRecord]:
    result = await db.execute(
        select(SummaryRecord).where(SummaryRecord.video_id == video_record_id)
    )
    return result.scalar_one_or_none()


async def save_summary(db: AsyncSession, video_record_id: int, summary: VideoSummary) -> SummaryRecord:
    record = SummaryRecord(video_id=video_record_id, summary=summary.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def log_user_query(
    db: AsyncSession,
    video_record_id: int,
    query: str,
    relevance_score: Optional[float] = None,
    answer: Optional[str] = None,
    user_id: Optional[str] = None,
) -> UserQueryRecord:
    record = UserQueryRecord(
        video_id=video_record_id,
        query=query,
        relevance_score=relevance_score,
        answer=answer,
        user_id=user_id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record
async def save_chunk_embeddings(db: AsyncSession, chunks: List[TranscriptChunkRecord]) -> None:
    """Persists whatever is currently set on each chunk's `.embedding` attribute."""
    await db.commit()

async def vector_search_chunks(
    db: AsyncSession, video_record_id: int, query_embedding: List[float], top_k: int = 5
) -> List[TranscriptChunkRecord]:
    """
    Finds the chunks whose embeddings are most semantically similar to the
    query embedding, using cosine distance (lower = more similar).
    Scoped to one video via video_id, and skips any chunk that hasn't been
    embedded yet.
    """
    result = await db.execute(
        select(TranscriptChunkRecord)
        .where(TranscriptChunkRecord.video_id == video_record_id)
        .where(TranscriptChunkRecord.embedding.is_not(None))
        .order_by(TranscriptChunkRecord.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )
    return list(result.scalars().all())

async def save_video_for_user(db: AsyncSession, user_id: str, video_record_id: int) -> None:
    existing = await db.execute(
        select(SavedVideoRecord).where(
            SavedVideoRecord.user_id == user_id, SavedVideoRecord.video_id == video_record_id
        )
    )
    if existing.scalar_one_or_none():
        return
    db.add(SavedVideoRecord(user_id=user_id, video_id=video_record_id))
    await db.commit()


async def unsave_video_for_user(db: AsyncSession, user_id: str, video_record_id: int) -> None:
    result = await db.execute(
        select(SavedVideoRecord).where(
            SavedVideoRecord.user_id == user_id, SavedVideoRecord.video_id == video_record_id
        )
    )
    record = result.scalar_one_or_none()
    if record:
        await db.delete(record)
        await db.commit()


async def get_saved_videos_for_user(db: AsyncSession, user_id: str):
    result = await db.execute(
        select(SavedVideoRecord, VideoRecord)
        .join(VideoRecord, SavedVideoRecord.video_id == VideoRecord.id)
        .where(SavedVideoRecord.user_id == user_id)
        .order_by(SavedVideoRecord.saved_at.desc())
    )
    return result.all()


async def get_recent_queries_for_user(db: AsyncSession, user_id: str, limit: int = 20):
    result = await db.execute(
        select(UserQueryRecord, VideoRecord.youtube_id)
        .join(VideoRecord, UserQueryRecord.video_id == VideoRecord.id)
        .where(UserQueryRecord.user_id == user_id)
        .order_by(UserQueryRecord.created_at.desc())
        .limit(limit)
    )
    return result.all()

async def try_consume_search_quota(db: AsyncSession) -> bool:
    """
    Attempts to reserve one YouTube search.list call against today's quota.
    Returns True and increments the counter if under the daily limit,
    False (without calling YouTube) if today's limit is already used up.
    """
    today = date_type.today()
    result = await db.execute(
        select(SearchQuotaRecord).where(SearchQuotaRecord.quota_date == today)
    )
    record = result.scalar_one_or_none()

    if record is None:
        record = SearchQuotaRecord(quota_date=today, count=0)
        db.add(record)

    if record.count >= DAILY_SEARCH_LIMIT:
        return False

    record.count += 1
    await db.commit()
    return True