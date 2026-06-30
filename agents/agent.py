"""Root ADK Agent — Aita-Lagun multi-agent assistant.

Orchestrates RecordatorioAgent (medication reminders) and InfoSaludAgent
(health system information) via LLM-driven sub-agent routing.

Key design decisions:
- Language detection runs as a before_agent_callback so all downstream
  agents inherit the detected language without duplicate detection.
- Basque is checked FIRST because words like "gogoratu" and "kaixo" are
  unique to Basque, while Spanish and English share some overlap
  (e.g., "hola" is Spanish-only; "hello" is English-only).
- The `description` field on each sub-agent is the sole routing signal
  for the LLM — no custom routing logic needed.
"""

import asyncio
import os
from datetime import date as date_mod

from dotenv import load_dotenv
from google.adk.agents import Agent

load_dotenv()
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agents.orchestrator import recordatorio
from agents.info_salud_agent import info_salud_agent


def _has_word(text: str, word: str) -> bool:
    """Check if ``word`` appears as a standalone word in ``text``.

    Uses regex word boundary (\\b) matching so that e.g. ``_has_word("bailar", "bai")``
    returns ``False``, while ``_has_word("bai, esan", "bai")`` returns ``True``.
    """
    import re
    return bool(re.search(rf'\b{re.escape(word)}\b', text, re.IGNORECASE))


async def _detect_language(callback_context: CallbackContext) -> None:
    """Detect user language from the latest user message.

    Scans the most recent user message for language-specific keywords.
    Basque is checked first (least overlap with other supported languages),
    then Spanish, then English.

    Unlike the previous version, this runs on EVERY turn — it does NOT
    cache the result once per session. This allows the user to switch
    languages mid-session (e.g., test Basque, then switch to English).

    However, short follow-ups (e.g. "Every day", "Egunero", "Bai") often
    lack clear language signals. So we apply a "strong match only" rule:
    if the latest message matches a keyword, update the cached lang;
    if it doesn't match anything, KEEP the current lang unchanged.

    The detected language is stored in ``callback_context.state["lang"]``,
    which is read by the root and sub-agent instructions.

    Args:
        callback_context: ADK callback context with session state access.
    """
    # Iterate events in reverse to find the latest user message.
    history = callback_context.session.events
    for event in reversed(history):
        if event.content is None:
            continue
        if hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    text = part.text.lower()

                    # Basque checked first: these words are highly distinctive
                    # and unlikely to appear in English or Spanish text.
                    # Short words (bai, ez) use word-boundary matching to
                    # avoid false positives from substrings like "bail", "size".
                    if any(w in text for w in ['gogoratu', 'baieztatu', 'kaixo']):
                        callback_context.state["lang"] = "eu"
                        return
                    if _has_word(text, 'bai') or _has_word(text, 'ez'):
                        callback_context.state["lang"] = "eu"
                        return
                    if any(w in text for w in ['recuerda', 'cita', 'hola', 'gracias']):
                        callback_context.state["lang"] = "es"
                        return
                    if any(w in text for w in ['hello', 'hi', 'remember', 'remind']):
                        callback_context.state["lang"] = "en"
                        return
                    # No strong signal → keep current language unchanged,
                    # or set default if this is the first ever detection.
                    callback_context.state.setdefault("lang", "en")
                    return
    # No user message found at all. Set a sensible default.
    callback_context.state.setdefault("lang", "en")


def _build_instruction(callback_context: CallbackContext) -> str:
    """Build dynamic instruction with the detected language.

    Reads the language detected by ``_detect_language`` from callback state
    and injects it into the instruction so the LLM receives an unambiguous
    language signal rather than re-detecting from the user message.

    Args:
        callback_context: ADK callback context with session state access.

    Returns:
        Instruction string for the root agent.
    """
    lang = callback_context.state.get("lang", "en")
    today = date_mod.today()
    return (
        "You are Aita-Lagun, a helpful assistant for elderly people in Barakaldo "
        "(Basque Country, Spain). "
        f"The user's language has been detected as: {lang.upper()}. "
        f"Today's date is {today.isoformat()}. "
        "You MUST respond in that language throughout the entire conversation. "
        "Do NOT switch languages unless the user explicitly changes. "
        "Do NOT mix languages in your response."

        "For medication reminders (e.g., 'remind me to take Sintrom at 8am', "
        "'recuerda tomarme la pastilla', 'gogoratu pastilla 8etan'), "
        "delegate to the recordatorio agent. "

        "For questions about Osakidetza health system (e.g., 'how to book an appointment', "
        "'horarios centro salud Barakaldo', 'cita previa Osakidetza'), "
        "delegate to the info_salud agent."
    )


root_agent = Agent(
    name="aita_lagun",
    model=os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
    instruction=_build_instruction,
    description="Root agent for Aita-Lagun assistant.",
    sub_agents=[recordatorio, info_salud_agent],
    before_agent_callback=_detect_language,
)


async def main():
    """Entry point: run the ADK agent interactively.

    Each turn sends the user's text as a new message to the runner.
    Confirmation is handled conversationally by the LLM (the agent asks,
    the user replies, then the agent calls the tool) — no ADK HITL
    confirmation infrastructure is used.
    """
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="aita_lagun",
        user_id="user",
        session_id="default",
    )
    runner = Runner(
        agent=root_agent,
        app_name="aita_lagun",
        session_service=session_service,
    )

    print("Aita-Lagun assistant ready. Type 'exit' to quit.")
    print("Supported: en / es / eu")

    try:
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ("exit", "quit", "salir", "salida", "agurtu"):
                print("Agent: Goodbye! / ¡Adiós! / Agur!")
                break

            async for event in runner.run_async(
                user_id="user",
                session_id="default",
                new_message=genai_types.Content(
                    role="user",
                    parts=[genai_types.Part.from_text(text=user_input)],
                ),
            ):
                if event.is_final_response() and event.content:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            print(f"Agent: {part.text}")
    except KeyboardInterrupt:
        print("\nAgent: Goodbye! / ¡Adiós! / Agur!")
    except Exception as e:
        print(f"Agent: Something went wrong — {e}")


if __name__ == "__main__":
    asyncio.run(main())
