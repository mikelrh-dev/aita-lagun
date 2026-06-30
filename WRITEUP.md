# Aita-Lagun: A Multi-Agent Assistant for Elderly Care in the Basque Country

**Track:** Agents for Good

**Project Link:** [github.com/mikelrh-dev/aita-lagun](https://github.com/mikelrh-dev/aita-lagun)

**Video:** [YouTube link — paste after uploading]

---

## 1. Problem Statement

Barakaldo, an industrial city in the Basque Country, has a significant elderly population. Many older adults manage chronic conditions requiring strict medication schedules — Sintrom (acenocoumarol), a blood thinner, is among the most common. Missing a dose or taking it at the wrong time carries real health risks. Family members often live in separate households and cannot supervise daily routines.

Compounding this, the Basque public health system (Osakidetza) provides comprehensive care but navigating it is not always straightforward. Booking appointments, finding health center hours, and understanding digital health services requires navigating web portals and understanding administrative processes — tasks that are harder for seniors who did not grow up with digital interfaces.

Language adds another layer. While many younger people in the Basque Country are fluent in English and Spanish, older adults often prefer Basque (Euskera) or feel more comfortable in Spanish when discussing health matters. A solution that works only in English excludes the very people who need it most.

The Kaggle AI Agents Capstone asks participants to build practical AI agent solutions using concepts from Google's 5-Day Intensive Vibe Coding Course. Aita-Lagun ("Elderly Friend" in Basque) is our answer — a free, multi-agent conversational assistant that addresses these challenges head-on.

## 2. Solution Overview

Aita-Lagun is a **multi-agent conversational assistant** built with Google's Agent Development Kit (ADK). It provides two core capabilities through natural conversation:

1. **Medication Reminders** — users tell the assistant about their medication (e.g., "remind me to take Sintrom at 8am"). The agent proactively asks about recurrence (daily/weekly/just once), detects if the requested time has already passed and schedules for tomorrow if needed, then requests conversational confirmation before creating the Google Calendar event with the correct RRULE.

2. **Health System Information** — users ask questions about Osakidetza services (e.g., "how do I book an appointment?") and receive answers extracted from official public PDFs published by the health authority.

The system operates entirely with **free, no-cost APIs** — Google AI Studio provides the API key for the language model, and no paid services are required. It supports **English, Spanish, and Basque**, detecting the user's language automatically and responding in kind. Language detection runs on every user turn, so switching languages mid-session works seamlessly.

## 3. Architecture

> 📐 **Architecture diagram**: [`docs/architecture.png`](docs/architecture.png)

<!--
The ASCII diagram below is a fallback for plain-text viewers.
The PNG renders in rich Markdown viewers (Kaggle Writeup, GitHub).
-->
```text
User Message
     │
     ▼
┌─────────────────────────────────┐
│   Root ADK Agent (aita_lagun)   │
│   - before_agent_callback       │
│     (language detection)        │
│   - LLM routing via description │
└────┬────────────────────┬───────┘
     │                    │
     ▼                    ▼
┌──────────┐      ┌──────────────┐
│recordatorio│    │ info_salud   │
│(Reminder) │    │ (Health Info) │
├──────────┤      ├──────────────┤
│FunctionTool│    │ McpToolset   │
│(conv.    │    │ ─── stdio ── │
│confirm)  │    │              │
│           │    │  ┌─────────┐ │
│McpToolset │    │  │PDF Fast │ │
│ ── stdio ─┤    │  │MCP      │ │
│           │    │  │Server   │ │
│┌────────┐ │    │  │PyMuPDF  │ │
││Calendar│ │    │  │3 PDFs   │ │
││FastMCP │ │    │  └─────────┘ │
││Server  │ │    └──────────────┘
││Google  │ │
││Calendar│ │
││API     │ │
│└────────┘ │
└──────────┘
```

The architecture follows a clear separation of concerns:

- **Root ADK Agent** (`agents/agent.py`): An `Agent(name="aita_lagun")` that registers two sub-agents and a `before_agent_callback` for language detection. The LLM reads each sub-agent's `description` field and routes the user's intent accordingly.

- **Recordatorio Agent** (`agents/orchestrator.py`): An ADK sub-agent focused on medication reminders. It carries a `FunctionTool` wrapping the calendar creation function with conversational confirmation (the LLM asks the user for approval before calling the tool), plus an `McpToolset` connection to the Calendar MCP server.

- **InfoSalud Agent** (`agents/info_salud_agent.py`): An ADK sub-agent that answers health system questions. It uses `McpToolset` to connect to the PDF MCP server via stdio transport.

- **Calendar MCP Server** (`mcp_servers/calendar_mcp.py`): A FastMCP server exposing a `crear_evento_calendar` tool. It authenticates via Google service account and uses the Google Calendar API to create events.

- **PDF MCP Server** (`mcp_servers/pdf_mcp.py`): A FastMCP server exposing a `buscar_en_pdfs` tool. It reads three official Osakidetza PDFs using PyMuPDF and returns relevant snippets.

## 4. Technical Deep Dive

### ADK Multi-Agent System

The root agent uses `Agent(sub_agents=[...])` to declare its routing topology. Each sub-agent has a `description` field that the LLM reads to decide where to route:

```python
root_agent = Agent(
    name="aita_lagun",
    sub_agents=[recordatorio, info_salud_agent],
    before_agent_callback=_detect_language,
)
```

Language detection runs as a `before_agent_callback` that scans the user's first message for keywords in Basque ("gogoratu", "kaixo"), Spanish ("recuerda", "hola"), or English ("remind", "hello") and stores the result in `callback_context.state["lang"]`. The agent instruction then tells the LLM to respond in the detected language.

### MCP Protocol via FastMCP

Both MCP servers use `FastMCP` from the `mcp` library. Each server runs as a separate stdio subprocess. The ADK agents connect to them using `McpToolset(StdioConnectionParams(...))`:

```python
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=["-m", "mcp_servers.calendar_mcp"],
        ),
    ),
)
```

This approach means each server is independently testable, can be developed in isolation, and follows the MCP specification.

### Human-in-the-Loop Security

Calendar event creation uses conversational confirmation. The recordatorio agent's instruction tells the LLM to explicitly ask the user for confirmation before calling the `crear_evento_calendar` tool, and the user must approve in their language before the event is created. No personal health data is stored — the system reads only public PDFs and creates calendar events with medication names and times.

### Testing with Strict TDD

The project follows Strict TDD. All MCP tool functions are pure or mock-isolated and tested with `pytest`. The Calendar MCP tests mock `googleapiclient.discovery.build`, while the PDF MCP tests mock `fitz.open` to verify text extraction and query matching across multiple documents. In total, **39 unit tests at 91% coverage** cover all components.

## 5. Key Technical Decisions

| Decision | Chosen Approach | Alternative | Rationale |
|----------|----------------|-------------|-----------|
| **Agent Routing** | LLM routing via `description` | Keyword matching | Handles natural language variation, scales to more agents without routing code changes |
| **MCP Transport** | stdio (subprocess) | HTTP | Simpler setup, no port conflicts, ADK manages lifecycle. Best for local/free deployment |
| **Calendar Auth** | Google Service Account | OAuth 2.0 | No interactive browser required — works headlessly. Service account calendar sharing is straightforward for demo scope |
| **LLM Provider** | Google AI Studio (free API key) | Vertex AI | Free tier sufficient for demo and evaluation. No billing setup required |
| **PDF Source** | Local PyMuPDF on public PDFs | Web scraping | Deterministic, no network dependency, respects public document terms of use |
| **Test Approach** | Strict TDD with mocks | Integration-only | Catch logic errors fast. Fast feedback during development |

## 6. Demo

*A 4-minute video demonstration accompanies this submission.*

The video walks through:
- **0:00–0:30** — Problem context: elderly users, medication management, Osakidetza complexity
- **0:30–1:00** — Architecture diagram walkthrough
- **1:00–2:30** — Demo 1: "remind me Sintrom at 8am". The agent proactively asks about recurrence (daily/weekly/once) with three buttons, then requests conversational confirmation before creating a Google Calendar event with the correct RRULE
- **2:30–3:20** — Demo 2: "how do I book an Osakidetza appointment?" shows the PDF search returning structured public health information from official documents
- **3:20–3:40** — Demo 3: "gogoratu pastilla 8:00" in Basque. The agent detects Basque instantly AND knows 8am has passed, so it proactively schedules for tomorrow. Language detection + temporal awareness in one response
- **3:40–4:00** — Closing: concepts demonstrated (ADK Multi-Agent, MCP Server, Security Features, Antigravity, Deployability, Agent Skills)

## 7. The Build Journey

This project started as a set of plain Python prototypes — a simple class-based orchestrator with an `input()` loop, a calendar function returning `"event_simulated"`, and PDF file paths that didn't match the actual files on disk. The architecture diagram showed ADK, but the code delivered none of it.

The first major decision was to fully commit to Google ADK and the MCP protocol. We evaluated three approaches: a single agent with all tools, a custom base-agent orchestrator, and true sub-agent delegation with LLM routing. The last option won because it's the only one that demonstrates the multi-agent architecture the course teaches.

The most challenging parts were:

- **ADK authentication setup**: Getting the API key flow right required restructuring the environment configuration and understanding the AI Studio vs Vertex AI distinction. The ADK library reads `GOOGLE_API_KEY` for AI Studio, but the initial prototype set it as `GOOGLE_AI_STUDIO_API_KEY` — a mismatch that took several rounds of debugging to identify. The fix also required adding `GOOGLE_GENAI_USE_VERTEXAI=False` to prevent the ADK from trying to authenticate against Vertex AI, which would fail without a GCP project configured.

- **MCP subprocess lifecycle on Windows**: Stdio server connections needed careful path handling and timeout configuration. The ADK `McpToolset` abstraction handled most of this, but debugging connection issues required understanding subprocess I/O. On Windows, Python module paths use backslashes, so the initial `command="python"` with `args=["-m", "mcp_servers.calendar_mcp"]` failed because the subprocess couldn't resolve absolute paths when spawned from different working directories. The resolution was ensuring all MCP server file references use `os.path.join` with `os.path.dirname(__file__)` for path resolution.

- **LLM routing non-determinism**: The sub-agent `description` fields needed precise wording to reliably route medication vs health questions. Small wording changes produced different routing behavior — for example, changing "Use this agent for reminders" to "Medication reminder agent. Creates calendar events for medication reminders" shifted the routing accuracy from ~60% to ~90% in testing. The key insight was that descriptions must contain both the **domain** (medication) and the **action** (creates calendar events) to guide the LLM effectively without relying on stopwords or vague terms.

- **Circular import on entry point**: The initial `agents/__init__.py` imported from `agents/agent.py`, which caused a double-load when running `python -m agents.agent` (Python runs `__init__.py` first, then `agent.py` re-imports what `__init__.py` already loaded). The fix was removing the `agent.py` import from `__init__.py` and only exporting the sub-agent instances (`recordatorio`, `info_salud_agent`) that other modules need. A comment in `__init__.py` now documents this restriction to prevent regressions.

After resolving these, the implementation flowed predictably: MCP servers first (independently testable), then ADK agent definitions, then tests, then integration wiring. 39 unit tests at 91% coverage verify all components.

## 8. Concepts Demonstrated

| Course Concept | Where Demonstrated |
|---------------|-------------------|
| **ADK Multi-Agent System** | `agents/agent.py`: Root `Agent` with `sub_agents=[recordatorio, info_salud_agent]`, LLM routing via `description` fields |
| **MCP Server** | `mcp_servers/calendar_mcp.py` and `mcp_servers/pdf_mcp.py`: FastMCP servers exposing tools via stdio transport, consumed by ADK via `McpToolset` |
| **Antigravity** | Full project loaded in Antigravity desktop IDE: `agents/`, `mcp_servers/`, tests, and configuration visible in the editor |
| **Security Features** | Conversational confirmation via LLM instruction before calendar writes (proactive ask + final HITL); zero personal health data stored; only public PDFs accessed |
| **Agent Skills** | `skills/SKILL.md`: Non-executable skill-definition file documenting the reminder creation capability with recurrence support |
| **Deployability** | `pyproject.toml`, `requirements.txt`, `.env.example`: Standard Python project structure, installable with `pip install -r requirements.txt`, runnable via `python -m uvicorn app.main:app --port 8080` |

## 9. Limitations & Future Work

- **Time parsing** is handled by the LLM, which is flexible but not perfectly reliable for edge cases. A regex fallback or structured time extraction would improve robustness.
- **Calendar integration** requires a Google service account. For production deployment, OAuth with token refresh would handle multi-user scenarios better.
- **Language detection** uses keyword heuristics re-evaluated on every user turn. The system handles EN/ES/EU switching mid-session, but short follow-ups (e.g., "Egunero") rely on the previous turn's detection.
- **Deployment** to Cloud Run or similar platforms would make the assistant accessible without local setup. The current ADK runner is designed for local/CLI interaction.
- **Video content** and media gallery screenshots are prepared but submitted separately with the Kaggle Writeup.

---

*Built with Google ADK, FastMCP, PyMuPDF, and Python. 100% free, no paid APIs.*
