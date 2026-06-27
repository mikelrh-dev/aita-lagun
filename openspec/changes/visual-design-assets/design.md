# Design: Visual Design Assets

## Technical Approach

Wrap the existing ADK agent behind a FastAPI REST endpoint served with a single-page HTML/JS chat frontend using Stitch design tokens. ADK's `McpToolset` already manages MCP subprocesses internally — no manual lifecycle code needed. Uvicorn serves both API and static files from the same process on port 8080.

## Architecture Decisions

### Decision: ADK Runner Lifecycle

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Create Runner per request | ✅ Stateless, ❌ Re-connects MCP each time | ❌ Rejected |
| **Create Runner once at startup** | ✅ Persistent session, ✅ MCP subprocess created once | **✅ Chosen** |
| Lazy init on first request | ✅ Fast startup, ❌ First request is slow | ❌ Not needed |

`InMemorySessionService` is created in FastAPI's `lifespan` context and shared across requests so conversation history persists across turns (spec R4).

### Decision: MCP Subprocess Management

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Manual subprocess spawn/terminate | ✅ Explicit control, ❌ Duplicates ADK's own lifecycle | ❌ Rejected |
| **Let ADK handle via McpToolset** | ✅ Zero code, ✅ Existing pattern in `info_salud_agent.py` | **✅ Chosen** |
| Run MCP servers in-process | ✅ No subprocess overhead, ❌ Tight coupling | ❌ Breaks existing pattern |

The PDF MCP server is already managed by `McpToolset(StdioConnectionParams(...))` which spawns a subprocess on first tool invocation. The calendar server is imported directly as a `FunctionTool` — no subprocess needed. No new lifecycle code required.

### Decision: Frontend Format

| Option | Tradeoff | Decision |
|--------|----------|----------|
| **Single HTML with inline CSS/JS** | ✅ Zero build, ✅ Self-contained, ✅ Fast loading | **✅ Chosen** |
| Split .html/.css/.js files | ✅ Separation of concerns, ❌ Extra HTTP requests | ❌ Overkill for one page |
| SPA framework (React, Vue) | ✅ Component model, ❌ 100KB+ bundle | ❌ Not justified |

Single file approach keeps the deliverable under 400 lines and matches the skill level of the project's existing codebase.

### Decision: Markdown Rendering

| Option | Tradeoff | Decision |
|--------|----------|----------|
| marked.js via CDN | ✅ Full spec, ✅ 10KB gzipped | **✅ Chosen** |
| Custom regex parser | ✅ Zero deps, ❌ Fragile, ❌ No table/list support | ❌ Rejected |
| Server-side rendering | ✅ Cleaner, ❌ Extra response size, ❌ HTML in JSON | ❌ Rejected |

marked.js is a lightweight, well-audited library that handles PDF-extracted formatting (bold, lists, headings) out of the box.

### Decision: Dev Server & File Structure

| Option | Tradeoff | Decision |
|--------|----------|----------|
| **`app/` directory with FastAPI** | ✅ Co-locates with existing agents/ | **✅ Chosen** |
| `web/` separate directory | ✅ Clearer boundary, ❌ Extra path config | ❌ Not needed |
| `scripts/run_dev.py` entry point | ✅ One command startup | **✅ Chosen** |

## Data Flow

```
Browser (index.html)
    │  POST /api/chat {"message": "..."}
    ▼
FastAPI (app/main.py)
    │  CORS: Allow localhost origins
    │  Validate: reject empty message → 422
    ▼
Agent Runner (app/agent_runner.py)
    │  runner.run_async(user_id="user", session_id="default", ...)
    │  Iterates AsyncGenerator → collects final response
    ▼
ADK Runner → root_agent → sub_agent routing
    │  ├─ McpToolset spawns pdf_mcp.py subprocess (first call only)
    │  └─ FunctionTool calls calendar_mcp functions in-process
    ▼
Response JSON {"reply": "..."}
    │
    ▼
Browser renders chat bubble (Markdown via marked.js)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `app/__init__.py` | Create | Empty package init |
| `app/main.py` | Create | FastAPI app: lifespan, CORS, `/api/chat` endpoint |
| `app/agent_runner.py` | Create | Wraps ADK Runner setup + `ask_agent()` function |
| `app/static/index.html` | Create | Chat frontend: dark theme, inline CSS/JS, Stitch tokens |
| `scripts/run_dev.py` | Create | Entry point: `uvicorn.run(app, host="0.0.0.0", port=8080)` |
| `requirements.txt` | Modify | Add `fastapi>=0.115.0`, `uvicorn[standard]>=0.34.0` |
| `pyproject.toml` | Modify | Add `app` to coverage source |
| `tests/unit/test_app.py` | Create | Tests for `/api/chat` endpoint (mock ADK agent) |
| `tests/unit/test_agent_runner.py` | Create | Tests for `ask_agent()` function |

## Interfaces / Contracts

**POST /api/chat**
```python
# Request
{"message": "remind me to take Sintrom at 8am"}

# Response (200)
{"reply": "I've noted your reminder for Sintrom at 8:00 AM. Shall I create the calendar event?"}

# Error (422)
{"detail": [{"loc": ["body", "message"], "msg": "field required"}]}

# Error (500)
{"detail": "Agent processing failed: <error message>"}
```

**Agent Runner contract**
```python
# app/agent_runner.py

async def ask_agent(message: str) -> str:
    """Send a message to the ADK agent and return the final response text.

    Args:
        message: User message text (must be non-empty).

    Returns:
        The agent's final response as plain text.

    Raises:
        RuntimeError: If agent fails to produce a response.
    """
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `ask_agent()` with mocked Runner | Mock `Runner.run_async`, assert return text matches expected event content |
| Unit | `/api/chat` endpoint | Use `TestClient`, mock `ask_agent()`, test 200, 422, 500 paths |
| Unit | Frontend renders correct bubbles | Not tested (static HTML is visual deliverable) |

Tests follow existing conventions: `pytest-asyncio`, `MagicMock`, `tests/unit/` directory, `--tb=short`.

## Migration / Rollout

No migration required. All files are new additions. Existing CLI entry point (`python -m agents.agent`) remains untouched.

## Open Questions

- [ ] Confirm 8080 vs 8000 as default port (spec says 8080)
- [ ] Confirm whether Kaggle expects web UI as a submission deliverable or purely for documentation
