from pydantic import BaseModel


class EmbeddingStatus(BaseModel):
    video_id: str
    total_chunks: int
    embedded_chunks: int