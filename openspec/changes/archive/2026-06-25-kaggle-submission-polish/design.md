# Design: Kaggle Submission Polish

## Technical Approach

Single-pass polish pass — additive changes only (comments, docs, new files). No refactoring, no feature changes. Target: ~350-380 lines to stay within the 400-line review budget. Every file modification follows existing patterns exactly.

## Architecture Overview

No architecture changes. The existing structure is the target:

```
User → Root Agent (aita_lagun) → recordatorio / info_salud
                                   ↕ MCP stdio        ↕ MCP stdio
                              Calendar Server      PDF Server
```

Polish touches every file in this diagram (comments/doscstrings) plus project-level files (README, Dockerfile, .env.example, skills, WRITEUP).

## README Design

**Structure** (9 sections, ~200 lines):
1. Badges (Python 3.10+, license)
2. Problem (2-3 sentences: elderly Barakaldo, medication, Osakidetza complexity, en/es/eu)
3. Solution (multi-agent ADK, HITL reminders, PDF health info)
4. Architecture section with `![Architecture](docs/architecture.png)` — links to existing diagram
5. Quick Start (copy-pasteable code blocks)
6. Detailed Setup (venv, .env, service account, running)
7. Testing (pytest, coverage)
8. Troubleshooting table (API key, module not found, PDF, Calendar)
9. Contributing / License

**Tone**: Warm, direct, professional. Code blocks with `bash` language tags. Commands prefixed with `$` or `python -m`.

## Code Comments Design

All docstrings follow PEP 257. Inline comments explain "why", not "what".

| File | Docstring Content | Inline Comments |
|------|------------------|-----------------|
| `agents/agent.py` | Root agent purpose, sub-agent routing, language detection callback | Language detection keyword heuristics (why Basque words checked first) |
| `agents/orchestrator.py` | Recordatorio agent, HITL explanation via `require_confirmation=True` | Why FunctionTool wraps recordatorio_agent (separation of MCP call from agent tool) |
| `agents/recordatorio_agent.py` | Calendar event creation function | No PHI stored, timezone assumption (`Europe/Madrid`) |
| `agents/info_salud_agent.py` | InfoSalud agent, PDF search connection | Public PDF sourcing, no personal data |
| `agents/__init__.py` | Package exports | Why import order matters (circular import history) |
| `mcp_servers/calendar_mcp.py` | MCP server, tool, auth flow | Service account vs OAuth choice, credential resolution logic |
| `mcp_servers/pdf_mcp.py` | MCP server, search logic | PDF path construction, case-insensitive search, snippet limit |
| `mcp_servers/__init__.py` | Package docstring | — |

### Key Docstring Locations

- `recordatorio_agent.py:crear_evento_calendar` — Args (medication, time, date), Returns (dict with status/event_id/html_link), Raises (ValueError if env not set)
- `calendar_mcp.py:_get_calendar_service` — Args (via env), Returns (service object), Raises (ValueError if credentials missing)
- `calendar_mcp.py:crear_evento_calendar` — MCP tool docstring matching the ADK function

## Dockerfile Design

**Base**: `python:3.10-slim` (smallest compatible base, matches requirements.txt Python version)

**Layers** (3, optimized for caching):
1. `COPY requirements.txt . && pip install --no-cache-dir -r requirements.txt`
2. `COPY . .`
3. `CMD ["python", "-m", "agents.agent"]`

**Env**: `PYTHONUNBUFFERED=1` for Cloud Run log streaming.

**.dockerignore**: Excludes `__pycache__`, `.git`, `.env`, `tests/`, `*.pyc`, cache dirs, `*.md` (except README.md), `openspec/`, `.coverage`.

**Cloud Run note**: Container listens on stdin (ADK CLI mode). For production Cloud Run, an HTTP wrapper (FastAPI) would be needed — out of scope for this polish.

## WRITEUP.md Design

Three targeted modifications:

1. **Section 3 (Architecture)**: Replace the ASCII diagram with `![Architecture](docs/architecture.png)` — the image already exists at `docs/architecture.png`. Keep the ASCII diagram as a fallback (comment: hidden from render).

2. **Section 7 (Build Journey)**: Add 2-3 concrete examples under existing challenges:
   - The circular import fix (`agents/__init__.py` → `agents/agent.py` double-load)
   - MCP subprocess lifecycle on Windows (path handling, timeout)
   - LLM description field tuning for reliable routing

3. **Section 8 (Concepts Demonstrated)**: Add "where demonstrated" column with file references (already partially done — ensure every row links to specific files).

## Skills/SKILL.md Design

**Frontmatter**:
```yaml
---
name: create_reminder
description: Creates medication reminder with human confirmation via Google Calendar
version: 1.0
---
```

**Sections**: Purpose, Input parameters (medication/str, time/str, date/optional/str), Output format (event_id or cancellation), Usage example (conversation flow showing HITL prompt), Security notes (requires confirmation, no PHI stored, public PDFs only).

**Tone**: Technical but accessible. Target: LLM consuming this as a skill definition.

## .env.example Design

Three variables, each with a comment explaining purpose and format:

| Variable | Comment | Example |
|----------|---------|---------|
| `GOOGLE_AI_STUDIO_API_KEY` | Required for ADK agent LLM | `your_api_key_here` |
| `GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON` | Path to JSON or inline JSON string | `path/to/service-account.json` |
| `GOOGLE_CALENDAR_ID` | Optional, defaults to primary | `primary` |

Preserve existing `GOOGLE_GENAI_USE_VERTEXAI=False` (needed for local dev with AI Studio).

## Risk Mitigation

| Risk | Mitigation | Trigger |
|------|------------|---------|
| **400-line budget exceeded** | Trim README examples first, defer least-critical docstrings second, defer WRITEUP.md polish third | Track files during apply; if sum > 350, cut scope |
| **Docker build failure** | Test `docker build -t aita-lagun .` locally before marking done | Build fails on Windows path or dependency issue |
| **README too verbose** | Target 200 lines max; use tables for troubleshooting, not paragraphs | Line count check after writing |
| **Docstring style inconsistency** | Use existing calendar_mcp.py docstrings as style template for all new docstrings | Review pass after apply |

No migration, no feature flags, no rollout — all changes are additive documentation.

## Open Questions

None. All design decisions are resolved by the spec and codebase reading.
