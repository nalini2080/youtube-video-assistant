from unittest.mock import AsyncMock, patch


class TestRelevanceEndpoint:
    def test_empty_query_returns_422(self, client):
        response = client.post("/api/videos/nrbBmoINqtk/relevance", json={"query": ""})
        assert response.status_code == 422

    @patch("app.api.videos.fetch_transcript")
    @patch("app.api.videos.repo.get_chunks_for_video", new_callable=AsyncMock)
    @patch("app.api.videos.repo.get_or_create_video", new_callable=AsyncMock)
    def test_transcript_unavailable_returns_404(
        self, mock_get_or_create, mock_get_chunks, mock_transcript, client
    ):
        from app.schemas.transcript import TranscriptResponse

        fake_record = type("Rec", (), {"id": 1})()
        mock_get_or_create.return_value = (fake_record, False)
        mock_get_chunks.return_value = []  # cache miss -> tries a fresh fetch
        mock_transcript.return_value = TranscriptResponse(
            video_id="nrbBmoINqtk",
            available=False,
            reason="Transcripts are disabled for this video.",
        )

        response = client.post(
            "/api/videos/nrbBmoINqtk/relevance", json={"query": "does it cover pointers"}
        )

        assert response.status_code == 404
        assert "disabled" in response.json()["detail"]

    @patch("app.api.videos.repo.log_user_query", new_callable=AsyncMock)
    @patch("app.api.videos.analyze_video_relevance", new_callable=AsyncMock)
    @patch("app.api.videos.repo.save_chunks", new_callable=AsyncMock)
    @patch("app.api.videos.chunk_transcript")
    @patch("app.api.videos.fetch_transcript")
    @patch("app.api.videos.repo.get_chunks_for_video", new_callable=AsyncMock)
    @patch("app.api.videos.repo.get_or_create_video", new_callable=AsyncMock)
    def test_relevance_success_path(
        self,
        mock_get_or_create,
        mock_get_chunks,
        mock_transcript,
        mock_chunk,
        mock_save_chunks,
        mock_analyze,
        mock_log,
        client,
    ):
        from app.schemas.transcript import TranscriptResponse, TranscriptSnippet
        from app.schemas.chunk import TranscriptChunk
        from app.schemas.relevance import RelevanceResult

        fake_record = type("Rec", (), {"id": 1})()
        mock_get_or_create.return_value = (fake_record, False)
        mock_get_chunks.return_value = []
        mock_transcript.return_value = TranscriptResponse(
            video_id="nrbBmoINqtk",
            available=True,
            language="English",
            language_code="en",
            is_generated=True,
            snippets=[TranscriptSnippet(text="hello world", start=0.0, duration=1.0)],
        )
        fake_chunk = TranscriptChunk(
            video_id="nrbBmoINqtk", text="hello world", start_time=0.0, end_time=1.0
        )
        mock_chunk.return_value = [fake_chunk]
        mock_save_chunks.return_value = [fake_chunk]  # duck-typed stand-in for an ORM record
        mock_analyze.return_value = RelevanceResult(
            video_id="nrbBmoINqtk",
            relevant=True,
            score=0.9,
            reason="Covers the topic directly.",
            covered_topics=["basics"],
            missing_topics=[],
            relevant_timestamps=["0:00"],
        )

        response = client.post(
            "/api/videos/nrbBmoINqtk/relevance", json={"query": "does it cover the basics"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["relevant"] is True
        assert data["score"] == 0.9
        mock_log.assert_awaited_once()