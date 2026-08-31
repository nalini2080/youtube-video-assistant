import re
from urllib.parse import urlparse, parse_qs


class InvalidYouTubeURLError(Exception):
    """Raised when a string cannot be parsed as a valid YouTube video URL."""
    pass


def extract_video_id(url: str) -> str:
    if not url or not isinstance(url, str):
        raise InvalidYouTubeURLError("URL must be a non-empty string")

    url = url.strip()

    try:
        parsed = urlparse(url)
    except ValueError:
        raise InvalidYouTubeURLError(f"Could not parse URL: {url}")

    if parsed.scheme not in ("http", "https"):
        raise InvalidYouTubeURLError(f"URL must start with http:// or https://: {url}")

    hostname = (parsed.hostname or "").lower().removeprefix("www.")

    video_id = None

    if hostname in ("youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            query_params = parse_qs(parsed.query)
            video_id = query_params.get("v", [None])[0]
        elif parsed.path.startswith("/embed/"):
            video_id = parsed.path.split("/embed/")[1].split("/")[0]
        elif parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/shorts/")[1].split("/")[0]
    elif hostname == "youtu.be":
        video_id = parsed.path.lstrip("/")

    if not video_id:
        raise InvalidYouTubeURLError(f"Could not find a video ID in URL: {url}")

    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise InvalidYouTubeURLError(f"Extracted string is not a valid video ID: {video_id}")

    return video_id