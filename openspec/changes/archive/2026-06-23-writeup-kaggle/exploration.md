# Exploration: Kaggle Writeup for Aita-Lagun

## Current Writeup State

The existing `WRITEUP_OUTLINE.md` is a bare skeleton (17 lines) with 5 section headers and minimal notes:

- **1. Problem**: Empty placeholder
- **2. Solution**: Single-line: "Multi-agent assistant for medication reminders with human confirmation."
- **3. Architecture**: References `docs/architecture.png` — no text description
- **4. Demo**: "4-min video in English, with 10s Basque clip subtitled."
- **5. Concepts**: Lists "ADK, MCP, Security" — no elaboration

**Assessment**: The outline is insufficient for a Kaggle writeup. It lacks problem statement content, architectural narrative, demo details, concept explanations, and the required "build journey" section. Judging criteria weight Technical Implementation (50 pts) and Writeup (10 pts) heavily.

## Kaggle Requirements (from kaggle.md)

| Requirement | Detail |
|-------------|--------|
| Max words | 2,500 |
| Track | Agents for Good (this project) |
| Required concepts (≥3) | ADK Multi-agent, MCP Server, Security, Antigravity (video), Deployability (video), Agent skills (code/video) |
| Evaluation Category 1 (30pt) | Core Concept & Value (10pt), Video (10pt), Writeup (10pt) |
| Evaluation Category 2 (70pt) | Technical Implementation (50pt), Documentation (20pt) |
| Attachments | Media Gallery, Public Video (≤5 min YouTube), Public Project Link (GitHub) |

## Project Implementation (current state)

The codebase is fully implemented with real ADK + MCP integration:

- **agents/agent.py** — Root ADK Agent with `before_agent_callback` for multi-language detection (en/es/eu), LLM-driven sub-agent delegation
- **agents/orchestrator.py** — `recordatorio` sub-agent with `FunctionTool(crear_evento_calendar, require_confirmation=True)` for human-in-the-loop, `McpToolset` to calendar MCP via stdio
- **agents/recordatorio_agent.py** — Tool function calling Google Calendar API (service account)
- **agents/info_salud_agent.py** — `info_salud` sub-agent with `McpToolset` to PDF MCP via stdio
- **mcp_servers/calendar_mcp.py** — FastMCP server, tool `crear_evento_calendar(medication, time, date)` using Google Calendar API
- **mcp_servers/pdf_mcp.py** — FastMCP server, tool `buscar_en_pdfs(query)` searching 3 Osakidetza PDFs with PyMuPDF
- **tests/unit/** — 17+ unit tests (PDF MCP: 4, Calendar MCP: 3, Agent definitions: 10+)
- **requirements.txt** — `google-adk`, `mcp`, `google-genai`, `PyMuPDF`, `pytest`, etc.
- **docs/architecture.png** — Architecture diagram exists
- **Data**: 3 real public PDF files from Osakidetza

## Key Technical Decisions Worth Highlighting

1. **LLM-driven sub-agent routing** (not keyword matching) — the `description` field on each sub-agent lets the LLM route by intent
2. **FastMCP with stdio transport** — each MCP server runs as an independent process, `McpToolset` handles lifecycle
3. **Human-in-the-loop** via `FunctionTool(require_confirmation=True)` — ADK's built-in confirmation flow, no raw `input()`
4. **Multi-language support** (en/es/eu) — `before_agent_callback` detects language from keywords, LLM responds in the same language
5. **100% free stack** — Google AI Studio API key (`GOOGLE_API_KEY`), no Vertex AI, no paid APIs
6. **Service account auth** for Google Calendar — no interactive OAuth required for demo
7. **Zero personal data** — only public PDFs, no PHI stored, calendar writes require explicit confirmation
8. **TDD with pytest** — tests for MCP servers, agent definitions, tool signatures

## Gaps in Current Outline

### Critical Missing Sections
- **Problem Statement**: The human problem (elderly in Barakaldo, medication adherence, health system navigation)
- **Why multi-agent?**: Why agents uniquely solve this vs. a simple chatbot
- **Architecture narrative**: Text description of the flow, not just a diagram reference
- **Concepts demonstrated**: Deep-dive on ADK multi-agent, MCP protocol, security features
- **The Build journey**: How it was built, challenges, evolution from prototypes to ADK
- **Track rationale**: Why "Agents for Good" fits this project
- **Technical decisions section**: With tradeoffs and rationale
- **Limitations / Future work**: Honest assessment

### Content That Exists But Needs Repurposing
- `Entendiendo-el-Capstone.md` — Detailed spec in Spanish, good source material
- `README.md` — Good summary, 25 lines
- `VIDEO_SCRIPT.md` — Rough 4-min timing, needs fleshing out
- Archived `proposal.md` and `design.md` — Architecture decisions, tradeoffs, rationale

### Content That Needs Creation
- Full 2,500-word writeup from scratch
- Completed video script (the video content goes in media gallery, but mentioned in writeup)
- GitHub public repo setup
- Media gallery images (screenshots, architecture diagram)

## Suggested Writeup Structure

| Section | Approx Words | Content |
|---------|-------------|---------|
| **1. Problem Statement** | 250 | Elderly in Barakaldo, medication adherence (Sintrom), Osakidetza system complexity, multi-language need (en/es/eu), why it matters |
| **2. Solution Overview** | 200 | Aita-Lagun as multi-agent conversational assistant, track alignment (Agents for Good), core capabilities, 100% free |
| **3. Architecture** | 400 | Multi-agent ADK flow diagram description, root agent → sub-agent routing, MCP servers (stdio/FastMCP), data flow, language detection callback |
| **4. Technical Deep Dive** | 600 | ADK multi-agent (Agent class, sub_agents, LLM routing), MCP servers (FastMCP protocol, tool definitions), Security features (HITL via require_confirmation, no PHI, public PDFs only), Multi-language (before_agent_callback), Calendar integration (service account, no OAuth), Testing strategy (TDD, pytest, unit tests) |
| **5. Key Technical Decisions** | 300 | LLM routing vs keyword matching, FastMCP stdio vs HTTP, Service account vs OAuth, AI Studio key vs Vertex AI, decision tradeoffs with rationale |
| **6. Demo** | 200 | References YouTube video (4 min), highlights: reminder flow with confirmation, Osakidetza PDF query, Basque language support |
| **7. The Build Journey** | 300 | Starting from plain Python prototypes, adopting ADK architecture, implementing MCP servers, adding tests, challenges encountered (ADK API key auth, MCP stdio lifecycle, LLM routing non-determinism) |
| **8. Concepts Demonstrated** | 200 | Table mapping course concepts to implementation: ADK (agents/agent.py), MCP (mcp_servers/), Security (HITL in orchestrator.py), Antigravity (video), Deployability (video), Agent skills (.env.example shows Agents CLI readiness) |
| **9. Limitations & Future Work** | 100 | Simulated time parsing, Calendar service account dependency, keyword-based language detection, potential for Cloud Run deployment |
| **Total** | ~2,550 | (trim to 2,500) |

## What Needs Creation vs Already Exists

| Item | Status | Action |
|------|--------|--------|
| Problem statement content | Missing | Write from scratch |
| Solution narrative | Partial | Expand from README |
| Architecture text | Missing | Write from codebase knowledge |
| Technical deep-dive | Missing | Extract from design.md + code |
| Key technical decisions | Partial | In archived design.md, need writeup adaptation |
| Demo section | Missing | Will reference video |
| Build journey | Missing | Reconstruct from archived explore/proposal/design |
| Concepts table | Missing | Create from kaggle.md requirements |
| GitHub repo | Missing | Create public repo |
| YouTube video | Missing | Record per VIDEO_SCRIPT |
| Video script improvements | Rough | Expand from 8 lines to proper script |
| Media gallery images | Missing | Architecture diagram exists, need screenshots |
| Final writeup submission | Missing | Full ~2,500 word document |

## Ready for Proposal

**Yes.** The exploration reveals a clear path forward:
- The codebase is complete and working
- The writeup requirements are well-defined
- The outline needs substantial expansion
- Content sources exist across multiple documents (code, spec, design decisions)
- The main work is synthesis: extracting key points from code/docs and structuring them into a compelling 2,500-word narrative
