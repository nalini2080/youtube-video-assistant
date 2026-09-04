from typing import List
from pydantic import BaseModel


class SuggestionsRequest(BaseModel):
    topics: List[str]


class SuggestedVideo(BaseModel):
    video_id: str
    title: str
    channel: str
    thumbnail_url: str
    topic: str


class SuggestionsResponse(BaseModel):
    suggestions: List[SuggestedVideo]
    quota_exceeded: bool = False