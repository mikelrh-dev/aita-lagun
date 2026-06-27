# Design: ADK + MCP Real Integration

## Technical Approach

Sub-agent Delegation with LLM Routing. Root `LlmAgent` delegates to sub-agents via `description`-driven LLM routing. Each sub-agent carries an `McpToolset(StdioConnectionParams)` pointing to its MCP server. Calendar HITL via `FunctionTool(require_confirmation=True)`. Language detection handled by `before_agent_callback` + LLM instruction. AI Studio API key (`GOOGLE_API_KEY`) for auth — no Vertex AI dependency.

The existing `OrchestratorAgent` class and keyword-based routing are replaced wholesale with ADK-native multi-agent orchestration.

## Architecture Decisions

| Decision | Choice | Alternative | Rationale |
|----------|--------|-------------|-----------|
| Agent Structure | Root + sub_agents | Flat agent with all tools | `description` field lets LLM route by intent — cleaner separation, matches Kaggle rubric's "ADK multi-agent" requirement |
| MCP Transport | stdio per server | All-in-one FastMCP | One server per process isolates failures, simpler startup, no port conflicts. `McpToolset` handles lifecycle |
| Tool Naming | One tool per MCP action | Combined mega-tool | LLM works better with focused tool descriptions. Calendar: `crear_evento_calendar`. PDF: `buscar_en_pdfs` |
| Calendar Auth | Service account | OAuth consent screen | No interactive browser in demo. Service account JSON file in `.env` path — sufficient for Kaggle submission |
| Time Parsing | LLM extracts from message | Regex + fallback | LLM handles "8am", "08:00", "ocho de la mañana" uniformly. Regex would need per-language patterns |
| PDF Server | Single `buscar_en_pdfs(query)` | Multi-tool per section | Simplifies MCP surface. PyMuPDF searches all PDFs in one call — three small PDFs, no perf concern |

## Data Flow

```
User message
    │
    ▼
agents/agent.py  (Root ADK Agent)
    │  before_agent_callback: detect language → state["lang"]
    │  LLM routes via sub-agent description + lang context
    │
    ├──→ orchestrator.py (sub-agent: Recordatorio)
    │       │  Extracts medication + time via LLM
    │       │  Calls FunctionTool(crear_evento_calendar)
    │       │  require_confirmation=True → LLM pauses for user
    │       │  User confirms → tool calls MCP Calendar
    │       │
    │       └──→ MCP Calendar (stdio) → Google Calendar API
    │
    └──→ info_salud_agent.py (sub-agent: InfoSalud)
            │  Calls McpToolset → buscar_en_pdfs(query)
            │
            └──→ MCP PDF (stdio) → PyMuPDF reads /data/*.pdf
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `agents/agent.py` | **Create** | Root ADK Agent with `sub_agents=[]`, `before_agent_callback` for lang detection. Entry point: `python -m agents.agent` |
| `agents/orchestrator.py` | **Rewrite** | ADK `Agent` with `McpToolset(StdioConnectionParams)` → calendar MCP. Tool: `crear_evento_calendar` |
| `agents/recordatorio_agent.py` | **Rewrite** | Reminder logic as pure functions (no class). Tool definitions and state helpers |
| `agents/info_salud_agent.py` | **Rewrite** | ADK `Agent` with `McpToolset` → PDF MCP. Tool: `buscar_en_pdfs` |
| `agents/__init__.py` | **Update** | Export `root_agent` and factory functions for sub-agent creation |
| `mcp_servers/calendar_mcp.py` | **Rewrite** | `FastMCP` server wrapping Google Calendar API. Tool: `crear_evento_calendar(medication: str, time: str)` |
| `mcp_servers/pdf_mcp.py` | **Rewrite** | `FastMCP` server with corrected PDF paths (`data/osakidetza_cita_previa.pdf` etc.). Tool: `buscar_en_pdfs(query: str)` |
| `mcp_servers/__init__.py` | **Create** | Package init |
| `requirements.txt` | **Update** | Add `google-adk>=0.5.0`, `mcp`, `google-genai`. Bump `PyMuPDF` |
| `.env.example` | **Update** | `AI_STUDIO_API_KEY` → `GOOGLE_API_KEY`, add `GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON` |
| `pyproject.toml` | **Create** | Pytest config: `testpaths=tests`, asyncio mode, `--cov` options |
| `tests/` | **Create** | `__init__.py`, `unit/` sub-packages |

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | MCP tool functions (`buscar_en_pdfs`) | Pure function tests with pytest — mock `fitz.open`, assert text extraction |
| Unit | Calendar flow (mocked APIs) | Mock `googleapiclient.discovery.build`, verify event payload structure |
| Unit | Agent tool definitions | Test function signatures, docstrings, type hints match ADK expectations |
| Integration | MCP server startup | Start FastMCP server in test process, call via `McpToolset` |
| E2E | Full agent loop | Manual: `python -m agents.agent` + synthetic prompts |

## Open Questions

- [ ] Service account JSON path: hardcoded path vs configurable via `.env`?
- [ ] Google Calendar token refresh: does the Python client handle this automatically?
- [ ] MCP server startup: should `agents/agent.py` launch MCP subprocesses or assume they're pre-started?
