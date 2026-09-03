import asyncio
import json
import re
from typing import List

from google import genai

from app.config import settings
from app.schemas.chunk import TranscriptChunk
from app.schemas.summary import VideoSummary
from app.schemas.relevance import RelevanceResult
from app.schemas.personalized_summary import PersonalizedSummaryResult

# Larger batches = fewer API calls per video, which matters more than token
# count on a free tier (request-count limits, not just token limits).
# Flash-Lite's huge context window means this costs us nothing in quality.
MAX_GROUP_CHARS = 8000
MAX_RELEVANCE_CONTEXT_CHARS = 12000


class AISummarizationError(Exception):
    pass


class AIRelevanceError(Exception):
    pass


class AIPersonalizedSummaryError(Exception):
    pass


def _get_client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured on the backend")
    return genai.Client(api_key=settings.gemini_api_key)


async def _generate_text(client: genai.Client, prompt: str) -> str:
    """Single shared entry point for calling Gemini — every AI feature goes through this."""
    response = await client.aio.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
    )
    return (response.text or "").strip()


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _group_chunks_for_mapping(chunks: List[TranscriptChunk]) -> List[List[TranscriptChunk]]:
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


def _select_chunks_for_relevance_context(chunks: List[TranscriptChunk]) -> List[TranscriptChunk]:
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


# ---------- Phase 5: General summarization (map-reduce) ----------

async def _summarize_group(client: genai.Client, group: List[TranscriptChunk]) -> str:
    combined_text = " ".join(chunk.text for chunk in group)
    prompt = (
        "Summarize the following portion of a YouTube video transcript in "
        "2-4 sentences. Be concise and factual — capture the key ideas discussed, "
        "not filler or small talk.\n\n"
        f"Transcript portion:\n{combined_text}"
    )
    return await _generate_text(client, prompt)


async def _reduce_to_final_summary(client: genai.Client, combined_summaries: str) -> VideoSummary:
    prompt = f"""You are analyzing a YouTube video based on section summaries of its transcript below. Produce a JSON object with exactly these keys:
- "overview": a short paragraph (2-4 sentences) explaining what the video is about
- "key_points": a list of 4-8 strings, the most important ideas discussed
- "main_topics": a list of 3-6 short strings naming concepts/topics covered
- "takeaways": a list of 2-5 strings describing what a viewer should remember

Respond with ONLY the JSON object. No markdown code fences, no extra text before or after.

Section summaries:
{combined_summaries}
"""
    raw = _strip_json_fences(await _generate_text(client, prompt))
    data = json.loads(raw)
    return VideoSummary(**data)


async def summarize_video(chunks: List[TranscriptChunk]) -> VideoSummary:
    if not chunks:
        raise AISummarizationError("No transcript chunks available to summarize.")

    try:
        client = _get_client()
    except RuntimeError as exc:
        raise AISummarizationError(str(exc))

    groups = _group_chunks_for_mapping(chunks)

    try:
        group_summaries = await asyncio.gather(
            *[_summarize_group(client, group) for group in groups]
        )
    except Exception as exc:
        raise AISummarizationError(f"Failed to summarize transcript sections: {exc}")

    combined_summaries = "\n\n".join(
        f"Section {i + 1}: {summary}" for i, summary in enumerate(group_summaries)
    )

    try:
        return await _reduce_to_final_summary(client, combined_summaries)
    except json.JSONDecodeError as exc:
        raise AISummarizationError(f"AI returned malformed JSON: {exc}")
    except Exception as exc:
        raise AISummarizationError(f"Failed to generate final summary: {exc}")


# ---------- Phase 7: Relevance analysis ----------

async def analyze_video_relevance(
    video_id: str, chunks: List[TranscriptChunk], query: str
) -> RelevanceResult:
    if not chunks:
        raise AIRelevanceError("No transcript chunks available to analyze.")
    if not query.strip():
        raise AIRelevanceError("A query describing what you're looking for is required.")

    try:
        client = _get_client()
    except RuntimeError as exc:
        raise AIRelevanceError(str(exc))

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
        raw = _strip_json_fences(await _generate_text(client, prompt))
        data = json.loads(raw)
        return RelevanceResult(video_id=video_id, **data)
    except json.JSONDecodeError as exc:
        raise AIRelevanceError(f"AI returned malformed JSON: {exc}")
    except Exception as exc:
        raise AIRelevanceError(f"Failed to analyze relevance: {exc}")


# ---------- Phase 8: Personalized summary ----------

async def generate_personalized_summary(
    video_id: str, chunks: List[TranscriptChunk], query: str
) -> PersonalizedSummaryResult:
    if not chunks:
        raise AIPersonalizedSummaryError("No transcript chunks available to summarize.")
    if not query.strip():
        raise AIPersonalizedSummaryError("A query describing what you're looking for is required.")

    try:
        client = _get_client()
    except RuntimeError as exc:
        raise AIPersonalizedSummaryError(str(exc))

    context_chunks = _select_chunks_for_relevance_context(chunks)
    formatted_transcript = _format_chunks_with_timestamps(context_chunks)

    prompt = f"""A viewer is deciding whether to watch a YouTube video and has told you what they're looking for:

"{query}"

Below is the video transcript, broken into timestamped segments (format: [MM:SS] text):

{formatted_transcript}

Write a personalized summary that answers: "How does this video help ME, given what I said I'm looking for?"
Focus specifically on the parts of the video relevant to the viewer's goal. Do not summarize unrelated parts of the video.

Respond with a JSON object with exactly these keys:
- "summary": 2-4 sentences written directly to the viewer (use "you"/"your"), explaining what this video offers for their specific goal
- "relevant_points": a list of 3-6 strings, specific points from the video that relate to the viewer's goal
- "timestamps": a list of up to 5 timestamp strings in "MM:SS" format, taken directly from the segments above, marking where the relevant content appears (empty list if nothing relevant)

Respond with ONLY the JSON object. No markdown code fences, no extra text.
"""

    try:
        raw = _strip_json_fences(await _generate_text(client, prompt))
        data = json.loads(raw)
        return PersonalizedSummaryResult(video_id=video_id, query=query, **data)
    except json.JSONDecodeError as exc:
        raise AIPersonalizedSummaryError(f"AI returned malformed JSON: {exc}")
    except Exception as exc:
        raise AIPersonalizedSummaryError(f"Failed to generate personalized summary: {exc}")


from app.schemas.chat import ChatResponse, ChatSource


class AIChatError(Exception):
    """Raised when the RAG chat pipeline fails."""
    pass


def _format_sources_with_timestamps(chunks: List[TranscriptChunk]) -> str:
    lines = []
    for chunk in chunks:
        minutes = int(chunk.start_time // 60)
        seconds = int(chunk.start_time % 60)
        lines.append(f"[{minutes}:{seconds:02d}] {chunk.text}")
    return "\n".join(lines)


async def answer_chat_question(
    video_id: str, retrieved_chunks: List[TranscriptChunk], question: str
) -> ChatResponse:
    if not retrieved_chunks:
        return ChatResponse(
            video_id=video_id,
            answer="I couldn't find any relevant information in this video's transcript to answer that.",
            sources=[],
            timestamps=[],
        )

    try:
        client = _get_client()
    except RuntimeError as exc:
        raise AIChatError(str(exc))

    formatted_context = _format_sources_with_timestamps(retrieved_chunks)

    prompt = f"""You are answering a viewer's question about a YouTube video, using ONLY the transcript excerpts below.

Viewer's question:
"{question}"

Relevant transcript excerpts (format: [MM:SS] text):
{formatted_context}

Instructions:
- Answer using ONLY information from the excerpts above.
- If the excerpts don't actually contain enough information to answer the question, say so plainly instead of guessing — do not use outside knowledge.
- Reference specific timestamps from the excerpts where relevant.
- Keep the answer concise (2-5 sentences).

Answer:"""

    try:
        answer_text = await _generate_text(client, prompt)
    except Exception as exc:
        raise AIChatError(f"Failed to generate chat answer: {exc}")

    sources = [
        ChatSource(text=c.text, start_time=c.start_time, end_time=c.end_time)
        for c in retrieved_chunks
    ]
    timestamps = [
        f"{int(c.start_time // 60)}:{int(c.start_time % 60):02d}" for c in retrieved_chunks
    ]

    return ChatResponse(video_id=video_id, answer=answer_text, sources=sources, timestamps=timestamps)