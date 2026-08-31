from typing import List, Optional
from pydantic import BaseModel


class TranscriptSnippet(BaseModel):
    text: str
    start: float
    duration: float


class TranscriptResponse(BaseModel):
    video_id: str
    available: bool
    language: Optional[str] = None
    language_code: Optional[str] = None
    is_generated: Optional[bool] = None
    snippets: List[TranscriptSnippet] = []
    reason: Optional[str] = None