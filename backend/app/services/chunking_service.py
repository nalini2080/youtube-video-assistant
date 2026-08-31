import re
from typing import List

from app.schemas.transcript import TranscriptSnippet
from app.schemas.chunk import TranscriptChunk

# Tunable thresholds — a chunk closes once EITHER limit is crossed.
MAX_CHUNK_CHARS = 1000
MAX_CHUNK_DURATION_SECONDS = 45.0


def _clean_text(text: str) -> str:
    """
    Collapse repeated whitespace/newlines into single spaces and trim.
    Raw transcript snippets sometimes carry stray newlines or double spaces.
    """
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_transcript(video_id: str, snippets: List[TranscriptSnippet]) -> List[TranscriptChunk]:
    """
    Group raw transcript snippets (often just a few words each) into larger,
    more coherent chunks.

    Strategy: accumulate consecutive snippets into a running chunk until
    EITHER the accumulated text exceeds MAX_CHUNK_CHARS OR the accumulated
    time span exceeds MAX_CHUNK_DURATION_SECONDS. Then that chunk is closed
    and a new one starts with the next snippet.
    """
    if not snippets:
        return []

    chunks: List[TranscriptChunk] = []
    current_texts: List[str] = []
    current_start: float = snippets[0].start
    current_end: float = snippets[0].start

    def flush_chunk():
        if not current_texts:
            return
        combined_text = _clean_text(" ".join(current_texts))
        if combined_text:
            chunks.append(
                TranscriptChunk(
                    video_id=video_id,
                    text=combined_text,
                    start_time=current_start,
                    end_time=current_end,
                )
            )

    for snippet in snippets:
        snippet_end = snippet.start + snippet.duration
        projected_text = " ".join(current_texts + [snippet.text])

        exceeds_chars = len(projected_text) > MAX_CHUNK_CHARS
        exceeds_duration = (snippet_end - current_start) > MAX_CHUNK_DURATION_SECONDS

        if current_texts and (exceeds_chars or exceeds_duration):
            flush_chunk()
            current_texts = []
            current_start = snippet.start

        current_texts.append(snippet.text)
        current_end = snippet_end

    flush_chunk()  # don't lose whatever's left in the last, unfinished chunk

    return chunks