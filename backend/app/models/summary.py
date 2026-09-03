from datetime import datetime, timezone

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SummaryRecord(Base):
    """A stored general (non-personalized) summary for a video."""

    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id", ondelete="CASCADE"), index=True)
    # Structured data (overview/key_points/main_topics/takeaways) stored as
    # JSONB rather than flattened into a single text blob.
    summary: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )