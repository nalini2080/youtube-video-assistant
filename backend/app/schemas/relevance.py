from typing import List
from pydantic import BaseModel, field_validator


class RelevanceRequest(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def query_not_empty_or_huge(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty.")
        if len(v) > 500:
            raise ValueError("Query is too long (max 500 characters).")
        return v


class RelevanceResult(BaseModel):
    video_id: str
    relevant: bool
    score: float
    reason: str
    covered_topics: List[str]
    missing_topics: List[str]
    relevant_timestamps: List[str]