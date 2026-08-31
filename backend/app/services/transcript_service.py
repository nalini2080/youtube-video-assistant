from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

from app.schemas.transcript import TranscriptResponse, TranscriptSnippet


def fetch_transcript(video_id: str) -> TranscriptResponse:
    """
    Attempt to retrieve a transcript for the given video ID.

    This deliberately does NOT raise for "expected" unavailability cases
    (disabled captions, no transcript in a usable language, etc.) — those
    are normal outcomes the frontend needs to display gracefully, not
    server errors. It returns available=False with a human-readable reason
    in those cases instead.
    """
    ytt_api = YouTubeTranscriptApi()

    try:
        fetched = ytt_api.fetch(video_id, languages=["en", "en-US", "en-GB"])
    except TranscriptsDisabled:
        return TranscriptResponse(
            video_id=video_id,
            available=False,
            reason="Transcripts are disabled for this video.",
        )
    except NoTranscriptFound:
        # No English transcript — fall back to whatever language IS available
        try:
            transcript_list = ytt_api.list(video_id)
            first_transcript = next(iter(transcript_list), None)
            if first_transcript is None:
                return TranscriptResponse(
                    video_id=video_id,
                    available=False,
                    reason="No transcript is available for this video in any language.",
                )
            fetched = first_transcript.fetch()
        except Exception:
            return TranscriptResponse(
                video_id=video_id,
                available=False,
                reason="No transcript is available for this video in a usable language.",
            )
    except VideoUnavailable:
        return TranscriptResponse(
            video_id=video_id,
            available=False,
            reason="This video is unavailable (it may be private or deleted).",
        )
    except Exception as exc:
        # Covers network failures, YouTube blocking our IP, and anything
        # else unexpected — surfaced as a reason rather than a crash.
        return TranscriptResponse(
            video_id=video_id,
            available=False,
            reason=f"Transcript retrieval failed: {exc}",
        )

    snippets = [
        TranscriptSnippet(text=s.text, start=s.start, duration=s.duration)
        for s in fetched
    ]

    return TranscriptResponse(
        video_id=video_id,
        available=True,
        language=fetched.language,
        language_code=fetched.language_code,
        is_generated=fetched.is_generated,
        snippets=snippets,
    )