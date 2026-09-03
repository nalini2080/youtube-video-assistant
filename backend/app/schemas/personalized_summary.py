from typing import List
from pydantic import BaseModel


class PersonalizedSummaryResult(BaseModel):
    video_id: str
    query: str
    summary: str
    relevant_points: List[str]
    timestamps: List[str]