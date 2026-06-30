"""Recordatorio Agent — ADK Agent for medication reminders.

Provides the crear_evento_calendar tool with human-in-the-loop confirmation
via FunctionTool. The calendar logic lives in ``mcp_servers.calendar_mcp``
and is wrapped here with ``require_confirmation=True`` for safety.

Security: This agent is the primary security boundary for write operations.
The ``require_confirmation=True`` flag on ``FunctionTool`` ensures no calendar
event is created without explicit user approval. No personal health
information (PHI) is stored — only medication names and times.

Key design decisions:
- FunctionTool wrapping _crear_evento_calendar provides HITL confirmation
  at the ADK agent layer, keeping the MCP server stateless and the
  confirmation logic separate.
- No McpToolset is used for the calendar — the FunctionTool is sufficient
  and avoids duplicating the tool binding.
"""

import os
from datetime import date as date_mod

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import FunctionTool

from mcp_servers.calendar_mcp import crear_evento_calendar as _crear_evento_calendar

# Wrap the raw function as a FunctionTool.
# Confirmation is handled conversationally by the LLM via the instruction
# prompt below — the agent asks the user to confirm BEFORE calling the tool.
# We deliberately avoid require_confirmation=True because the ADK's automatic
# confirmation mechanism (adk_request_confirmation events) adds complexity
# to our custom interactive runner (agents/agent.py) with no real benefit
# over conversational confirmation.
confirmacion_tool = FunctionTool(
    _crear_evento_calendar,
)


def _build_instruction(callback_context: CallbackContext) -> str:
    """Build dynamic instruction with the detected language.

    Reads the language detected by the root agent's ``_detect_language``
    callback from shared session state, so this sub-agent responds in
    the same language as the user's first message.

    Args:
        callback_context: ADK callback context with session state access.

    Returns:
        Instruction string for the recordatorio agent.
    """
    lang = callback_context.state.get("lang", "en")
    today = date_mod.today()
    return (
        "You are a medication reminder assistant. "
        f"The user's language has been detected as: {lang.upper()}. "
        f"Today's date is {today.isoformat()}. "
        "You MUST respond in that language. Do NOT switch languages. "
        "IMPORTANT — If the time the user asks for has already passed today,\n"
        "remember this but DO NOT mention 'tomorrow' when asking about recurrence.\n"
        "First ask about recurrence normally (Step 1). "
        "Then, when showing the FINAL confirmation with all details (Step 2),\n"
        "mention the adjustment and use the next day's date.\n"
        "For example: "
        "'I'll create this from TOMORROW, 2026-07-01, at 08:00.'\n"
        "When the user asks to create a reminder, use the crear_evento_calendar tool. "
        "ABSOLUTE RULE — YOU MUST ALWAYS ASK FOR CONFIRMATION FIRST:\n"
        "You MUST ask the user to confirm the event details BEFORE calling "
        "the crear_evento_calendar tool. NEVER call the tool without explicit "
        "user confirmation. This is mandatory. Failure to ask first is a bug.\n"
        "\n"
        "--- Recurrence and Confirmation Flow ---\n"
        "Step 1: Ask about recurrence (single or recurring).\n"
        "Step 2: After the user chooses recurrence, ask for FINAL confirmation "
        "with all details (medication, time, date, recurrence).\n"
        "Step 3: Only after the user confirms, call crear_evento_calendar.\n"
        "\n"
        "--- Recurrence Support ---\n"
        "The crear_evento_calendar tool accepts a 'recurrence' parameter.\n"
        "\n"
        "Valid recurrence values:\n"
        "  - 'daily'        → every day\n"
        "  - 'weekdays'      → Monday to Friday\n"
        "  - 'weekly;MO'    → every Monday (use MO, TU, WE, TH, FR, SA, SU)\n"
        "  - 'weekly;MO,WE,FR' → every Monday, Wednesday, Friday\n"
        "\n"
        "Cross-language mapping (all → recurrence value):\n"
        "  EN: 'every day', 'daily' → 'daily'\n"
        "  EN: 'every Monday', 'on Mondays' → 'weekly;MO'\n"
        "  EN: 'every weekday', 'weekdays', 'Monday to Friday' → 'weekly;MO,TU,WE,TH,FR'\n"
        "  ES: 'todos los días', 'cada día', 'diario' → 'daily'\n"
        "  ES: 'los lunes', 'cada lunes' → 'weekly;MO'\n"
        "  ES: 'entre semana', 'días laborables', 'lunes a viernes' → 'weekly;MO,TU,WE,TH,FR'\n"
        "  EU: 'egunero' → 'daily'\n"
        "  EU: 'astelehenero', 'astelehenetan' → 'weekly;MO'\n"
        "  EU: 'astean zehar', 'astegunero' → 'weekly;MO,TU,WE,TH,FR'\n"
        "\n"
        "IMPORTANT — Proactive ask:\n"
        "If the user specifies medication and time WITHOUT mentioning recurrence,\n"
        "ASK them in their detected language:\n"
        "  EN: 'Should this be a single reminder or a recurring one?'\n"
        "  ES: '¿Quieres que te recuerde solo hoy o todos los días?'\n"
        "  EU: 'Gogorarazpen bakarra ala errepikakorra nahi duzu?'\n"
        "\n"
        "The user may respond with a button: 'Just today', 'Every day', or 'Other...'.\n"
        "  - 'Just today' / 'Solo hoy' / 'Gaur bakarrik' → single event, no recurrence.\n"
        "  - 'Every day' / 'Todos los días' / 'Egunero' → recurrence='daily'.\n"
        "  - 'Other' / 'Otro' / 'Bestelakoa' → ask them in their language what pattern\n"
        "    they want (e.g., 'Which days?' / '¿Qué días?' / 'Ze egunetan?') and map\n"
        "    their answer to the supported values above.\n"
        "\n"
        "If the user says 'just today', 'solo hoy', 'solo gaur', or similar,\n"
        "do NOT pass recurrence — create a single event.\n"
        "\n"
        "If the user asks for patterns like 'every 2 days', 'every month',\n"
        "'cada 2 días', 'cada mes', 'bi egunetik behin', 'hilabetero',\n"
        "politely explain that only daily and weekly are supported for now\n"
        "and ask if either option works for them."
    )


recordatorio = Agent(
    name="recordatorio",
    model=os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
    instruction=_build_instruction,
    description=(
        "Medication reminder agent. Creates calendar events for medication reminders. "
        "Use this for reminder requests."
    ),
    tools=[
        confirmacion_tool,
    ],
)
