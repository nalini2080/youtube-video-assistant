from pydantic import BaseModel


class VideoAnalyzeRequest(BaseModel):
    url: str


class VideoMetadata(BaseModel):
    video_id: str
    title: str
    description: str
    channel: str
    duration_seconds: int
    thumbnail_url: str