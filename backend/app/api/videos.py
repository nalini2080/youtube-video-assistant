from fastapi import APIRouter, HTTPException

from app.schemas.video import VideoAnalyzeRequest, VideoMetadata
from app.schemas.transcript import TranscriptResponse
from app.utils.youtube_url import extract_video_id, InvalidYouTubeURLError
from app.services.youtube_service import (
    fetch_video_metadata,
    YouTubeAPIError,
    VideoNotFoundError,
)
from app.services.transcript_service import fetch_transcript

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.post("/analyze", response_model=VideoMetadata)
async def analyze_video(request: VideoAnalyzeRequest):
    try:
        video_id = extract_video_id(request.url)
    except InvalidYouTubeURLError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        metadata = await fetch_video_metadata(video_id)
    except VideoNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except YouTubeAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return metadata


@router.get("/{video_id}/transcript", response_model=TranscriptResponse)
def get_transcript(video_id: str):
    return fetch_transcript(video_id)