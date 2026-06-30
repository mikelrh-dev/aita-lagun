# Design: Optional Recurrence for Medication Reminders

**Change:** `recurrencia-recordatorios`
**Status:** Draft
**Date:** 2026-06-30
**Designer:** SDD Design Executor

---

## 1. Architecture Overview

### 1.1 Data Flow

```
User says "remember every day at 8"
    │
    ▼
recordatorio Agent (ADK, agents/orchestrator.py)
    │  — instruction prompts LLM to map "every day" → recurrence="daily"
    │  — LLM calls crear_evento_calendar(medication="Sintrom", time="08:00", recurrence="daily")
    ▼
crear_evento_calendar tool (mcp_servers/calendar_mcp.py)
    │  — validates recurrence via _build_rrule("daily")
    │  — returns ["RRULE:FREQ=DAILY"]
    │  — injects into event_body["recurrence"]
    ▼
Google Calendar API v3
    │  — native RRULE support, no extra deps
    ▼
Event created with recurrence series
```

### 1.2 Layer Responsibilities

| Layer | File | Responsibility |
|-------|------|---------------|
| **Agent prompt** | `agents/orchestrator.py` | Cross-language recurrence mapping, proactive asking, graceful decline |
| **LLM reasoning** | (runtime) | Maps natural language → `recurrence` parameter value |
| **Tool signature** | `mcp_servers/calendar_mcp.py` | Accepts `recurrence: Optional[str]` parameter |
| **RRULE builder** | `mcp_servers/calendar_mcp.py` | Validates input, builds RFC 5545 RRULE string |
| **Google Calendar API** | (external) | Native `recurrence` field — no extra packages needed |

### 1.3 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Normalize inside `_build_rrule`, not the prompt | Centralized validation — one place to fix edge cases, testable pure function |
| `_build_rrule` returns `None` for no-recurrence | Clean sentinel — event body stays backward-compatible when `None` |
| Validation raises `ValueError`, tool catches it | Consistent with existing `_parse_time` error pattern |
| `weekdays` → `weekly;MO,TU,WE,TH,FR` expansion | Separate normalization from the agent prompt — the prompt uses the expanded form, the tool handles shortcuts |
| No `COUNT`/`UNTIL` in V1 | Per NFR-6, V1 produces indefinite recurrence series. V2 can add end-date support |

---

## 2. Module-by-Module Changes

### 2.1 `mcp_servers/calendar_mcp.py`

#### 2.1.1 New Function: `_build_rrule`

```python
import logging

logger = logging.getLogger(__name__)

_VALID_DAY_CODES = {"MO", "TU", "WE", "TH", "FR", "SA", "SU"}

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
    if normalized.startswith("weekly;") or normalized.startswith("weekly;"):
        # Normalize: split on ";", ensure prefix is "weekly"
        # (startswith already guarantees this for valid input)
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
```

**Validation logic (priority order):**

1. `None` or `""` → `None` (backward compatible, no `recurrence` field)
2. `"daily"` → `["RRULE:FREQ=DAILY"]`
3. `"weekdays"` → `["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"]`
4. `"weekly;DAY[,DAY...]"` → validate each day ∈ `{MO,TU,WE,TH,FR,SA,SU}`, then `["RRULE:FREQ=WEEKLY;BYDAY=..."]`
5. Everything else → `ValueError`

#### 2.1.2 Updated Tool Signature

```python
@mcp.tool()
def crear_evento_calendar(
    medication: str,
    time: str,
    date: Optional[str] = None,
    recurrence: Optional[str] = None,  # NEW
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
    # ... existing time parsing stays identical ...

    event_body = {
        # ... existing fields stay identical ...
    }

    # NEW: inject recurrence if present
    try:
        rrule = _build_rrule(recurrence)
        if rrule is not None:
            event_body["recurrence"] = rrule
    except ValueError as e:
        return {"status": "error", "error": str(e)}

    # ... existing API call stays identical ...
```

#### 2.1.3 Event Body Construction (changes in context)

```python
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

    # NEW: Add recurrence field when applicable
    try:
        rrule = _build_rrule(recurrence)
        if rrule is not None:
            event_body["recurrence"] = rrule
    except ValueError as e:
        return {"status": "error", "error": str(e)}
```

#### 2.1.4 Complete Modified Function

The existing logic (`_parse_time`, date defaults, event_body build, service call, return) remains **100% unchanged** except for:
- The new `recurrence` parameter in the function signature
- The `_build_rrule` call + injection block before the service call
- The new `logging` import and `logger` at module level
- The new `_VALID_DAY_CODES` constant
- The `_build_rrule` function definition

#### 2.1.5 Logging

```python
import logging
logger = logging.getLogger(__name__)
```

Every `_build_rrule` return path logs the generated RRULE at `DEBUG` level.

---

### 2.2 `agents/orchestrator.py` — Agent Instruction Update

Replace the existing `instruction` tuple with extended version:

```python
recordatorio = Agent(
    name="recordatorio",
    model=os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
    instruction=(
        "You are a medication reminder assistant. "
        "When the user asks to create a reminder, use the crear_evento_calendar tool. "
        "IMPORTANT: You MUST ask the user to confirm the event details BEFORE calling "
        "the tool. Wait for their explicit confirmation. "
        "Support multiple languages: English, Spanish, and Basque."
        "\n\n"
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
        "If the user says 'just today', 'solo hoy', 'solo gaur', or similar,\n"
        "do NOT pass recurrence — create a single event.\n"
        "\n"
        "If the user asks for patterns like 'every 2 days', 'every month',\n"
        "'cada 2 días', 'cada mes', 'bi egunetik behin', 'hilabetero',\n"
        "politely explain that only daily and weekly are supported for now\n"
        "and ask if either option works for them."
    ),
    # ... rest unchanged ...
)
```

#### 2.2.1 Change Summary

| Aspect | Current | After |
|--------|---------|-------|
| `instruction` length | ~4 sentences | ~30 lines (multi-section) |
| Recurrence knowledge | None | Full cross-language mapping |
| Proactive ask | None | Required when recurrence unspecified |
| Graceful decline | None | Required for unsupported patterns |
| `tools` | `[confirmacion_tool]` | Unchanged |
| `name`, `model`, `description` | Unchanged | Unchanged |

---

## 3. Error Handling Strategy

### 3.1 Error Categories

| Category | Detection Point | Response |
|----------|----------------|---------|
| Unsupported pattern (`"monthly"`, `"every 2 days"`) | `_build_rrule` → `ValueError` | `{"status": "error", "error": "Unsupported recurrence pattern..."}` |
| Invalid weekly format (`"weekly"` no days, `"weekly;"` empty) | `_build_rrule` → `ValueError` | `{"status": "error", "error": "Invalid weekly recurrence..."}` |
| Invalid day codes (`"weekly;XX"`) | `_build_rrule` → `ValueError` | `{"status": "error", "error": "Invalid day code(s)..."}` |
| Empty string | `_build_rrule` → `None` | No `recurrence` field (treated as single event) |
| Case variation (`"WEEKLY;MO"`, `"Weekly;mo"`) | Normalized in `_build_rrule` | Accepted silently |

### 3.2 Error Return Pattern

All errors follow the existing convention from `_parse_time`:

```python
try:
    rrule = _build_rrule(recurrence)
except ValueError as e:
    return {"status": "error", "error": str(e)}
```

This ensures the tool always returns a dict (never raises through the MCP boundary) and the LLM receives structured error information it can relay to the user.

### 3.3 API Call Guard

The Google Calendar API is ONLY called when `_build_rrule` succeeds (returns `None` or a valid RRULE list). Validation errors short-circuit before `service.events().insert(...)`.

---

## 4. Test Strategy

### 4.1 Test Pyramid Placement

```
        ╱╲
       ╱  ╲         E2E / Eval (~5%)
      ╱    ╲        agents-cli eval for agent behavior
     ╱──────╲
    ╱        ╲      Integration Tests (~15%)
   ╱          ╲     crear_evento_calendar with mocked API
  ╱────────────╲
 ╱              ╲   Unit Tests (~80%)
╱────────────────╲  _build_rrule — pure, no mocking needed
```

### 4.2 Unit Tests for `_build_rrule` (Pure Function — No Mocks)

These test the mapping + validation logic in complete isolation. No mocking, no I/O, milliseconds each.

| Test Name | Input | Expected |
|-----------|-------|----------|
| `test_rrule_none` | `None` | `None` |
| `test_rrule_empty_string` | `""` | `None` |
| `test_rrule_daily` | `"daily"` | `["RRULE:FREQ=DAILY"]` |
| `test_rrule_weekdays_shorthand` | `"weekdays"` | `["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"]` |
| `test_rrule_weekly_single_day` | `"weekly;MO"` | `["RRULE:FREQ=WEEKLY;BYDAY=MO"]` |
| `test_rrule_weekly_multiple_days` | `"weekly;MO,WE,FR"` | `["RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"]` |
| `test_rrule_weekly_all_days` | `"weekly;MO,TU,WE,TH,FR,SA,SU"` | `["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR,SA,SU"]` |
| `test_rrule_unsupported_raises` | `"monthly"` | `ValueError` |
| `test_rrule_weekly_no_days_raises` | `"weekly"` | `ValueError` |
| `test_rrule_weekly_empty_days_raises` | `"weekly;"` | `ValueError` |
| `test_rrule_invalid_day_code_raises` | `"weekly;XX"` | `ValueError` |
| `test_rrule_case_normalization` | `"WEEKLY;MO"` | `["RRULE:FREQ=WEEKLY;BYDAY=MO"]` |
| `test_rrule_mixed_case_days` | `"weekly;mo,we,fr"` | `["RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"]` |

### 4.3 Integration Tests for `crear_evento_calendar` (Mocked API)

These test the full tool with mocked `_get_calendar_service`, following the existing pattern.

| Test Name | Input | Expected |
|-----------|-------|----------|
| `test_daily_recurrence` | `recurrence="daily"` | `recurrence: ["RRULE:FREQ=DAILY"]` in API body |
| `test_weekly_recurrence_single_day` | `recurrence="weekly;MO"` | `recurrence: ["RRULE:FREQ=WEEKLY;BYDAY=MO"]` in body |
| `test_weekly_recurrence_multiple_days` | `recurrence="weekly;MO,WE,FR"` | `recurrence: ["RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"]` in body |
| `test_no_recurrence_default` | no `recurrence` arg | No `recurrence` field in body |
| `test_no_recurrence_empty_string` | `recurrence=""` | No `recurrence` field in body |
| `test_unsupported_recurrence_returns_error` | `recurrence="monthly"` | `{"status": "error", "error": "..."}`, API NOT called |
| `test_weekly_without_days_returns_error` | `recurrence="weekly"` | Error dict, API NOT called |
| `test_weekdays_shorthand` | `recurrence="weekdays"` | `recurrence: ["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"]` in body |
| `test_recurrence_with_date` | `recurrence="daily"`, `date="2026-12-25"` | Both RRULE and date in body |

### 4.4 Backward Compatibility Verification

All 12 existing tests (9 in `TestParseTime`, 3 in `TestCalendarMCP`) must pass without modification. This is verified via:

```bash
pytest tests/unit/test_calendar_mcp.py -v
```

| Existing Test | Impact | Status |
|---------------|--------|--------|
| `test_crear_evento_basic` | No `recurrence` → event body unchanged | Must still pass |
| `test_crear_evento_with_date` | No `recurrence` → event body unchanged | Must still pass |
| `test_crear_evento_default_date_is_today` | No `recurrence` → event body unchanged | Must still pass |
| `TestParseTime` (all 9) | Pure function, untouched | Must still pass |
| `test_invalid_time_in_crear_evento_returns_error` | No `recurrence` → error path unchanged | Must still pass |

### 4.5 Agent Tests (Eval — Not Pytest)

The agent's recurrence behavior (proactive asking, cross-language mapping, graceful decline) is **non-deterministic LLM output** and MUST NOT be tested with pytest assertions on response text. Instead:

- **Validated via** `agents-cli eval` with LLM-as-judge criteria
- A MAY-be-added test: verify the `recordatorio` agent's instruction string contains expected recurrence keywords (string content check, not LLM behavior)

### 4.6 DAMP Test Example

```python
# test_rrule_builder.py

import pytest
from mcp_servers.calendar_mcp import _build_rrule


class TestBuildRrule:
    """Pure function tests for _build_rrule — no mocking needed."""

    def test_none_returns_none(self):
        """None input returns None (no recurrence)."""
        assert _build_rrule(None) is None

    def test_empty_string_returns_none(self):
        """Empty string returns None (backward compatible)."""
        assert _build_rrule("") is None

    def test_daily(self):
        """'daily' maps to FREQ=DAILY."""
        assert _build_rrule("daily") == ["RRULE:FREQ=DAILY"]

    def test_weekdays_shorthand(self):
        """'weekdays' maps to all weekdays."""
        assert _build_rrule("weekdays") == [
            "RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"
        ]

    def test_weekly_single_day(self):
        """'weekly;MO' maps to FREQ=WEEKLY;BYDAY=MO."""
        assert _build_rrule("weekly;MO") == [
            "RRULE:FREQ=WEEKLY;BYDAY=MO"
        ]

    def test_weekly_multiple_days(self):
        """'weekly;MO,WE,FR' maps correctly."""
        assert _build_rrule("weekly;MO,WE,FR") == [
            "RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"
        ]

    def test_unsupported_raises_valueerror(self):
        """'monthly' raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported recurrence"):
            _build_rrule("monthly")

    def test_weekly_no_days_raises(self):
        """'weekly' without days raises ValueError."""
        with pytest.raises(ValueError, match="Invalid weekly"):
            _build_rrule("weekly")

    def test_invalid_day_code_raises(self):
        """'weekly;XX' raises ValueError with invalid day message."""
        with pytest.raises(ValueError, match="Invalid day code"):
            _build_rrule("weekly;XX")
```

---

## 5. Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| `logging` | stdlib | Already available, add import |
| `googleapiclient` | existing | Already handles RRULE strings |
| Google Calendar API v3 | external | Native `recurrence` field support |
| New Python packages | — | **None required** |

---

## 6. Backward Compatibility Guarantee

The design ensures that **every existing caller and test** works identically:

1. **`recurrence` defaults to `None`** → no code change required for existing callers
2. **`_build_rrule(None)` returns `None`** → `if rrule is not None` guard ensures no `recurrence` field in event body
3. **`_build_rrule("")` returns `None`** → same guard applies
4. **Existing tests don't pass `recurrence`** → function behavior is identical to current code

---

## 7. Implementation Order

| Step | File | Description | Dependencies |
|------|------|-------------|--------------|
| 1 | `mcp_servers/calendar_mcp.py` | Add `_build_rrule` function + imports | None |
| 2 | `mcp_servers/calendar_mcp.py` | Update `crear_evento_calendar` signature + body | Step 1 |
| 3 | `tests/unit/test_calendar_mcp.py` | Add `TestBuildRrule` class (unit tests) | Step 1 |
| 4 | `tests/unit/test_calendar_mcp.py` | Add integration tests for recurrence in tool | Step 2 |
| 5 | `agents/orchestrator.py` | Update `recordatorio` instruction | None (independent) |
| 6 | Verify | Run `pytest tests/unit/test_calendar_mcp.py -v` | Steps 1–5 |

Steps 1–4 are interdependent (function → tool → tests). Step 5 (agent instruction) is independent and can be done in parallel.

---

## 8. Open Questions

| Question | Resolution (in design) |
|----------|------------------------|
| Should `_build_rrule` be in a separate module? | No — it's small, tightly coupled to the tool, and keeping it in `calendar_mcp.py` avoids import indirection. If it grows beyond 5 patterns, extract to `mcp_servers/_rrule.py`. |
| Should the `weekdays` shorthand be expanded in the prompt or in code? | **In code** — the prompt tells the LLM to use `weekly;MO,TU,WE,TH,FR`, and `_build_rrule` accepts the `weekdays` shortcut as a convenience. This keeps the prompt format canonical. |
| Validation before or after time parsing? | Before (time parsing first, then recurrence). Time errors are more common and should fail fast. |
| Log level? | `DEBUG` — generated RRULEs are low-cardinality strings, useful for debugging but too noisy for `INFO`. |
