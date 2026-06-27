"""ADK agent wrapper — exposes the Aita-Lagun agent as an async callable.

Runner and session are created once on first call and reused thereafter
(lazy initialization). This avoids module-level async limitations (ADK's
``create_session`` is async) and keeps the module import-safe for testing.

Design decisions:
- Runner is created once so MCP subprocesses (PDF server) are spawned once,
  not per request. ADK's McpToolset manages subprocess lifecycle internally.
- The session is persistent so conversation context carries across turns (spec R4).
- Errors are caught and returned as strings rather than crashing the endpoint.
"""

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agents.agent import root_agent

_runner: Runner | None = None
_session_service: InMemorySessionService | None = None


async def _ensure_runner() -> Runner:
    """Lazily initialize the Runner singleton on first call.

    Returns:
        The shared Runner instance.
    """
    global _runner, _session_service

    if _runner is None:
        _session_service = InMemorySessionService()
        await _session_service.create_session(
            app_name="aita-lagun-web",
            user_id="web-user",
            session_id="visual-session",
        )
        _runner = Runner(
            agent=root_agent,
            app_name="aita-lagun-web",
            session_service=_session_service,
        )

    return _runner


async def ask_agent(message: str) -> str:
    """Send a message to the ADK agent and return the final response text.

    Args:
        message: User message text. Empty or whitespace-only strings return
            ``""`` immediately without calling the runner.

    Returns:
        The agent's final response as plain text, or an error message string
        if processing fails.
    """
    if not message or not message.strip():
        return ""

    runner = await _ensure_runner()

    reply_parts: list[str] = []
    try:
        async for event in runner.run_async(
            user_id="web-user",
            session_id="visual-session",
            new_message=genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=message)],
            ),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        reply_parts.append(part.text)

        return " ".join(reply_parts) if reply_parts else ""
    except Exception as e:
        return f"Error: {e}"
