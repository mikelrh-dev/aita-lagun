# Visual Design Assets — Specification

Three new domains: FastAPI chat backend, chat frontend, integration setup.

---

## 1. FastAPI Chat Backend

### Purpose

Expose the existing ADK agent as a REST API so a browser-based chat UI can interact with it.

### Requirements

#### R1: Chat Endpoint

The system MUST expose `POST /api/chat` accepting `{"message": string}` and returning `{"reply": string}`.

- **Scenario: Happy path — agent responds**
  - GIVEN the backend is running with all MCP subprocesses
  - WHEN a POST to `/api/chat` with `{"message": "Hello"}` is sent
  - THEN the response SHALL have a `200` status and `{"reply": "..."}`
  - AND the reply SHALL contain the ADK agent's response

- **Scenario: Empty message**
  - WHEN a POST to `/api/chat` with `{"message": ""}` is sent
  - THEN the response MUST be `422 Unprocessable Entity`

#### R2: MCP Subprocess Management

The backend MUST start the calendar and PDF MCP servers as subprocesses on launch and SHUTDOWN them on exit.

- **Scenario: Servers start with backend**
  - GIVEN the FastAPI server starts
  - THEN both `mcp_servers/calendar_mcp.py` and `mcp_servers/pdf_mcp.py` SHALL be running as subprocesses within 5 seconds

- **Scenario: Servers clean up on shutdown**
  - GIVEN the FastAPI server is shutting down
  - THEN all MCP subprocesses MUST be terminated

#### R3: CORS

The system MUST enable CORS for `http://localhost:*` origins.

- **Scenario: Frontend origin allowed**
  - GIVEN a frontend at `http://localhost:5500`
  - WHEN it sends a POST to `/api/chat`
  - THEN the response SHALL include `Access-Control-Allow-Origin: *`

#### R4: Chat History

The system MUST use `InMemorySessionService` so conversation context persists across turns within a session.

- **Scenario: Context carried across turns**
  - GIVEN a user sends "My name is Jon"
  - WHEN they send "What is my name?" in a subsequent request
  - THEN the agent SHALL reply with "Jon"

#### R5: Environment Configuration

The backend MUST load `.env` for `GEMINI_API_KEY`, `GOOGLE_SERVICE_ACCOUNT`, and `GOOGLE_CALENDAR_ID`.

- **Scenario: Missing env variable**
  - GIVEN `GEMINI_API_KEY` is not set in `.env`
  - WHEN the server starts
  - THEN it MUST log a clear error and SHUTDOWN

---

## 2. Chat Frontend

### Purpose

Single-page chat UI that matches the existing Stitch design system (dark theme, teal primary, Hanken Grotesk + Atkinson Hyperlegible Next).

### Requirements

#### R6: Chat Bubble Layout

The UI MUST render user messages right-aligned and assistant messages left-aligned.

- **Scenario: User message alignment**
  - GIVEN the user sends "Hello"
  - THEN the message bubble SHALL appear on the right side with a distinct user color

- **Scenario: Assistant message alignment**
  - GIVEN the agent replies "How can I help?"
  - THEN the bubble SHALL appear on the left side with a different background color

#### R7: Language Badge

The UI SHOULD display a badge showing the detected language (EN / ES / EU).

- **Scenario: Badge updates per message**
  - GIVEN the last response was in Spanish
  - THEN a badge reading "ES" SHALL be visible near the response

#### R8: Loading Indicator

The UI MUST show a loading indicator while waiting for the API response.

- **Scenario: Loading shown during request**
  - GIVEN the user sends a message
  - WHEN the API request is pending
  - THEN a spinner or "..." SHALL be visible and the send button SHALL be disabled

#### R9: Markdown Rendering

The UI MUST render Markdown in assistant messages (for PDF-extracted health info formatting).

- **Scenario: Bold text rendered**
  - GIVEN the agent response contains `**bold**`
  - THEN the UI SHALL render it as `<strong>`bold`</strong>`

#### R10: Responsive Design

The UI MUST work on viewports from 375px to 1920px width.

- **Scenario: Mobile layout**
  - GIVEN a 375px-wide viewport
  - THEN the chat SHALL fill the full width with readable font sizes

- **Scenario: Desktop layout**
  - GIVEN a 1280px-wide viewport
  - THEN the chat container SHALL be centered with a max-width of 800px

#### R11: Design System Match

The UI MUST use the project's design tokens: dark background (`#0f172a`), teal accent (`#2dd4bf`), Hanken Grotesk for headings, Atkinson Hyperlegible Next for body.

- **Scenario: Visual inspection**
  - GIVEN the page loads
  - THEN the computed styles SHALL match the defined tokens

---

## 3. Integration & Dev Setup

### Purpose

Scripts and documentation to run the full stack locally with one command.

### Requirements

#### R12: Single Start Command

The project MUST provide a command (Makefile target or script) that starts both the FastAPI backend and the frontend.

- **Scenario: Backend starts on 8080**
  - GIVEN the developer runs `python scripts/run_dev.py` (or equivalent)
  - THEN the FastAPI server SHALL listen on `http://localhost:8080`
  - AND the frontend SHALL be served or accessible

- **Scenario: Frontend served**
  - GIVEN the dev server is running
  - WHEN a browser navigates to `http://localhost:8080` (or `http://localhost:5500` for dev server)
  - THEN the chat UI SHALL load

#### R13: .env Documentation

The `.env` variables MUST be documented in `README.md` with example values.

- **Scenario: README contains env table**
  - GIVEN a new developer reads `README.md`
  - THEN they SHALL find a table with all required env vars, descriptions, and example values

#### R14: Dependency Installation

The setup SHALL include a `pip install -r requirements.txt` step (with FastAPI, uvicorn added to requirements).

- **Scenario: New clone setup**
  - GIVEN a fresh clone
  - WHEN `pip install -r requirements.txt && python scripts/run_dev.py` is run
  - THEN the full stack SHALL start without import errors
