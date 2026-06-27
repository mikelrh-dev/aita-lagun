"""Tests for the chat API and agent runner.

Tests follow the existing project patterns:
- unittest.mock for mocking ADK dependencies
- asyncio_mode=auto (no @pytest.mark.asyncio needed)
- TestClient for FastAPI endpoint tests
"""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient


class TestAgentRunner:
    """Tests for app.agent_runner.ask_agent()."""

    async def test_ask_agent_returns_reply(self):
        """ask_agent returns the agent's text response when given a message."""
        import app.agent_runner

        mock_runner = MagicMock()
        app.agent_runner._runner = mock_runner

        async def mock_run_async(**kwargs):
            event = MagicMock()
            event.content.parts = [MagicMock(text="Hello! How can I help you?")]
            yield event

        mock_runner.run_async = mock_run_async

        from app.agent_runner import ask_agent

        result = await ask_agent("Hello")
        assert result == "Hello! How can I help you?"

    async def test_ask_agent_empty_message(self):
        """ask_agent returns empty string for empty input without calling the runner."""
        import app.agent_runner

        mock_runner = MagicMock()
        app.agent_runner._runner = mock_runner

        from app.agent_runner import ask_agent

        result = await ask_agent("")
        assert result == ""
        # Runner should not be called for empty messages
        mock_runner.run_async.assert_not_called()


class TestChatAPI:
    """Tests for the FastAPI chat endpoint."""

    def test_chat_endpoint_returns_200(self):
        """POST /api/chat with valid message returns 200 and reply."""
        with patch("app.agent_runner.ask_agent", new_callable=AsyncMock) as mock_ask:
            mock_ask.return_value = "Hello! How can I help you?"

            from app.main import app

            client = TestClient(app)
            response = client.post("/api/chat", json={"message": "hello"})

            assert response.status_code == 200
            data = response.json()
            assert "reply" in data
            assert data["reply"] == "Hello! How can I help you?"

    def test_chat_endpoint_returns_422(self):
        """POST /api/chat with empty body returns 422."""
        from app.main import app

        client = TestClient(app)
        response = client.post("/api/chat", json={})
        assert response.status_code == 422

    def test_health_check(self):
        """GET /health returns 200 with status ok."""
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
