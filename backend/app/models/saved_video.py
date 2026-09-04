from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SavedVideoRecord(Base):
    """A video a signed-in user has explicitly bookmarked."""

    __tablename__ = "saved_videos"
    __table_args__ = (UniqueConstraint("user_id", "video_id", name="uq_saved_video_per_user"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id", ondelete="CASCADE"), index=True)
    saved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )