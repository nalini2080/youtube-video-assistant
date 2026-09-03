from typing import List
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatSource(BaseModel):
    text: str
    start_time: float
    end_time: float


class ChatResponse(BaseModel):
    video_id: str
    answer: str
    sources: List[ChatSource]
    timestamps: List[str]