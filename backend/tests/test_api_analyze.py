from unittest.mock import AsyncMock, patch

from app.schemas.video import VideoMetadata

SAMPLE_METADATA = VideoMetadata(
    video_id="nrbBmoINqtk",
    title="C tutorial for beginners",
    description="A beginner tutorial",
    channel="Bro Code",
    duration_seconds=757,
    thumbnail_url="https://example.com/thumb.jpg",
)


class TestAnalyzeEndpoint:
    def test_invalid_url_returns_400(self, client):
        response = client.post("/api/videos/analyze", json={"url": "not a url"})
        assert response.status_code == 400

    def test_missing_url_field_returns_422(self, client):
        response = client.post("/api/videos/analyze", json={})
        assert response.status_code == 422

    @patch("app.api.videos.repo.create_video", new_callable=AsyncMock)
    @patch("app.api.videos.fetch_video_metadata", new_callable=AsyncMock)
    @patch("app.api.videos.repo.get_video_by_youtube_id", new_callable=AsyncMock)
    def test_new_video_fetches_and_saves(self, mock_get, mock_fetch, mock_create, client):
        mock_get.return_value = None  # not cached yet
        mock_fetch.return_value = SAMPLE_METADATA

        response = client.post(
            "/api/videos/analyze",
            json={"url": "https://www.youtube.com/watch?v=nrbBmoINqtk"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["video_id"] == "nrbBmoINqtk"
        assert data["title"] == "C tutorial for beginners"
        mock_fetch.assert_awaited_once_with("nrbBmoINqtk")
        mock_create.assert_awaited_once()

    @patch("app.api.videos.fetch_video_metadata", new_callable=AsyncMock)
    @patch("app.api.videos.repo.video_record_to_metadata")
    @patch("app.api.videos.repo.get_video_by_youtube_id", new_callable=AsyncMock)
    def test_existing_video_skips_youtube_call(self, mock_get, mock_to_metadata, mock_fetch, client):
        mock_get.return_value = object()  # already cached
        mock_to_metadata.return_value = SAMPLE_METADATA

        response = client.post(
            "/api/videos/analyze",
            json={"url": "https://www.youtube.com/watch?v=nrbBmoINqtk"},
        )

        assert response.status_code == 200
        mock_fetch.assert_not_called()  # cache hit — no YouTube API call made

    @patch("app.api.videos.fetch_video_metadata", new_callable=AsyncMock)
    @patch("app.api.videos.repo.get_video_by_youtube_id", new_callable=AsyncMock)
    def test_video_not_found_returns_404(self, mock_get, mock_fetch, client):
        from app.services.youtube_service import VideoNotFoundError

        mock_get.return_value = None
        mock_fetch.side_effect = VideoNotFoundError("No video found")

        response = client.post(
            "/api/videos/analyze",
            json={"url": "https://www.youtube.com/watch?v=00000000000"},
        )

        assert response.status_code == 404

    @patch("app.api.videos.fetch_video_metadata", new_callable=AsyncMock)
    @patch("app.api.videos.repo.get_video_by_youtube_id", new_callable=AsyncMock)
    def test_youtube_api_error_returns_502(self, mock_get, mock_fetch, client):
        from app.services.youtube_service import YouTubeAPIError

        mock_get.return_value = None
        mock_fetch.side_effect = YouTubeAPIError("quota exceeded")

        response = client.post(
            "/api/videos/analyze",
            json={"url": "https://www.youtube.com/watch?v=nrbBmoINqtk"},
        )

        assert response.status_code == 502