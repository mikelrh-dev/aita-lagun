# Proposal: ADK + MCP Real Integration

## Intent

Plain Python prototypes masquerading as ADK agents. Calendar MCP returns simulated events, PDF MCP has wrong paths, medication/time hardcoded, zero tests. Migrate to real Google ADK multi-agent architecture with real MCP protocol servers and Google Calendar. Pure re-architecture — no spec-level behavior changes.

## Scope

**In**: Root ADK Agent with LLM routing; RecordatorioAgent with real Google Calendar via MCP; InfoSaludAgent with real PDF MCP server; FastMCP servers for calendar + PDF; fix PDF file names; parse medication/time from message; test infra; add google-adk/mcp to requirements; HITL for calendar; multi-language.

**Out**: YouTube video, Kaggle Writeup, Cloud Run deployment, advanced NLP, git repo.

## Capabilities

**New**: None. **Modified**: None — implementation only, spec-level unchanged.

## Approach

Sub-agent Delegation with LLM Routing (Approach 1). Root `Agent(sub_agents=[...])` where LLM delegates based on `description`. `before_agent_callback` detects language and sets `state["lang"]`. Sub-agents use `McpToolset(StdioConnectionParams)` for MCP tools. Calendar uses `FunctionTool(require_confirmation=True)` for HITL. AI Studio API key auth (`GOOGLE_API_KEY`).

## Affected Areas

- `agents/agent.py` — NEW (root agent + entry point)
- `agents/orchestrator.py` — REWRITE (ADK Agent)
- `agents/recordatorio_agent.py` — REWRITE (ADK sub-agent + MCP)
- `agents/info_salud_agent.py` — REWRITE (ADK sub-agent + MCP)
- `agents/__init__.py` — UPDATE (export root_agent)
- `mcp_servers/calendar_mcp.py` — REWRITE (FastMCP + Calendar API)
- `mcp_servers/pdf_mcp.py` — REWRITE (FastMCP + correct paths)
- `requirements.txt` — UPDATE (add google-adk, mcp)
- `.env.example` — UPDATE (add GOOGLE_API_KEY)
- `tests/` — NEW (pytest + unit tests)
- `pyproject.toml` — NEW (pytest config)

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| ADK API key auth | Low | AI Studio key in .env |
| Calendar OAuth | Med | Service account for demo |
| MCP stdio lifecycle | Low | McpToolset handles cleanup |
| Zero test baseline | Med | Strict TDD enforced |
| LLM routing non-determinism | Med | Agent descriptions tuned via eval |

## Rollback Plan

Keep old code in `backup/` branch. Each MCP server independently revertible. ADK Agent swappable by reverting `agents/*.py`.

## Dependencies

`google-adk` ≥ 0.5.0, `mcp` (FastMCP), Google Calendar API enabled, Python 3.10+

## Success Criteria

- [ ] `python -m agents.agent` starts ADK agent loop
- [ ] "remind me Sintrom at 8am" creates real Calendar event after confirmation
- [ ] "how do I book an Osakidetza appointment?" returns PDF content
- [ ] Basque "gogoratu pastilla 8:00" triggers RecordatorioAgent
- [ ] `pytest` passes (MCP server unit tests)
- [ ] All existing functionality preserved (regression)
