from pydantic import BaseModel


class TranscriptChunk(BaseModel):
    video_id: str
    text: str
    start_time: float
    end_time: float