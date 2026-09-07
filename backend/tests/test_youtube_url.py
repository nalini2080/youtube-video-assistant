import pytest
from app.utils.youtube_url import extract_video_id, InvalidYouTubeURLError


class TestExtractVideoId:
    def test_standard_watch_url(self):
        assert extract_video_id("https://www.youtube.com/watch?v=nrbBmoINqtk") == "nrbBmoINqtk"

    def test_watch_url_without_www(self):
        assert extract_video_id("https://youtube.com/watch?v=nrbBmoINqtk") == "nrbBmoINqtk"

    def test_watch_url_with_extra_params(self):
        assert extract_video_id("https://www.youtube.com/watch?v=nrbBmoINqtk&t=42s") == "nrbBmoINqtk"

    def test_short_url(self):
        assert extract_video_id("https://youtu.be/nrbBmoINqtk") == "nrbBmoINqtk"

    def test_embed_url(self):
        assert extract_video_id("https://www.youtube.com/embed/nrbBmoINqtk") == "nrbBmoINqtk"

    def test_shorts_url(self):
        assert extract_video_id("https://www.youtube.com/shorts/nrbBmoINqtk") == "nrbBmoINqtk"

    def test_mobile_subdomain(self):
        assert extract_video_id("https://m.youtube.com/watch?v=nrbBmoINqtk") == "nrbBmoINqtk"

    def test_strips_whitespace(self):
        assert extract_video_id("  https://youtu.be/nrbBmoINqtk  ") == "nrbBmoINqtk"

    def test_empty_string_raises(self):
        with pytest.raises(InvalidYouTubeURLError):
            extract_video_id("")

    def test_non_youtube_url_raises(self):
        with pytest.raises(InvalidYouTubeURLError):
            extract_video_id("https://vimeo.com/12345678")

    def test_missing_scheme_raises(self):
        with pytest.raises(InvalidYouTubeURLError):
            extract_video_id("youtube.com/watch?v=nrbBmoINqtk")

    def test_watch_url_without_video_id_raises(self):
        with pytest.raises(InvalidYouTubeURLError):
            extract_video_id("https://www.youtube.com/watch")

    def test_malformed_video_id_length_raises(self):
        with pytest.raises(InvalidYouTubeURLError):
            extract_video_id("https://youtu.be/short")