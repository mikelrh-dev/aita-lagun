# Tasks: Visual Design Assets

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~730 (additions) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1: Visual assets → PR 2: Backend + Tests → PR 3: Frontend + Setup |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Stitch screens + DESIGN.md | PR 1 | ~50 lines, independent, base=main |
| 2 | app/ package + backend + tests | PR 2 | ~285 lines, base=main, testable via TestClient |
| 3 | Frontend + dev setup + README | PR 3 | ~395 lines, base=main, depends on PR 2 API contract |

## Phase 1: Visual Design Assets

- [ ] 1.1 Generate 3 mockup screens in Stitch (chat interface, mobile conversation, feature cards) — export PNG to `docs/`
- [ ] 1.2 Extract design tokens from Stitch project `13558646535241964762` → `DESIGN.md` (colors, typography, spacing, shapes)

## Phase 2: Backend Foundation

- [x] 2.1 Create `app/__init__.py` — empty package init
- [x] 2.2 Add `fastapi>=0.115.0`, `uvicorn[standard]>=0.34.0` to `requirements.txt`
- [x] 2.3 Add `"app"` to `[tool.coverage.run].source` in `pyproject.toml`

## Phase 3: Backend Implementation (TDD)

- [x] 3.1 RED: Write `tests/unit/test_chat_api.py` (consolidated) — mock `Runner.run_async`, assert `ask_agent()` contract + `TestClient` tests for `POST /api/chat`
- [x] 3.2 GREEN: Create `app/agent_runner.py` — `async def ask_agent(message: str) -> str` wrapping ADK Runner with lazy-init singleton pattern
- [x] 3.3 RED: Test coverage included in `test_chat_api.py` (5 tests: agent reply, empty message, 200, 422, health)
- [x] 3.4 GREEN: Create `app/main.py` — FastAPI app with CORS (`*`), `POST /api/chat` endpoint delegating to `ask_agent()`

## Phase 4: Frontend

- [ ] 4.1 Create `app/static/index.html` — single-page chat UI: dark theme (`#0f172a` bg), teal accent (`#2dd4bf`), Hanken Grotesk + Atkinson Hyperlegible Next, chat bubbles (user right, assistant left), loading spinner, marked.js CDN, responsive 375px–1920px, language badge

## Phase 5: Dev Setup & Docs

- [ ] 5.1 Create `scripts/run_dev.py` — `uvicorn.run("app.main:app", host="0.0.0.0", port=8080)`
- [ ] 5.2 Update `README.md` — add `.env` variable table (GEMINI_API_KEY, GOOGLE_SERVICE_ACCOUNT, GOOGLE_CALENDAR_ID), dev setup commands, link to DESIGN.md
- [ ] 5.3 Verify full stack: `pytest` passes, `python scripts/run_dev.py` starts without import errors
