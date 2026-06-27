# Tasks: Kaggle Submission Polish

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~350-380 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: stacked-to-main
400-line budget risk: Low

## Phase 1: Foundation

- [x] 1.1 Create `Dockerfile` — python:3.10-slim, 3-layer build, PYTHONUNBUFFERED=1
- [x] 1.2 Create `.dockerignore` — exclude cache, tests, .env, openspec, *.md (except README)
- [x] 1.3 Complete `.env.example` — document GOOGLE_API_KEY, GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON, GOOGLE_CALENDAR_ID with descriptions

## Phase 2: Code Comments

- [x] 2.1 Add module docstrings + inline comments to `agents/agent.py` (root agent routing, language detection callback, Basque-first heuristic)
- [x] 2.2 Add module docstrings + inline comments to `agents/orchestrator.py` (recordatorio agent, HITL via require_confirmation, FunctionTool wrapper rationale)
- [x] 2.3 Add module docstrings + inline comments to `agents/recordatorio_agent.py` (crear_evento_calendar, no PHI stored, Europe/Madrid timezone)
- [x] 2.4 Add module docstrings + inline comments to `agents/info_salud_agent.py` (InfoSalud agent, public PDF sourcing)
- [x] 2.5 Add module-level docstring to `agents/__init__.py` (package exports, import order reasoning)
- [x] 2.6 Add module docstrings + inline comments to `mcp_servers/calendar_mcp.py` (MCP server, service account vs OAuth, credential resolution)
- [x] 2.7 Add module docstrings + inline comments to `mcp_servers/pdf_mcp.py` (MCP server, PDF search, case-insensitive logic, snippet limit)
- [x] 2.8 Add module-level docstring to `mcp_servers/__init__.py`

## Phase 3: Documentation

- [x] 3.1 Rewrite `README.md` — 9 sections: badges, problem, solution, architecture with diagram link, quick start, detailed setup, testing, troubleshooting table, contributing/license
- [x] 3.2 Polish `WRITEUP.md` — embed architecture diagram image ref, expand Build Journey (circular import, MCP lifecycle, LLM routing), add "where demonstrated" column with file links
- [x] 3.3 Refine `skills/SKILL.md` — proper frontmatter, expanded description, input/output params, usage example, security notes

## Phase 4: Cleanup

- [x] 4.1 Deprecate `WRITEUP_OUTLINE.md` — add note that it is superseded by WRITEUP.md
