from typing import List, Optional
from pydantic import BaseModel

from app.schemas.video import VideoMetadata


class SavedVideoItem(BaseModel):
    video: VideoMetadata
    saved_at: str


class QueryHistoryItem(BaseModel):
    video_id: str
    query: str
    relevance_score: Optional[float]
    answer: Optional[str]
    created_at: str


class HistoryResponse(BaseModel):
    saved_videos: List[SavedVideoItem]
    recent_queries: List[QueryHistoryItem]