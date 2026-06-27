---
name: create_reminder
description: Creates a medication reminder with human confirmation via Google Calendar
version: 1.0
---

# SKILL: create_reminder

## Purpose

Creates a Google Calendar event for a medication reminder after obtaining
explicit human confirmation. This is the core write operation in the
Aita-Lagun assistant.

## Input Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `medication` | `str` | ✅ Yes | Name of the medication (e.g., "Sintrom", "Paracetamol") |
| `time` | `str` | ✅ Yes | Time in HH:MM format (e.g., "08:00", "14:30") |
| `date` | `str` | ❌ No | Date in YYYY-MM-DD format (defaults to today) |

## Output Format

**Success:**
```json
{
  "status": "created",
  "event_id": "abc123def456",
  "html_link": "https://www.google.com/calendar/event?eid=..."
}
```

**Cancelled (user declines confirmation):**
The event is not created — the FunctionTool prevents execution before
the MCP server is called. ADK returns a cancellation message.

## Security Notes

- **⚠️ Human confirmation required**: This tool is wrapped with
  `FunctionTool(require_confirmation=True)`. The ADK framework pauses
  execution and presents the details (medication name, time, date) to
  the user before the calendar event is created. No event is written
  without explicit approval.
- **No PHI storage**: Medication names and times are passed transiently
  to the Google Calendar API. The system does not store, log, or retain
  any personal health information.
- **Public PDFs only**: The health information subsystem reads only
  from official public Osakidetza PDFs. No personal or restricted data
  is accessed.

## Usage Example

**User:** "Remind me to take Sintrom at 8am"

**Agent (after LLM routing to recordatorio):**
"I'll create a reminder for Sintrom at 08:00 today. Shall I proceed?"

**User confirms:** "Yes"

**FunctionTool confirmation prompt (ADK built-in):**
```
Tool: crear_evento_calendar
Parameters:
  medication: Sintrom
  time: 08:00
  date: 2026-06-25
Do you want to proceed? (yes/no):
```

**User:** "yes"

**Result:** Calendar event created. Agent responds with confirmation
and a link to the event.

## Implementation Details

**Call chain:**
```
User → Root Agent → recordatorio → FunctionTool (confirm?) → crear_evento_calendar
                                                                    ↓
                                                            Calendar MCP Server
                                                                    ↓
                                                            Google Calendar API
```

- The `FunctionTool` lives in `agents/orchestrator.py`
- The actual calendar logic is in `agents/recordatorio_agent.py`
- The MCP server is `mcp_servers/calendar_mcp.py`
