# Spec: Optional Recurrence for Medication Reminders

**Change:** `recurrencia-recordatorios`
**Status:** Draft
**Date:** 2026-06-30

---

## 1. Functional Requirements

### FR-1: Daily Recurrence

The `crear_evento_calendar` tool SHALL accept a `recurrence` parameter value of `"daily"` and generate a Google Calendar event with `RRULE:FREQ=DAILY` in the `recurrence` field of the event body.

### FR-2: Weekly Recurrence with Specific Days

The `crear_evento_calendar` tool SHALL accept a `recurrence` parameter value in the format `"weekly;DAY1,DAY2,..."` where each `DAY` is a two-letter RFC 5545 day abbreviation (`MO`, `TU`, `WE`, `TH`, `FR`, `SA`, `SU`). It SHALL generate a Google Calendar event with `RRULE:FREQ=WEEKLY;BYDAY=DAY1,DAY2,...` in the `recurrence` field.

### FR-3: Weekday Recurrence Shorthand

The tool SHALL accept `"weekly;MO,TU,WE,TH,FR"` (and equivalent variant `"weekdays"`) and generate `RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR`. Agent instructions SHALL map both `"weekdays"` and `"weekly;MO,TU,WE,TH,FR"` to the same RRULE.

### FR-4: No Recurrence (Backward Compatibility)

When `recurrence` is `None` (default) or an empty string, the tool SHALL produce the exact same event body as the current implementation — no `recurrence` field SHALL be present in the event body.

### FR-5: Agent Proactive Ask About Recurrence

When the user provides medication + time WITHOUT specifying recurrence, the recordatorio agent SHOULD ask the user if they want a single event or a recurring one. The question SHALL be in the detected user language.

### FR-6: Recurrence Only When User Specifies

If the user explicitly rejects recurrence or confirms "just for today", the agent SHALL NOT add recurrence and SHALL create a single event.

### FR-7: Cross-Language Recurrence Mapping

The agent SHALL recognize recurrence phrases in English, Spanish, and Basque and map them to the correct `recurrence` parameter value:

| Language | "every day" Equivalent | `recurrence` value |
|----------|----------------------|--------------------|
| English  | "every day", "daily" | `"daily"` |
| Spanish  | "todos los días", "cada día", "diario" | `"daily"` |
| Basque   | "egunero", "egunero." | `"daily"` |

| Language | "every Monday" Equivalent | `recurrence` value |
|----------|--------------------------|--------------------|
| English  | "every Monday", "on Mondays" | `"weekly;MO"` |
| Spanish  | "los lunes", "cada lunes" | `"weekly;MO"` |
| Basque   | "astelehenero", "astelehenetan" | `"weekly;MO"` |

| Language | "every weekday" Equivalent | `recurrence` value |
|----------|---------------------------|--------------------|
| English  | "every weekday", "weekdays", "Monday to Friday" | `"weekly;MO,TU,WE,TH,FR"` |
| Spanish  | "entre semana", "días laborables", "lunes a viernes" | `"weekly;MO,TU,WE,TH,FR"` |
| Basque   | "astean zehar", "astegunero" | `"weekly;MO,TU,WE,TH,FR"` |

### FR-8: Graceful Decline for Unsupported Patterns

When the user specifies a recurrence pattern NOT supported in V1 (e.g., "every 2 days", "every month", "every other day"), the agent SHALL respond with a message in the detected language explaining that only daily and weekly recurrence are currently supported, and asking if either of those works.

---

## 2. Non-Functional Requirements

### NFR-1: Backward Compatibility

All existing single-event behavior MUST remain unchanged. Any code path where `recurrence` is `None` or absent MUST produce identical event bodies to the current implementation.

### NFR-2: Validation

The tool SHALL validate the `recurrence` parameter before sending to the Google Calendar API. Invalid or unrecognized values SHALL return an error dict (`{"status": "error", "error": "..."}`) rather than propagating a malformed RRULE to the API.

### NFR-3: Error Handling

If `recurrence` is provided but in an invalid format (e.g., `"weekly"` without days, `"monthly"`, empty string treated as None), the tool SHALL return a structured error response and SHALL NOT call the Google Calendar API.

### NFR-4: Logging

The MCP server SHALL log the generated RRULE string at DEBUG level for auditability.

### NFR-5: Event Duration

Recurring events SHALL use the same duration as single events (15 minutes after start time). The duration applies to every occurrence in the recurrence series.

### NFR-6: No End Date

Recurring events in V1 SHALL NOT specify `UNTIL` or `COUNT` in the RRULE. Events continue indefinitely. A V2 enhancement MAY add end-date support.

---

## 3. Acceptance Criteria

- [ ] **AC-1**: `crear_evento_calendar("Sintrom", "08:00", recurrence="daily")` creates an event with `recurrence: ["RRULE:FREQ=DAILY"]` in the API call body.
- [ ] **AC-2**: `crear_evento_calendar("Sintrom", "08:00", recurrence="weekly;MO")` creates an event with `recurrence: ["RRULE:FREQ=WEEKLY;BYDAY=MO"]`.
- [ ] **AC-3**: `crear_evento_calendar("Sintrom", "08:00", recurrence="weekly;MO,WE,FR")` creates an event with `recurrence: ["RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"]`.
- [ ] **AC-4**: `crear_evento_calendar("Sintrom", "08:00")` (no recurrence) creates an event body with NO `recurrence` field.
- [ ] **AC-5**: `crear_evento_calendar("Sintrom", "08:00", recurrence="")` (empty string) behaves identically to AC-4 — no `recurrence` field.
- [ ] **AC-6**: `crear_evento_calendar("Test", "08:00", recurrence="monthly")` returns `{"status": "error", "error": "..."}` — unsupported pattern.
- [ ] **AC-7**: `crear_evento_calendar("Test", "08:00", recurrence="weekly")` (no day specifiers) returns error — invalid format.
- [ ] **AC-8**: All existing tests (`tests/unit/test_calendar_mcp.py`, `tests/unit/test_agents.py`) pass without modification.
- [ ] **AC-9**: The recordatorio agent's instruction mentions recurrence support and asks about it proactively.
- [ ] **AC-10**: Agent recognizes "todos los días" (es) and "egunero" (eu) and maps to `recurrence="daily"`.

---

## 4. Scenarios

### Scenario 1: Daily Recurrence — User Specifies "every day"

```
Given the crear_evento_calendar tool
When called with medication="Sintrom", time="08:00", recurrence="daily"
Then the event body contains "recurrence": ["RRULE:FREQ=DAILY"]
And the event has summary "Recordatorio: Sintrom"
And the event duration is 15 minutes
And the event starts at 08:00 on today's date
```

### Scenario 2: Weekly Recurrence — Specific Day

```
Given the crear_evento_calendar tool
When called with medication="Sintrom", time="08:00", recurrence="weekly;MO"
Then the event body contains "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=MO"]
```

### Scenario 3: Weekly Recurrence — Multiple Days

```
Given the crear_evento_calendar tool
When called with medication="Sintrom", time="08:00", recurrence="weekly;MO,WE,FR"
Then the event body contains "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"]
```

### Scenario 4: No Recurrence — Default Behavior

```
Given the crear_evento_calendar tool
When called with medication="Sintrom", time="08:00" (no recurrence argument)
Then the event body contains NO "recurrence" field
And the event is a single occurrence
```

### Scenario 5: No Recurrence — Empty String

```
Given the crear_evento_calendar tool
When called with medication="Sintrom", time="08:00", recurrence=""
Then the event body contains NO "recurrence" field
And the event is a single occurrence
```

### Scenario 6: Unsupported Recurrence Pattern

```
Given the crear_evento_calendar tool
When called with medication="Test", time="08:00", recurrence="monthly"
Then the return value is {"status": "error", "error": "..."}
And the Google Calendar API is NOT called
```

### Scenario 7: Invalid Weekly Format (No Days)

```
Given the crear_evento_calendar tool
When called with medication="Test", time="08:00", recurrence="weekly"
Then the return value is {"status": "error", "error": "..."}
And the Google Calendar API is NOT called
```

### Scenario 8: Backward Compatibility — Existing Tests Pass

```
Given the existing test suite in tests/unit/test_calendar_mcp.py
When all tests are run
Then every existing test passes without any modification
```

### Scenario 9: Agent Asks About Recurrence

```
Given a user says "Recuérdame tomar Sintrom a las 8"
And the user has NOT specified recurrence
When the recordatorio agent processes the request
Then the agent asks "¿Quieres que te recuerde solo hoy o todos los días?"
```

### Scenario 10: User Explicitly Declines Recurrence

```
Given a user says "Recuérdame tomar Sintrom a las 8"
And the agent asks about recurrence
When the user responds "Solo hoy" or "just today"
Then the agent creates a single event with no recurrence
```

### Scenario 11: Spanish Daily Mapping

```
Given a user says "Recuérdame tomar Sintrom a las 8 todos los días"
When the recordatorio agent processes the request
Then the agent calls crear_evento_calendar with recurrence="daily"
```

### Scenario 12: Basque Weekly Mapping

```
Given a user says "Gogoratu Sintrom 8etan astelehenero"
When the recordatorio agent processes the request
Then the agent calls crear_evento_calendar with recurrence="weekly;MO"
```

### Scenario 13: Unsupported Pattern — Graceful Decline

```
Given a user says "Recuérdame tomar Sintrom a las 8 cada 2 días"
When the recordatorio agent processes the request
Then the agent responds that only daily and weekly recurrence are supported
And asks if either option would work
```

### Scenario 14: Recurrence with Date

```
Given the crear_evento_calendar tool
When called with medication="Sintrom", time="08:00", date="2026-12-25", recurrence="daily"
Then the event body contains "recurrence": ["RRULE:FREQ=DAILY"]
And the start dateTime contains "2026-12-25"
```

---

## 5. Technical Specification

### 5.1 `mcp_servers/calendar_mcp.py` — Tool Signature Change

Add `recurrence` parameter:

```python
@mcp.tool()
def crear_evento_calendar(
    medication: str,
    time: str,
    date: Optional[str] = None,
    recurrence: Optional[str] = None,  # NEW
) -> dict:
```

### 5.2 RRULE Mapping Logic

Introduce a `_build_rrule(recurrence: Optional[str]) -> Optional[list[str]]` helper:

| Input | Output | Notes |
|-------|--------|-------|
| `None` | `None` | No recurrence field added to event body |
| `""` | `None` | Empty string treated as no recurrence |
| `"daily"` | `["RRULE:FREQ=DAILY"]` | Standard daily recurrence |
| `"weekly;MO"` | `["RRULE:FREQ=WEEKLY;BYDAY=MO"]` | Weekly on specific day(s) |
| `"weekly;MO,WE,FR"` | `["RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"]` | Multiple days |
| `"weekdays"` | `["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"]` | Weekday shorthand |
| `"monthly"` | raises `ValueError` | Unsupported |
| `"weekly"` | raises `ValueError` | Missing day specifiers |

### 5.3 Event Body Change

When `recurrence` is provided and valid, add to `event_body`:

```python
if rrule := _build_rrule(recurrence):
    event_body["recurrence"] = rrule
```

### 5.4 `agents/orchestrator.py` — Instruction Update

Append to the `recordatorio` agent's `instruction`:

```python
(
    "You support optional recurrence for medication reminders. "
    "The crear_evento_calendar tool accepts a 'recurrence' parameter. "
    "Use 'daily' for every day, 'weekly;MO' for every Monday, "
    "'weekly;MO,TU,WE,TH,FR' for weekdays (Monday to Friday). "
    "SUPPORTED LANGUAGES: "
    "EN: 'every day' → daily, 'every Monday' → weekly;MO, 'weekdays' → weekly;MO,TU,WE,TH,FR. "
    "ES: 'todos los días' → daily, 'los lunes' → weekly;MO, 'entre semana' → weekly;MO,TU,WE,TH,FR. "
    "EU: 'egunero' → daily, 'astelehenero' → weekly;MO, 'astegunero' → weekly;MO,TU,WE,TH,FR. "
    "IMPORTANT: If the user specifies medication and time WITHOUT mentioning "
    "recurrence, ASK them if they want a single event or a recurring one. "
    "If the user asks for unsupported patterns like 'every 2 days' or 'every month', "
    "politely explain that only daily and weekly are supported and ask if either works. "
    "If the user confirms 'just today' or declines recurrence, create a single event "
    "with no recurrence."
)
```

### 5.5 Validation Rules

1. If `recurrence` is `None` or `""`: return `None` (no RRULE, backward compatible)
2. If `recurrence == "daily"`: return `["RRULE:FREQ=DAILY"]`
3. If `recurrence == "weekdays"`: return `["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"]`
4. If `recurrence` starts with `"weekly;"` and has at least one day after `;`: validate that each day is one of `MO,TU,WE,TH,FR,SA,SU`; if valid, return `["RRULE:FREQ=WEEKLY;BYDAY=..."]`
5. Otherwise: raise `ValueError` with descriptive message

---

## 6. Test Requirements

### 6.1 New Unit Tests (`tests/unit/test_calendar_mcp.py`)

| Test Name | Description |
|-----------|-------------|
| `test_daily_recurrence` | Daily recurrence adds `["RRULE:FREQ=DAILY"]` to event body |
| `test_weekly_recurrence_single_day` | `weekly;MO` maps to `FREQ=WEEKLY;BYDAY=MO` |
| `test_weekly_recurrence_multiple_days` | `weekly;MO,WE,FR` maps to `FREQ=WEEKLY;BYDAY=MO,WE,FR` |
| `test_no_recurrence_default` | No `recurrence` param = no recurrence field in body |
| `test_no_recurrence_empty_string` | Empty string treated as no recurrence |
| `test_unsupported_recurrence_returns_error` | `"monthly"` returns error dict |
| `test_weekly_without_days_returns_error` | `"weekly"` (no days) returns error dict |
| `test_weekdays_shorthand` | `"weekdays"` maps to `MO,TU,WE,TH,FR` |
| `test_recurrence_with_date` | Recurrence works when explicit date is provided |

### 6.2 Existing Tests — No Changes

All existing tests in `test_calendar_mcp.py` MUST pass without modification:

- `test_crear_evento_basic`
- `test_crear_evento_with_date`
- `test_crear_evento_default_date_is_today`
- `TestParseTime` (all 9 tests)
- `test_invalid_time_in_crear_evento_returns_error`

### 6.3 Agent Tests (`tests/unit/test_agents.py`)

No changes needed — the agent import and structure tests should remain unchanged. The recurrence behavior is tested via eval, not pytest (non-deterministic LLM output). However, a test MAY be added to verify the orchestrator's updated instruction string contains recurrence keywords.

---

## 7. Edge Cases

| Edge Case | Handling |
|-----------|----------|
| `recurrence=""` (empty string) | Treated as `None` — single event, no RRULE |
| `recurrence="weekly"` (missing days) | Return error — invalid format |
| `recurrence="weekly;"` (empty day list) | Return error — invalid format |
| `recurrence="WEEKLY;MO"` (uppercase) | Accept — normalize to lowercase `"weekly;MO"` |
| `recurrence="WEEKLY;mo"` (mixed case days) | Accept — normalize days to uppercase |
| Unsupported pattern like `"monthly"`, `"yearly"`, `"every 2 days"` | Return error — unsupported |
| Recurrence with past date | Accept (Google Calendar API handles it); agent MAY clarify if date is suspicious (deferred to V2) |
| Recurrence with non-existent day code (e.g., `"weekly;XX"`) | Return error — invalid day code |

---

## 8. Test Command

```bash
pytest tests/unit/test_calendar_mcp.py -v
```

All tests MUST pass before the change is considered complete.

---

## 9. Dependencies

- No new Python packages required
- Google Calendar API v3 already supports the `recurrence` field natively
- The `googleapiclient` library handles RFC 5545 RRULE strings as-is
