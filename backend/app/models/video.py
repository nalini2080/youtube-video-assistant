from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VideoRecord(Base):
    """Database row for a single analyzed video."""

    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    youtube_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, default="")
    channel: Mapped[str] = mapped_column(String(255))
    duration_seconds: Mapped[int] = mapped_column(Integer)
    thumbnail_url: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )