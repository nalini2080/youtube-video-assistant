from typing import List
from pydantic import BaseModel


class RelevanceRequest(BaseModel):
    query: str


class RelevanceResult(BaseModel):
    video_id: str
    relevant: bool
    score: float
    reason: str
    covered_topics: List[str]
    missing_topics: List[str]
    relevant_timestamps: List[str]