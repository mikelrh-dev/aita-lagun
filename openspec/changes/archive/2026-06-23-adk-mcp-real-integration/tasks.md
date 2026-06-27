# Tasks: ADK + MCP Real Integration

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~420 (350+ added, 70+ deleted) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR1: Foundation + MCP Servers → PR2: ADK Agents → PR3: Tests |
| Delivery strategy | ask-always |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Base |
|------|------|-----------|------|
| 1 | Foundation + MCP Servers | PR 1 | main |
| 2 | ADK Agents + Wiring | PR 2 | main (after PR 1) |
| 3 | Tests | PR 3 | main (after PR 2) |

## Phase 1: Foundation

- [x] 1.1 Add `google-adk`, `mcp`, `google-genai` to `requirements.txt`
- [x] 1.2 Create `pyproject.toml` with pytest and coverage config
- [x] 1.3 Create `mcp_servers/__init__.py`
- [x] 1.4 Create `tests/__init__.py` and `tests/unit/__init__.py`
- [x] 1.5 Update `.env.example` with `GOOGLE_API_KEY` and `GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON`

## Phase 2: MCP Servers

- [x] 2.1 Rewrite `mcp_servers/calendar_mcp.py`: FastMCP server with Google Calendar API (service account), tool `crear_evento_calendar(medication, time, date)`
  - Actual PDF files used: `data/01_cita_previa_osakidetza.pdf`, `data/02_horarios_barakaldo.pdf`, `data/03_carpeta_salud_funciones.pdf`
- [x] 2.2 Rewrite `mcp_servers/pdf_mcp.py`: FastMCP server with corrected PDF paths, tool `buscar_en_pdfs(query)`
  - Uses real filenames from disk (not the paths from design)

## Phase 3: ADK Agents

- [x] 3.1 Create `agents/agent.py`: root ADK Agent with `sub_agents=[recordatorio, info_salud]`, `before_agent_callback` for language detection, entry point
- [x] 3.2 Update `agents/__init__.py`: export `root_agent` and sub-agent references
- [x] 3.3 Rewrite `agents/recordatorio_agent.py`: tool function `crear_evento_calendar` with Google Calendar API integration
- [x] 3.4 Rewrite `agents/orchestrator.py`: ADK Agent `recordatorio` with FunctionTool (HITL) + McpToolset to calendar MCP
- [x] 3.5 Rewrite `agents/info_salud_agent.py`: ADK Agent `info_salud` with McpToolset to PDF MCP

## Phase 4: Tests

- [x] 4.1 Write `tests/unit/test_pdf_mcp.py`: mock `fitz.open`, verify text extraction and query matching
- [x] 4.2 Write `tests/unit/test_calendar_mcp.py`: mock `googleapiclient.discovery.build`, verify event payload structure
- [x] 4.3 Write `tests/unit/test_agents.py`: verify tool function signatures, type hints, docstrings match ADK expectations
- [x] 4.4 Run `pytest` and verify all tests pass
