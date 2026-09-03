# Importing every model module here ensures they're all registered on
# Base.metadata before create_all() runs at startup — SQLAlchemy only
# knows to create tables for models it has actually seen imported.
from app.models.video import VideoRecord
from app.models.transcript_chunk import TranscriptChunkRecord
from app.models.summary import SummaryRecord
from app.models.user_query import UserQueryRecord

__all__ = [
    "VideoRecord",
    "TranscriptChunkRecord",
    "SummaryRecord",
    "UserQueryRecord",
]