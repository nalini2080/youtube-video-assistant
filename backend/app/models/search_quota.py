from datetime import date as date_type

from sqlalchemy import Date, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SearchQuotaRecord(Base):
    """
    Tracks how many YouTube search.list calls have been made today, so we
    stay well under YouTube's expensive (100-unit) search cost and its
    separate 100-calls/day hard cap — deliberately kept much lower than
    that ceiling here.
    """

    __tablename__ = "search_quota"

    quota_date: Mapped[date_type] = mapped_column(Date, primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=0)