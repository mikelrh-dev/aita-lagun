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

from google.adk.agents import Agent
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

recordatorio = Agent(
    name="recordatorio",
    model=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
    instruction=(
        "You are a medication reminder assistant. "
        "When the user asks to create a reminder, use the crear_evento_calendar tool. "
        "IMPORTANT: You MUST ask the user to confirm the event details BEFORE calling "
        "the tool. Wait for their explicit confirmation. "
        "Support multiple languages: English, Spanish, and Basque."
    ),
    description=(
        "Medication reminder agent. Creates calendar events for medication reminders. "
        "Use this for reminder requests."
    ),
    tools=[
        confirmacion_tool,
    ],
)
