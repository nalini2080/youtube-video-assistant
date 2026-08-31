import asyncio
import json
import re
from typing import List

from openai import AsyncOpenAI

from app.config import settings
from app.schemas.chunk import TranscriptChunk
from app.schemas.summary import VideoSummary
from app.schemas.relevance import RelevanceResult

MAX_GROUP_CHARS = 3000
MAX_RELEVANCE_CONTEXT_CHARS = 12000

class AIRelevanceError(Exception):
    """Raised when the AI relevance-analysis pipeline fails."""
    pass

class AISummarizationError(Exception):
    """Raised when the AI summarization pipeline fails at any stage."""
    pass

def _select_chunks_for_relevance_context(chunks: List[TranscriptChunk]) -> List[TranscriptChunk]:
    """
    Cap how much transcript text we send to the relevance-analysis prompt.
    Rather than truncating from the end (which would bias the analysis toward
    only the video's intro), we sample chunks evenly across the whole video
    so every section has a chance to be represented.
    """
    total_chars = sum(len(c.text) for c in chunks)
    if total_chars <= MAX_RELEVANCE_CONTEXT_CHARS or len(chunks) <= 1:
        return chunks

    target_count = max(1, int(len(chunks) * MAX_RELEVANCE_CONTEXT_CHARS / total_chars))
    if target_count >= len(chunks):
        return chunks

    step = len(chunks) / target_count
    indices = sorted({int(i * step) for i in range(target_count)})
    return [chunks[i] for i in indices]


def _format_chunks_with_timestamps(chunks: List[TranscriptChunk]) -> str:
    lines = []
    for chunk in chunks:
        minutes = int(chunk.start_time // 60)
        seconds = int(chunk.start_time % 60)
        lines.append(f"[{minutes}:{seconds:02d}] {chunk.text}")
    return "\n".join(lines)


async def analyze_video_relevance(
    video_id: str, chunks: List[TranscriptChunk], query: str
) -> RelevanceResult:
    if not chunks:
        raise AIRelevanceError("No transcript chunks available to analyze.")
    if not query.strip():
        raise AIRelevanceError("A query describing what you're looking for is required.")
    if not settings.openai_api_key:
        raise AIRelevanceError("OPENAI_API_KEY is not configured on the backend")

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    context_chunks = _select_chunks_for_relevance_context(chunks)
    formatted_transcript = _format_chunks_with_timestamps(context_chunks)

    prompt = f"""You are helping a viewer decide whether a YouTube video is relevant to what they're looking for.

The viewer's goal:
"{query}"

Below is the video transcript, broken into timestamped segments (format: [MM:SS] text):

{formatted_transcript}

Based ONLY on the transcript above, respond with a JSON object with exactly these keys:
- "relevant": boolean, whether this video is genuinely useful for the viewer's stated goal
- "score": a number from 0.0 to 1.0 indicating how relevant the video is to the goal
- "reason": a 1-3 sentence explanation of why it is or isn't relevant
- "covered_topics": a list of strings naming topics related to the viewer's goal that ARE covered in the video
- "missing_topics": a list of strings naming topics related to the viewer's goal that are NOT covered
- "relevant_timestamps": a list of up to 5 timestamp strings in "MM:SS" format, taken directly from the segments above, where the most relevant information appears (empty list if not relevant)

Respond with ONLY the JSON object. No markdown code fences, no extra text.
"""

    try:
        response = await client.responses.create(model=settings.openai_model, input=prompt)
        raw = _strip_json_fences(response.output_text)
        data = json.loads(raw)
        return RelevanceResult(video_id=video_id, **data)
    except json.JSONDecodeError as exc:
        raise AIRelevanceError(f"AI returned malformed JSON: {exc}")
    except Exception as exc:
        raise AIRelevanceError(f"Failed to analyze relevance: {exc}")

def _group_chunks_for_mapping(chunks: List[TranscriptChunk]) -> List[List[TranscriptChunk]]:
    """
    Batch transcript chunks together so the 'map' step makes far fewer,
    larger API calls instead of one tiny call per chunk.
    """
    groups: List[List[TranscriptChunk]] = []
    current: List[TranscriptChunk] = []
    current_len = 0

    for chunk in chunks:
        if current and current_len + len(chunk.text) > MAX_GROUP_CHARS:
            groups.append(current)
            current = []
            current_len = 0
        current.append(chunk)
        current_len += len(chunk.text)

    if current:
        groups.append(current)

    return groups


def _strip_json_fences(text: str) -> str:
    """
    Models sometimes wrap JSON in ```json ... ``` even when told not to.
    Strip that off before parsing.
    """
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


async def _summarize_group(client: AsyncOpenAI, group: List[TranscriptChunk]) -> str:
    combined_text = " ".join(chunk.text for chunk in group)
    prompt = (
        "Summarize the following portion of a YouTube video transcript in "
        "2-4 sentences. Be concise and factual — capture the key ideas discussed, "
        "not filler or small talk.\n\n"
        f"Transcript portion:\n{combined_text}"
    )
    response = await client.responses.create(model=settings.openai_model, input=prompt)
    return response.output_text.strip()


async def _reduce_to_final_summary(client: AsyncOpenAI, combined_summaries: str) -> VideoSummary:
    prompt = f"""You are analyzing a YouTube video based on section summaries of its transcript below. Produce a JSON object with exactly these keys:
- "overview": a short paragraph (2-4 sentences) explaining what the video is about
- "key_points": a list of 4-8 strings, the most important ideas discussed
- "main_topics": a list of 3-6 short strings naming concepts/topics covered
- "takeaways": a list of 2-5 strings describing what a viewer should remember

Respond with ONLY the JSON object. No markdown code fences, no extra text before or after.

Section summaries:
{combined_summaries}
"""
    response = await client.responses.create(model=settings.openai_model, input=prompt)
    raw = _strip_json_fences(response.output_text)
    data = json.loads(raw)
    return VideoSummary(**data)


async def summarize_video(chunks: List[TranscriptChunk]) -> VideoSummary:
    """
    Map-reduce summarization pipeline:
      chunks -> grouped batches -> per-batch summaries (parallel) -> final structured summary
    """
    if not chunks:
        raise AISummarizationError("No transcript chunks available to summarize.")

    if not settings.openai_api_key:
        raise AISummarizationError("OPENAI_API_KEY is not configured on the backend")

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    groups = _group_chunks_for_mapping(chunks)

    try:
        # Map step: summarize each group concurrently, not one at a time.
        group_summaries = await asyncio.gather(
            *[_summarize_group(client, group) for group in groups]
        )
    except Exception as exc:
        raise AISummarizationError(f"Failed to summarize transcript sections: {exc}")

    combined_summaries = "\n\n".join(
        f"Section {i + 1}: {summary}" for i, summary in enumerate(group_summaries)
    )

    try:
        # Reduce step: turn the condensed summaries into final structured output.
        return await _reduce_to_final_summary(client, combined_summaries)
    except json.JSONDecodeError as exc:
        raise AISummarizationError(f"AI returned malformed JSON: {exc}")
    except Exception as exc:
        raise AISummarizationError(f"Failed to generate final summary: {exc}")