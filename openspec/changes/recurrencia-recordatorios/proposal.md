# Proposal: Optional Recurrence for Medication Reminders

## Intent

Add optional Google Calendar event recurrence to the `crear_evento_calendar` tool so users can create daily or weekly recurring medication reminders without having to repeat the same request every day.

## Business Problem

For medications like Sintrom (taken daily) or weekly injections, the current implementation creates only a **single event** for today. Users who say "remind me to take Sintrom at 8am every day" get only one event and must repeat the request each day. This is a real friction point for elderly users who depend on consistent reminders.

The Kaggle evaluation also expects agents to handle recurrent requests naturally — the current gap would lose points in the "completeness" and "correctness" criteria.

## Target Behavior

### User Stories

| ID | Story | Priority |
|----|-------|----------|
| US-1 | As a user, I can say "Remind me to take Sintrom at 8am" and get a single event for today (current behavior, unchanged) | P0 |
| US-2 | As a user, I can say "Remind me to take Sintrom at 8am every day" and get a daily recurring event starting today | P0 |
| US-3 | As a user, I can say "Remind me to take Sintrom at 8am every Monday" and get a weekly recurring event on Mondays | P0 |
| US-4 | As a user who says "Remind me to take Sintrom at 8am" without specifying recurrence, the agent asks "Do you want this just for today, or every day?" | P1 |
| US-5 | As a user, I can say "Remind me to take Sintrom at 8am every weekday" and get a recurring event Mon-Fri | P1 |

### Interaction Examples

**US-4 (agent asks about recurrence):**
> User: "Remind me to take Sintrom at 8am"
> Agent: "Do you want this just for today, or every day?"
> User: "Every day"
> → Creates daily recurring event

**US-2 (user specifies daily):**
> User: "Remind me to take Sintrom at 8am every day"
> Agent: (summarizes and confirms) "I'll create a daily reminder for Sintrom at 08:00 starting today. Shall I proceed?"
> User: "Yes"
> → Creates daily recurring event

**US-3 (user specifies weekly):**
> User: "Remind me to take Sintrom at 8am every Monday"
> → Creates weekly recurring event on Mondays

## Current-State Gap

| Area | Current | Required |
|------|---------|----------|
| `crear_evento_calendar` signature | `(medication, time, date?)` — no recurrence param | Accept optional `recurrence` param (e.g. `"daily"`, `"weekly;MO"`) |
| Event body sent to Google Calendar | No `recurrence` field | Include `recurrence: ["RRULE:FREQ=DAILY"]` array in event body |
| Agent instruction in `recordatorio` | Does not mention recurrence | Must instruct LLM to ask about recurrence when not specified |
| Tests | Only single-event scenarios | Add tests for daily, weekly, weekday recurrence |

## Proposed Solution

### 1. `mcp_servers/calendar_mcp.py` — Add `recurrence` parameter to `crear_evento_calendar`

Add an optional `recurrence` parameter to the tool signature:

```python
def crear_evento_calendar(
    medication: str,
    time: str,
    date: Optional[str] = None,
    recurrence: Optional[str] = None,  # NEW
) -> dict:
```

The `recurrence` value maps to Google Calendar API's RFC 5545 RRULE format:

| User says | `recurrence` value | Generated RRULE |
|-----------|-------------------|-----------------|
| "every day" | `"daily"` | `["RRULE:FREQ=DAILY"]` |
| "every Monday" | `"weekly;MO"` | `["RRULE:FREQ=WEEKLY;BYDAY=MO"]` |
| "every weekday" | `"weekly;MO,TU,WE,TH,FR"` | `["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"]` |

When `recurrence` is `None` (default), behavior is identical to current — single event with no recurrence.

### 2. `agents/orchestrator.py` — Update agent instruction

Update the `recordatorio` agent's instruction prompt to:
- Mention that the `crear_evento_calendar` tool supports optional recurrence
- Instruct the LLM to ask about recurrence when the user doesn't specify it (e.g., "just for today or every day?")
- Instruct the LLM to map natural language ("every day", "every Monday", "every weekday") to the correct `recurrence` parameter value

### 3. `tests/unit/test_calendar_mcp.py` — Add recurrence tests

Extend the test class with:
- Daily recurrence adds `recurrence` field with `["RRULE:FREQ=DAILY"]`
- Weekly recurrence adds `["RRULE:FREQ=WEEKLY;BYDAY=MO"]`
- Weekday recurrence adds `["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"]`
- Default (no recurrence) remains unchanged — no `recurrence` in event body

## Edge Cases to Consider

| Edge Case | How to Handle |
|-----------|--------------|
| Recurrence with explicit date in the past | The API will accept it but the user probably meant today — agent should clarify. Defer to spec phase. |
| "Every 2 days" / "every other day" | Not supported in V1. The agent should say "I can do daily or weekly. Would either of those work?" |
| "Every month" / monthly recurrence | Not supported in V1. Same graceful fallback. |
| "Until next month" / end date for recurrence | Google Calendar RRULE supports `UNTIL` and `COUNT`. Could be V2. For V1, no end date — events continue indefinitely. |
| Cross-language mapping | Spanish: "todos los días" → daily, "los lunes" → weekly;MO. Basque: "egunero" → daily, "astelehenero" → weekly;MO. Must handle all three languages. |
| Event duration for recurring events | Same as single events: 15 min after start time. Applies to every occurrence. |
| Empty/null recurrence string | Treat same as `None` — single event. |

## Non-Goals

- Editing or deleting existing recurring events (the Google Calendar API supports this via `eventId` but is out of scope)
- Monthly, yearly, or custom recurrence patterns (INTERVAL, UNTIL, COUNT, BYMONTHDAY, etc.)
- UI for managing recurring events
- Listing/cancelling specific occurrences of a recurring event
- Notifications about upcoming recurring events (the agent only creates them)

## Approach Summary

| Layer | Change | Impact |
|-------|--------|--------|
| `mcp_servers/calendar_mcp.py` | Add `recurrence: Optional[str]` param, map to RRULE in event body | Non-breaking — default None preserves current behavior |
| `agents/orchestrator.py` | Update `instruction` to teach LLM about recurrence + ask behavior | Prompt-only change, no code logic changes |
| `tests/unit/test_calendar_mcp.py` | Add test cases for recurrence patterns | Extended coverage |

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `mcp_servers/calendar_mcp.py` | Modified | Add `recurrence` parameter to tool; add RRULE mapping logic |
| `agents/orchestrator.py` | Modified | Update instruction prompt |
| `tests/unit/test_calendar_mcp.py` | Extended | Add recurrence test cases |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Google Calendar API rejects malformed RRULE | Low | Validate recurrence format server-side before sending; map known strings only |
| LLM misinterprets recurrence mapping (e.g., "weekly Monday" vs "every Monday") | Medium | Provide explicit examples in instruction prompt; `agents-cli eval` to validate |
| Regression: existing single-event behavior breaks | Low | Default `recurrence=None` keeps exact same code path; existing tests must pass |

## Rollback Plan

Revert `mcp_servers/calendar_mcp.py` — remove `recurrence` parameter and RRULE logic. Revert `agents/orchestrator.py` instruction update. All changes are contained in those two files, with no database or external state changes.

## Dependencies

- Google Calendar API v3 — already in use, no new packages needed
- The `googleapiclient` library already handles the `recurrence` field natively — it's a standard event property

## Success Criteria

- [ ] `crear_evento_calendar(medication="Sintrom", time="08:00", recurrence="daily")` creates an event with `recurrence: ["RRULE:FREQ=DAILY"]` in the API call
- [ ] `crear_evento_calendar(medication="Sintrom", time="08:00", recurrence="weekly;MO")` creates an event with `RRULE:FREQ=WEEKLY;BYDAY=MO`
- [ ] `crear_evento_calendar(medication="Sintrom", time="08:00")` (no recurrence) creates the exact same event body as today — no `recurrence` field
- [ ] All existing tests pass without modification
- [ ] Agent asks about recurrence when the user provides medication + time without specifying recurrence
