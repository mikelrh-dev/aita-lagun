"""FastMCP server for Google Calendar integration.

Exposes a single tool ``crear_evento_calendar`` that creates calendar events
using the Google Calendar API via a service account.

Security and design decisions:
- Service account auth is used INSTEAD of OAuth 2.0 because:
  a) No interactive browser flow required — works headlessly in CLI/container
  b) The calendar is shared with the service account email by the owner
  c) Suitable for demo/personal use; production multi-user would need OAuth
- The credential string can be either a file path or inline JSON.
  This flexibility supports both local dev (file path) and Cloud Run
  (environment variable with inline JSON) deployment scenarios.
- The ``json`` import is used here for parsing inline credential JSON.
  This is a standard library dependency — no extra package needed.
"""

import json
import logging
import os
import re
from datetime import date as date_mod, datetime
from typing import Optional

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calendar Server")

logger = logging.getLogger(__name__)

_VALID_DAY_CODES = {"MO", "TU", "WE", "TH", "FR", "SA", "SU"}


# OAuth scope for read/write calendar access via service account.
# This is the minimum scope needed to create events on a shared calendar.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def _get_calendar_service():
    """Build and return an authenticated Google Calendar service object.

    Resolves credentials from the ``GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON``
    environment variable. Supports two formats:
    - File path ending in ``.json``: loads from local file
    - Inline JSON string: parsed directly

    Why two formats:
    Local development typically uses a file path, while container/Cloud Run
    deployments pass the full JSON as an environment variable for simplicity.

    Returns:
        googleapiclient.discovery.Resource: Authenticated Calendar API service.

    Raises:
        ValueError: If the environment variable is not set or empty.
    """
    creds_json = os.environ.get("GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON", "")
    if not creds_json:
        raise ValueError(
            "GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON env var not set. "
            "Provide a path to a JSON file or the JSON string itself."
        )
    # Detect file path vs inline JSON by checking the trailing extension.
    # This is a heuristic: a JSON string ending in ".json" would be
    # misidentified, but in practice credential JSON content never ends with
    # ".json" as a filename extension would.
    if creds_json.endswith(".json"):
        creds = Credentials.from_service_account_file(creds_json, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
    return build("calendar", "v3", credentials=creds)


def _parse_time(time_str: str) -> str:
    """Parse a time string into ``HH:MM`` format.

    Accepts a variety of common time formats:

    - ``"08:00"`` — already in HH:MM
    - ``"8"`` or ``"14"`` — bare hour, assumes ``:00``
    - ``"8am"``, ``"8 pm"``, ``"8:30am"``, ``"8:00 PM"`` — AM/PM notation

    Returns:
        Normalized ``HH:MM`` string.

    Raises:
        ValueError: If *time_str* cannot be parsed.
    """
    time_str = time_str.strip()

    # Already in HH:MM format
    if re.match(r"^\d{1,2}:\d{2}$", time_str):
        return time_str

    # Bare hour without minutes (e.g., "8" or "14")
    if re.match(r"^\d{1,2}$", time_str):
        return f"{int(time_str):02d}:00"

    # AM/PM formats: "8am", "8 pm", "8:30AM", "8:00 PM"
    m = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(am|pm)$", time_str, re.IGNORECASE)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2)) if m.group(2) else 0
        suffix = m.group(3).lower()
        if suffix == "pm" and hour != 12:
            hour += 12
        elif suffix == "am" and hour == 12:
            hour = 0
        return f"{hour:02d}:{minute:02d}"

    raise ValueError(
        f"Could not parse time: '{time_str}'. "
        "Use formats like '08:00', '8am', '8:30 pm', or '14'."
    )


def _build_rrule(recurrence: Optional[str]) -> Optional[list[str]]:
    """Build a Google Calendar ``recurrence`` list from a simplified recurrence string.

    Input → Output mapping:

    ============================  ========================================
    Input                          Output
    ============================  ========================================
    ``None``                       ``None``
    ``""``                         ``None``
    ``"daily"``                    ``["RRULE:FREQ=DAILY"]``
    ``"weekdays"``                 ``["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"]``
    ``"weekly;MO"``                ``["RRULE:FREQ=WEEKLY;BYDAY=MO"]``
    ``"weekly;MO,WE,FR"``          ``["RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"]``
    ``"WEEKLY;mo"`` (mixed case)   ``["RRULE:FREQ=WEEKLY;BYDAY=MO"]`` (normalized)
    ============================  ========================================

    Unsupported or invalid inputs raise ``ValueError``.

    Args:
        recurrence: A simplified recurrence string.

    Returns:
        A list containing one RFC 5545 RRULE string, or ``None``.

    Raises:
        ValueError: If the input is not a supported recurrence pattern.
    """
    if recurrence is None or recurrence == "":
        return None

    normalized = recurrence.strip().lower()

    # --- "weekdays" shorthand → weekly with full weekday set ---
    if normalized == "weekdays":
        result = ["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"]
        logger.debug("Built RRULE for 'weekdays': %s", result[0])
        return result

    # --- "daily" → FREQ=DAILY ---
    if normalized == "daily":
        result = ["RRULE:FREQ=DAILY"]
        logger.debug("Built RRULE for 'daily': %s", result[0])
        return result

    # --- "weekly;DAY1,DAY2,..." → FREQ=WEEKLY;BYDAY=... ---
    # Bare "weekly" (without semicolon) is invalid
    if normalized == "weekly":
        raise ValueError(
            f"Invalid weekly recurrence: '{recurrence}'. "
            "Use format 'weekly;MO' or 'weekly;MO,WE,FR'."
        )
    if normalized.startswith("weekly;"):
        segments = normalized.split(";", maxsplit=1)
        if len(segments) != 2 or not segments[1].strip():
            raise ValueError(
                f"Invalid weekly recurrence: '{recurrence}'. "
                "Use format 'weekly;MO' or 'weekly;MO,WE,FR'."
            )

        day_codes_raw = segments[1].strip().upper().split(",")
        day_codes = [d.strip() for d in day_codes_raw if d.strip()]

        if not day_codes:
            raise ValueError(
                f"Invalid weekly recurrence: '{recurrence}'. "
                "At least one day code is required after 'weekly;'."
            )

        invalid_days = [d for d in day_codes if d not in _VALID_DAY_CODES]
        if invalid_days:
            raise ValueError(
                f"Invalid day code(s) in recurrence: '{', '.join(invalid_days)}'. "
                f"Valid codes: {', '.join(sorted(_VALID_DAY_CODES))}."
            )

        result = [f"RRULE:FREQ=WEEKLY;BYDAY={','.join(day_codes)}"]
        logger.debug("Built RRULE for '%s': %s", recurrence, result[0])
        return result

    # --- Unsupported pattern ---
    raise ValueError(
        f"Unsupported recurrence pattern: '{recurrence}'. "
        "Supported patterns: 'daily', 'weekly;DAY', 'weekdays'."
    )


@mcp.tool()
def crear_evento_calendar(
    medication: str,
    time: str,
    date: Optional[str] = None,
    recurrence: Optional[str] = None,
) -> dict:
    """Create a calendar event for a medication reminder.

    Args:
        medication: Name of the medication (e.g., 'Sintrom')
        time: Time in HH:MM, 12h, or bare-hour format (e.g., '08:00', '8am', '14')
        date: Date in YYYY-MM-DD format (default: today)
        recurrence: Optional recurrence pattern ('daily', 'weekly;MO', 'weekdays', etc.)

    Returns:
        dict with status and event details
    """
    event_date = date if date is not None else date_mod.today().isoformat()

    try:
        parsed_time = _parse_time(time)
    except ValueError as e:
        return {"status": "error", "error": str(e)}

    start_dt = datetime.fromisoformat(f"{event_date}T{parsed_time}:00")
    end_dt = start_dt.replace(hour=start_dt.hour, minute=start_dt.minute + 15)

    event_body = {
        "summary": f"Recordatorio: {medication}",
        "description": f"Medication reminder for {medication}",
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "Europe/Madrid",
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "Europe/Madrid",
        },
    }

    # NEW: inject recurrence if present
    try:
        rrule = _build_rrule(recurrence)
        if rrule is not None:
            event_body["recurrence"] = rrule
    except ValueError as e:
        return {"status": "error", "error": str(e)}

    service = _get_calendar_service()
    event = service.events().insert(calendarId=os.environ.get("GOOGLE_CALENDAR_ID", "primary"), body=event_body).execute()

    return {
        "status": "created",
        "event_id": event.get("id"),
        "html_link": event.get("htmlLink", ""),
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
