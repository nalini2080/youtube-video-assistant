import pytest
from pydantic import ValidationError

from app.schemas.relevance import RelevanceRequest
from app.schemas.chat import ChatRequest


class TestRelevanceRequestValidation:
    def test_valid_query_accepted(self):
        req = RelevanceRequest(query="how does gradient descent work")
        assert req.query == "how does gradient descent work"

    def test_strips_surrounding_whitespace(self):
        assert RelevanceRequest(query="  hello  ").query == "hello"

    def test_empty_query_rejected(self):
        with pytest.raises(ValidationError):
            RelevanceRequest(query="")

    def test_whitespace_only_query_rejected(self):
        with pytest.raises(ValidationError):
            RelevanceRequest(query="   ")

    def test_overly_long_query_rejected(self):
        with pytest.raises(ValidationError):
            RelevanceRequest(query="x" * 501)

    def test_max_length_query_accepted(self):
        assert len(RelevanceRequest(query="x" * 500).query) == 500


class TestChatRequestValidation:
    def test_valid_message_accepted(self):
        req = ChatRequest(message="does it cover pointers?")
        assert req.message == "does it cover pointers?"

    def test_empty_message_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_overly_long_message_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="x" * 1001)