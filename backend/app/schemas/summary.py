from typing import List
from pydantic import BaseModel


class VideoSummary(BaseModel):
    overview: str
    key_points: List[str]
    main_topics: List[str]
    takeaways: List[str]