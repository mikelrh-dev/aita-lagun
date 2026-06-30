# Tasks: Optional Recurrence for Medication Reminders

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~275 (170 test + 105 impl) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

---

## Phase 1: Foundation — `_build_rrule` Pure Function

Per TDD, tests are written BEFORE implementation.

- [ ] 1.1 **RED**: Write `TestBuildRrule` class in `tests/unit/test_calendar_mcp.py` with 13 unit tests covering all `_build_rrule` inputs (None, empty, daily, weekdays, weekly;MO, weekly;MO,WE,FR, all-days, unsupported, no-days, empty-days, invalid-day, case-normalization, mixed-case-days). All tests fail initially because `_build_rrule` doesn't exist.
- [ ] 1.2 **GREEN**: Implement `_build_rrule(recurrence)` in `mcp_servers/calendar_mcp.py` — add `import logging`, `_VALID_DAY_CODES`, `logger = logging.getLogger(...)`, and the full function with validation, normalization, and RRULE generation. All 13 tests pass.
- [ ] 1.3 **REFACTOR**: Verify `_build_rrule` function is clean — docstring matches design, logging at DEBUG on every path, error messages use consistent format. No behavior changes.

## Phase 2: Tool Integration — `crear_evento_calendar` Recurrence Support

- [ ] 2.1 **RED**: Write 9 integration tests in `tests/unit/test_calendar_mcp.py` for recurrence in `crear_evento_calendar` (daily, weekly;MO, weekly;MO,WE,FR, no-recurrence-default, empty-string, unsupported-error, weekly-no-days-error, weekdays-shorthand, recurrence-with-date). Tests that require API calls are mocked via `_get_calendar_service`. All new tests fail because the tool doesn't handle `recurrence` yet.
- [ ] 2.2 **GREEN**: Update `crear_evento_calendar` signature to accept `recurrence: Optional[str] = None`, add `_build_rrule` try/except block before the service call, inject `event_body["recurrence"]` when rrule is not None. All 9 new integration tests pass.
- [ ] 2.3 Verify existing 12 tests (`TestCalendarMCP` 3 + `TestParseTime` 9) still pass with zero modifications.

## Phase 3: Agent Instruction Update (Independent — Parallel with Phase 1-2)

- [ ] 3.1 Update `agents/orchestrator.py` — replace the `recordatorio` agent's `instruction` with the extended version (~28 lines) covering cross-language recurrence mapping, proactive ask, and graceful decline for unsupported patterns.
- [ ] 3.2 (Optional) Add a MAY-test: verify `recordatorio.instruction` string contains recurrence keywords like `"recurrence"`, `"daily"`, `"weekly"` — string assertion, no LLM interaction.

## Phase 4: Full Verification

- [ ] 4.1 Run `pytest tests/unit/test_calendar_mcp.py -v` — all 34 tests pass (12 existing + 13 `_build_rrule` unit + 9 integration).
- [ ] 4.2 Run `pytest tests/unit/ -v` — confirm agent tests still pass.

---

## Implementation Order

**Phases 1 → 2 → 4** are strictly sequential (each depends on the previous). **Phase 3** (agent instruction) is fully independent and can run in parallel with Phases 1-2 since it only changes a prompt string, not tool logic.

## Review Workload Forecast

- **Estimated changed lines**: ~275 total (~170 test, ~105 implementation)
- **400-line budget risk**: Low — well under the threshold, single PR is safe
- **Chained PRs recommended**: No — the change is focused, tests are co-located with code per TDD, and total diff fits comfortably in one review
- **Delivery strategy**: `ask-on-risk` — but risk is low, so no chaining needed
- **Decision needed before apply**: No — proceed with single PR
