# Exploration: ADK + MCP Real Integration

## Current State

The project uses plain Python classes (no `google.adk` imports) masquerading as agents. MCP servers are simple Python functions, not MCP protocol implementations. Key problems:

- **agents/orchestrator.py**: Plain class with `detect_lang()` and `route()` using string matching — no LLM, no ADK
- **agents/recordatorio_agent.py**: Hardcoded time `08:00`, simulated calendar event, CLI-based human-in-the-loop via `input()`
- **agents/info_salud_agent.py**: Calls `buscar_en_pdfs()` which references **wrong file paths** (`data/osakidetza_cita_previa.pdf`, `data/centros_barakaldo.pdf` instead of actual files `01_cita_previa_osakidetza.pdf`, `02_horarios_barakaldo.pdf`)
- **mcp_servers/calendar_mcp.py**: Returns `f'event_{medication}_{time}_simulated'` — no real MCP protocol, no Google Calendar API
- **mcp_servers/pdf_mcp.py**: Reads PDFs directly via PyMuPDF with wrong paths, no tool schema, no MCP protocol
- **requirements.txt**: Missing `google-adk`, `mcp` packages
- **No tests at all** (strict TDD enabled in openspec but zero test files)
- **No git repo**

## Affected Areas

- `requirements.txt` — must add `google-adk`, `mcp` (or `fastmcp`), update version pins
- `agents/orchestrator.py` — rewrite from plain class to ADK `Agent` with sub-agents
- `agents/recordatorio_agent.py` — rewrite as ADK sub-agent with calendar MCP tool connection
- `agents/info_salud_agent.py` — rewrite as ADK sub-agent with PDF MCP tool connection
- `agents/__init__.py` — update for ADK agent discovery (export `root_agent`)
- `mcp_servers/calendar_mcp.py` — rewrite as real FastMCP server with proper tool definitions
- `mcp_servers/pdf_mcp.py` — rewrite as real FastMCP server with correct file paths and clean query logic
- `.env.example` — add ADK auth-related variables (e.g., `GOOGLE_API_KEY`, `GOOGLE_GENAI_USE_VERTEXAI`)
- New: `agents/agent.py` — root ADK agent definition (entry point for ADK runner)
- New: `tests/unit/test_calendar_mcp.py` — unit tests for calendar MCP server
- New: `tests/unit/test_pdf_mcp.py` — unit tests for PDF MCP server
- New: `tests/unit/test_agents.py` — unit tests for agent routing/lang detection
- `data/` — no changes needed (files already exist with correct names)

## Approaches

### Approach 1: Sub-agent Delegation with LLM Routing (Recommended)

A single root `Agent` with `sub_agents` for Recordatorio and InfoSalud. The LLM decides which agent to use based on `description`. Language context is injected via state (`before_agent_callback`). Human-in-the-loop uses ADK's built-in `request_confirmation` mechanism.

**Architecture:**

```
Root Agent (llm_agent)
 ├─ before_agent_callback → state["lang"] = detect(message)
 ├─ sub_agents:
 │   ├─ RecordatorioAgent → McpToolset → stdio → python calendar_mcp_server.py
 │   └─ InfoSaludAgent → McpToolset → stdio → python pdf_mcp_server.py
 └─ tools: [detect_language_tool] (optional, or keep in callback)
```

**MCP Servers:**
- Each MCP server is a standalone Python script using FastMCP (`mcp.server.fastmcp.FastMCP`)
- Calendar MCP server: tool `crear_evento_calendar(medication: str, time: str) -> dict` — connects to real Google Calendar API
- PDF MCP server: tool `buscar_en_pdfs(query: str) -> str` — searches correct PDF files with PyMuPDF
- Both run via stdio transport, launched as subprocesses by ADK's `McpToolset`

**Human-in-the-Loop:**
- `FunctionTool(crear_evento_calendar, require_confirmation=True)` — ADK shows confirmation UI instead of raw `input()`
- Or use `register_function_tool` with explicit confirmation callable

**Language Handling:**
- `before_agent_callback` sets `state["lang"]` based on detecting key words in the user message
- Sub-agents read `state["lang"]` to format responses
- The LLM's instruction includes the language preference from state

**Pros:**
- True ADK multi-agent architecture matching the project's README claim
- LLM handles routing intelligently (better than string matching)
- Built-in tool confirmation for human-in-the-loop
- Real MCP protocol — tools are discoverable, have schemas, use JSON-RPC
- Each MCP server is independently testable
- Clean separation: agents orchestrate, MCP servers execute

**Cons:**
- Requires `google-adk` package installation and authentication setup
- MCP servers as subprocesses add complexity to deployment
- Need to configure Google API auth for Calendar integration
- State injection for language requires careful callback wiring
- LLM routing is non-deterministic — eval needed to validate routing behavior

**Effort:** High (full rewrite of 6 files, 3 new files, test infrastructure)

---

### Approach 2: Custom BaseAgent Orchestrator

Keep the deterministic routing logic but use ADK's `BaseAgent` for the orchestrator. The orchestrator manually runs sub-agents using `agent.run_async()`. Sub-agents use `McpToolset` to connect to MCP servers.

**Architecture:**

```
OrchestratorAgent (BaseAgent)
 ├─ _run_async_impl() → manual routing via string matching
 ├─ runs RecordatorioAgent or InfoSaludAgent via agent.run_async()
 └─ each sub-agent has its own McpToolset → MCP servers
```

**Pros:**
- Deterministic routing (no LLM uncertainty)
- Full control over agent lifecycle
- Easier to test routing logic

**Cons:**
- More boilerplate (custom BaseAgent implementation)
- Doesn't demonstrate ADK's LLM routing capability
- Still need ADK and MCP infrastructure
- Harder to maintain as agent count grows

**Effort:** Medium-High

---

### Approach 3: Single Agent with All MCP Tools

One `Agent` with all tools from both MCP servers loaded via multiple `McpToolset` instances. No sub-agents.

**Architecture:**

```
Root Agent (llm_agent)
 └─ tools:
     ├─ McpToolset → calendar_mcp_server.py
     └─ McpToolset → pdf_mcp_server.py
```

**Pros:**
- Simplest migration path
- Fewest file changes
- Single agent, single runner

**Cons:**
- Loses the multi-agent architecture the project was designed for
- All tools in one namespace — potential confusion for the LLM
- No separation of concerns
- Doesn't match the Kaggle capstone requirements for multi-agent demonstration
- Language-specific response formatting is harder

**Effort:** Medium (fewer files, but undermines project goals)

---

## Recommendation

**Approach 1 (Sub-agent Delegation with LLM Routing)** is the recommended path. It aligns with the project's stated architecture (multi-agent), the Kaggle capstone requirements, and demonstrates real ADK + MCP integration. The LLM routing is a feature, not a bug — the current string-matching approach is fragile and doesn't scale.

**Migration order:**
1. Update `requirements.txt` with `google-adk`, `mcp`
2. Rewrite `mcp_servers/calendar_mcp.py` as FastMCP server (real Calendar API calls)
3. Rewrite `mcp_servers/pdf_mcp.py` as FastMCP server (correct file paths)
4. Write `agents/agent.py` with root agent, sub-agents, and MCP tool connections
5. Rewrite `agents/orchestrator.py` → integrated into `agents/agent.py`
6. Rewrite `agents/recordatorio_agent.py` → ADK sub-agent
7. Rewrite `agents/info_salud_agent.py` → ADK sub-agent
8. Write unit tests for MCP servers
9. Write integration tests for agent routing
10. Update `.env.example` and documentation

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Google API authentication required for ADK | Blocking for dev | Use AI Studio API key (`GOOGLE_API_KEY` + `GOOGLE_GENAI_USE_VERTEXAI=False`) — free tier available |
| Google Calendar API requires OAuth for write | High | For Kaggle demo, pre-authorize a service account or use application credentials. Document as demo limitation. |
| MCP stdio subprocess lifecycle | Medium | ADK's `McpToolset` handles cleanup automatically. Test that error propagation works. |
| LLM routing non-determinism | Medium | Use `tools` instead of `sub_agents` for critical routing. Add eval datasets. |
| Windows compatibility for MCP stdio | Low | Feren confirms `adk web --no-reload` works on Windows. Stdio transport works on all platforms. |
| PyMuPDF file path resolution | Low | MCP server runs from project root — use `os.path.join(os.path.dirname(__file__), ...)` for absolute paths |
| Missing test infrastructure | Medium | Strict TDD is enabled. Must write tests before implementation code. |

## Ready for Proposal

Yes
