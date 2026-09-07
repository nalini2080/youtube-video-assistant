from app.schemas.transcript import TranscriptSnippet
from app.services.chunking_service import (
    chunk_transcript,
    MAX_CHUNK_CHARS,
    MAX_CHUNK_DURATION_SECONDS,
)


def make_snippet(text, start, duration):
    return TranscriptSnippet(text=text, start=start, duration=duration)


class TestChunkTranscript:
    def test_empty_snippets_returns_empty_list(self):
        assert chunk_transcript("vid123", []) == []

    def test_single_snippet_becomes_one_chunk(self):
        chunks = chunk_transcript("vid123", [make_snippet("hello world", 0.0, 2.0)])
        assert len(chunks) == 1
        assert chunks[0].text == "hello world"
        assert chunks[0].start_time == 0.0
        assert chunks[0].end_time == 2.0

    def test_short_snippets_merge_into_one_chunk(self):
        snippets = [
            make_snippet("one", 0.0, 1.0),
            make_snippet("two", 1.0, 1.0),
            make_snippet("three", 2.0, 1.0),
        ]
        chunks = chunk_transcript("vid123", snippets)
        assert len(chunks) == 1
        assert chunks[0].text == "one two three"
        assert chunks[0].start_time == 0.0
        assert chunks[0].end_time == 3.0

    def test_splits_when_duration_limit_exceeded(self):
        snippets = [
            make_snippet("first", 0.0, MAX_CHUNK_DURATION_SECONDS - 1),
            make_snippet("second", MAX_CHUNK_DURATION_SECONDS - 1, 5.0),
        ]
        chunks = chunk_transcript("vid123", snippets)
        assert len(chunks) == 2
        assert chunks[0].text == "first"
        assert chunks[1].text == "second"

    def test_splits_when_char_limit_exceeded(self):
        long_text = "x" * (MAX_CHUNK_CHARS + 10)
        snippets = [make_snippet(long_text, 0.0, 1.0), make_snippet("short", 1.0, 1.0)]
        chunks = chunk_transcript("vid123", snippets)
        assert len(chunks) == 2

    def test_collapses_repeated_whitespace(self):
        chunks = chunk_transcript("vid123", [make_snippet("hello    world\nnewline", 0.0, 1.0)])
        assert chunks[0].text == "hello world newline"

    def test_video_id_is_preserved(self):
        chunks = chunk_transcript("abc123", [make_snippet("hi", 0.0, 1.0)])
        assert chunks[0].video_id == "abc123"

    def test_chunks_never_overlap_in_time(self):
        snippets = [make_snippet(f"word{i}", float(i), 1.0) for i in range(20)]
        chunks = chunk_transcript("vid123", snippets)
        for prev, curr in zip(chunks, chunks[1:]):
            assert prev.end_time <= curr.start_time