from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, Text, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Text, Float, DateTime, String

from app.database import Base


class UserQueryRecord(Base):
    """A record of a user's 'what are you looking for' query for a video."""

    __tablename__ = "user_queries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id", ondelete="CASCADE"), index=True)
    query: Mapped[str] = mapped_column(Text)
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    user_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)