from typing import List
from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def message_not_empty_or_huge(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty.")
        if len(v) > 1000:
            raise ValueError("Message is too long (max 1000 characters).")
        return v


class ChatSource(BaseModel):
    text: str
    start_time: float
    end_time: float


class ChatResponse(BaseModel):
    video_id: str
    answer: str
    sources: List[ChatSource]
    timestamps: List[str]