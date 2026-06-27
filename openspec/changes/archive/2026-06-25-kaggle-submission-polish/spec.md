# Spec: Kaggle Submission Polish

**Change:** `kaggle-submission-polish`  
**Track:** Agents for Good  
**Status:** Proposed  
**Date:** 2026-06-25

---

## 1. Problem Statement

Kaggle's evaluation criteria explicitly require:
- "Code should contain comments pertinent to implementation, design and behaviors"
- "README.md file explaining the problem, solution, architecture, instructions for setup, and relevant diagrams"

Current state:
- README: 25 lines, minimal setup info, no architecture explanation
- Code: Zero multi-line docstrings or block comments
- No Dockerfile or deployment configuration
- WRITEUP.md lacks embedded architecture diagram

This spec defines the polish required to meet Kaggle's documentation and code quality standards.

---

## 2. Requirements by File

### 2.1 README.md (Complete Rewrite)

**Current:** 25 lines, minimal content  
**Target:** ~200 lines, comprehensive guide

**Requirements:**

1. **Badges Section**
   - Python version badge (3.10+)
   - pytest coverage badge (if available)
   - License badge (if applicable)

2. **Problem Statement** (2-3 sentences)
   - Elderly users in Barakaldo forget medication
   - Osakidetza information is hard to navigate
   - Multi-language support (en/es/eu)

3. **Solution Overview** (3-4 sentences)
   - Multi-agent ADK assistant
   - Medication reminders with HITL confirmation
   - Health information from official PDFs

4. **Quick Start** (Step-by-step)
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Configure API keys
   python -m agents.agent
   ```

5. **Architecture** (with diagram reference)
   - Root ADK agent with sub-agents
   - MCP servers (Calendar, PDF)
   - Language detection callback
   - Link to `docs/architecture.png`

6. **Setup Guide** (Detailed)
   - Python version requirement
   - Virtual environment setup
   - `.env` configuration with all required vars
   - Google Calendar service account setup
   - Running the agent

7. **Testing**
   - `pytest` command
   - Coverage report generation
   - Test structure explanation

8. **Troubleshooting**
   - "API key not set" error
   - "Module not found" error
   - "PDF not found" error
   - "Calendar permission denied" error

9. **Contributing**
   - How to add new agents
   - How to add new MCP servers
   - Code style (PEP 8, type hints)
   - Test requirements

10. **License** (if applicable)

**Acceptance Criteria:**
- New user can clone, install, configure, and run in <10 minutes
- All error messages in troubleshooting section are accurate
- Architecture diagram link works

---

### 2.2 Code Comments (All Source Files)

**Files to modify:**
- `agents/agent.py`
- `agents/orchestrator.py`
- `agents/recordatorio_agent.py`
- `agents/info_salud_agent.py`
- `agents/__init__.py`
- `mcp_servers/calendar_mcp.py`
- `mcp_servers/pdf_mcp.py`
- `mcp_servers/__init__.py`

**Requirements:**

1. **Module Docstrings** (All files)
   - Purpose of the module
   - Key classes/functions
   - Dependencies

2. **Class Docstrings** (All public classes)
   - PEP 257 format
   - Purpose, key methods, usage example

3. **Function Docstrings** (All public functions)
   - PEP 257 format
   - Args: parameter types and descriptions
   - Returns: return type and description
   - Raises: exceptions and when they occur

4. **Inline Comments** (Non-obvious logic)
   - Language detection heuristics
   - HITL confirmation flow
   - MCP protocol details
   - Security considerations

5. **Security Notes**
   - Comment on `require_confirmation=True`
   - Comment on no PHI storage
   - Comment on public PDF usage

**Acceptance Criteria:**
- `pyright` or `mypy` shows no "missing docstring" errors
- All public APIs have complete docstrings
- Inline comments explain "why", not "what"

---

### 2.3 Dockerfile (New File)

**Requirements:**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Entry point
CMD ["python", "-m", "agents.agent"]
```

**Acceptance Criteria:**
- `docker build -t aita-lagun .` succeeds
- Container runs with `docker run`
- Compatible with Cloud Run deployment

---

### 2.4 .dockerignore (New File)

**Requirements:**

```
__pycache__
.git
.env
tests/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.md
!README.md
openspec/
```

**Acceptance Criteria:**
- Docker build excludes unnecessary files
- Image size is minimal

---

### 2.5 WRITEUP.md (Polish)

**Current:** 175 lines, solid content  
**Target:** ~200 lines, embedded diagram

**Requirements:**

1. **Embed Architecture Diagram**
   - Add reference to `docs/architecture.png`
   - Add markdown image syntax with alt text

2. **Expand Build Journey**
   - Add more detail about challenges faced
   - Add lessons learned

3. **Concepts Demonstrated Table**
   - Add file references for each concept
   - Add "where demonstrated" column

**Acceptance Criteria:**
- Architecture diagram renders in Kaggle writeup
- Build Journey section has concrete examples

---

### 2.6 skills/SKILL.md (Refine)

**Current:** 9 lines, minimal  
**Target:** ~30 lines, proper format

**Requirements:**

1. **Frontmatter**
   ```yaml
   ---
   name: create_reminder
   description: Creates medication reminder with human confirmation
   version: 1.0
   ---
   ```

2. **Expanded Description**
   - Purpose
   - Input parameters
   - Output format
   - Security notes

3. **Usage Examples**
   - Example conversation flow
   - Confirmation prompt example

**Acceptance Criteria:**
- Skill follows SKILL.md template format
- Security notes are prominent

---

### 2.7 .env.example (Complete)

**Current:** Partial  
**Target:** All required variables documented

**Requirements:**

```bash
# Google AI Studio API Key
GOOGLE_AI_STUDIO_API_KEY=your_api_key_here

# Google Calendar Service Account JSON (path or inline JSON)
GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON=/path/to/service-account.json

# Google Calendar ID (default: primary)
GOOGLE_CALENDAR_ID=primary
```

**Acceptance Criteria:**
- All env vars used in code are documented
- Comments explain each variable

---

## 3. Non-Functional Requirements

1. **Language:** All artifacts in English (per domain contract)
2. **Style:** Python PEP 8, PEP 257 docstrings
3. **Security:** No secrets in code, .env.example safe to commit
4. **Maintainability:** Comments explain "why", not "what"

---

## 4. Constraints

1. **Line Budget:** Total changed lines ≤ 400
2. **No Breaking Changes:** Existing functionality unchanged
3. **No New Dependencies:** Use existing `requirements.txt`
4. **No New Features:** Polish only, no new agents/MCP servers

---

## 5. Risks

| Risk | Mitigation |
|------|------------|
| 400-line budget exceeded | Monitor during task breakdown; split into chained PRs if needed |
| README too long | Focus on clarity; use code blocks for examples |
| Dockerfile complexity | Keep minimal; use slim base image |

---

## 6. Acceptance Criteria (Overall)

1. Kaggle documentation requirements met (README + code comments)
2. Dockerfile builds successfully
3. All tests pass after changes
4. No regression in existing functionality
5. Total changed lines ≤ 400 (or chained PRs activated)

---

## 7. Next Steps

1. `sdd-design`: Technical design for each file modification
2. `sdd-tasks`: Break into implementable tasks
3. `sdd-apply`: Implement tasks in batches
4. `sdd-verify`: Validate against specs
5. `sdd-archive`: Archive completed change