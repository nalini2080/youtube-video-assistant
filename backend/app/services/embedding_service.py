import asyncio
from typing import List

from google import genai
from google.genai.types import EmbedContentConfig

from app.config import settings
from app.models.transcript_chunk import TranscriptChunkRecord, EMBEDDING_DIMENSIONS

MAX_BATCH_CHARS = 6000


class AIEmbeddingError(Exception):
    """Raised when generating embeddings via the Gemini API fails."""
    pass


def _get_client() -> genai.Client:
    if not settings.gemini_api_key:
        raise AIEmbeddingError("GEMINI_API_KEY is not configured on the backend")
    return genai.Client(api_key=settings.gemini_api_key)


def _batch_chunks(chunks: List[TranscriptChunkRecord]) -> List[List[TranscriptChunkRecord]]:
    """Group chunks so we embed many per API call instead of one call each."""
    batches: List[List[TranscriptChunkRecord]] = []
    current: List[TranscriptChunkRecord] = []
    current_len = 0

    for chunk in chunks:
        if current and current_len + len(chunk.text) > MAX_BATCH_CHARS:
            batches.append(current)
            current = []
            current_len = 0
        current.append(chunk)
        current_len += len(chunk.text)

    if current:
        batches.append(current)

    return batches


async def _embed_batch(client: genai.Client, batch: List[TranscriptChunkRecord]) -> None:
    response = await client.aio.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=[chunk.text for chunk in batch],
        config=EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )
    if len(response.embeddings) != len(batch):
        raise AIEmbeddingError("Mismatch between chunks sent and embeddings returned.")

    for chunk, embedding in zip(batch, response.embeddings):
        chunk.embedding = embedding.values


async def generate_embeddings_for_chunks(chunks: List[TranscriptChunkRecord]) -> None:
    """
    Generates an embedding for each chunk and assigns it to that chunk's
    `.embedding` attribute in place. Does NOT commit — the caller decides
    when to persist, keeping this function focused only on calling Gemini.
    """
    if not chunks:
        return

    client = _get_client()
    batches = _batch_chunks(chunks)

    try:
        await asyncio.gather(*[_embed_batch(client, batch) for batch in batches])
    except AIEmbeddingError:
        raise
    except Exception as exc:
        raise AIEmbeddingError(f"Failed to generate embeddings: {exc}")

async def embed_query_text(text: str) -> List[float]:
    """
    Embeds a single piece of text as a SEARCH QUERY, not a document.
    Gemini's embedding model produces different vectors for the same text
    depending on this role — using the wrong one here would silently hurt
    retrieval quality without throwing any error.
    """
    client = _get_client()
    response = await client.aio.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=text,
        config=EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )
    return response.embeddings[0].values