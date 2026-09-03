from typing import List

from sqlalchemy import ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.database import Base

EMBEDDING_DIMENSIONS = 768


class TranscriptChunkRecord(Base):
    """A stored, timestamped chunk of a video's transcript."""

    __tablename__ = "transcript_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(Text)
    start_time: Mapped[float] = mapped_column(Float)
    end_time: Mapped[float] = mapped_column(Float)
    embedding: Mapped[List[float]] = mapped_column(Vector(EMBEDDING_DIMENSIONS), nullable=True)