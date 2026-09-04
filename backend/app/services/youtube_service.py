import re
import httpx

from app.config import settings
from app.schemas.video import VideoMetadata


class YouTubeAPIError(Exception):
    """Raised when the YouTube Data API call fails or returns unexpected data."""
    pass


class VideoNotFoundError(Exception):
    """Raised when the requested video ID does not exist or is private/deleted."""
    pass


def _parse_iso8601_duration(duration: str) -> int:
    match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not match:
        return 0
    hours, minutes, seconds = (int(g) if g else 0 for g in match.groups())
    return hours * 3600 + minutes * 60 + seconds


async def fetch_video_metadata(video_id: str) -> VideoMetadata:
    if not settings.youtube_api_key:
        raise YouTubeAPIError("YOUTUBE_API_KEY is not configured on the backend")

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,contentDetails",
        "id": video_id,
        "key": settings.youtube_api_key,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
        except httpx.RequestError as exc:
            raise YouTubeAPIError(f"Network error calling YouTube API: {exc}")

    if response.status_code == 403:
        raise YouTubeAPIError("YouTube API request forbidden — check your API key and quota")
    if response.status_code != 200:
        raise YouTubeAPIError(f"YouTube API returned status {response.status_code}: {response.text}")

    data = response.json()
    items = data.get("items", [])

    if not items:
        raise VideoNotFoundError(f"No video found for ID '{video_id}' (it may be private or deleted)")

    item = items[0]
    snippet = item["snippet"]
    content_details = item["contentDetails"]

    thumbnails = snippet.get("thumbnails", {})
    best_thumbnail = (
        thumbnails.get("high")
        or thumbnails.get("medium")
        or thumbnails.get("default")
        or {}
    )

    return VideoMetadata(
        video_id=video_id,
        title=snippet.get("title", ""),
        description=snippet.get("description", ""),
        channel=snippet.get("channelTitle", ""),
        duration_seconds=_parse_iso8601_duration(content_details.get("duration", "")),
        thumbnail_url=best_thumbnail.get("url", ""),
    )

async def search_videos(
    query: str, max_results: int = 3, exclude_video_id: str | None = None
) -> list[dict]:
    """
    Searches public YouTube videos matching a query. Note: search.list costs
    100 quota units per call (vs. 1 for a normal read) and is separately
    capped at 100 calls/day by YouTube regardless of remaining quota — so
    callers should use this sparingly, not on every request.
    """
    if not settings.youtube_api_key:
        raise YouTubeAPIError("YOUTUBE_API_KEY is not configured on the backend")

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": settings.youtube_api_key,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
        except httpx.RequestError as exc:
            raise YouTubeAPIError(f"Network error calling YouTube API: {exc}")

    if response.status_code == 403:
        raise YouTubeAPIError("YouTube API request forbidden — check your API key and quota")
    if response.status_code != 200:
        raise YouTubeAPIError(f"YouTube API returned status {response.status_code}: {response.text}")

    data = response.json()
    results = []
    for item in data.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        if not video_id or video_id == exclude_video_id:
            continue
        snippet = item.get("snippet", {})
        thumbnails = snippet.get("thumbnails", {})
        thumb = thumbnails.get("medium") or thumbnails.get("default") or {}
        results.append(
            {
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "thumbnail_url": thumb.get("url", ""),
            }
        )
    return results