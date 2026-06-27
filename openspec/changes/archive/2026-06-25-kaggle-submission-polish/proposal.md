# Proposal: Kaggle Submission Polish

## Intent

Maximize Kaggle evaluation score by polishing existing code and documentation. No new functionality. Current estimated score: 64/100.

## Scope

### In Scope
- README.md complete rewrite (currently 25 lines)
- Add code comments to all source files (Kaggle explicit requirement)
- Dockerfile + .dockerignore for Cloud Run deployability
- WRITEUP.md polish with architecture diagram reference
- skills/SKILL.md refinement
- .env.example cleanup

### Out of Scope
- YouTube video (user handles separately)
- New agents, MCP servers, or features
- Testing changes (existing 18 tests pass)
- Architecture changes

## Capabilities

### New Capabilities
None — pure polish pass, no new features.

### Modified Capabilities
None — no spec-level behavior changes.

## Approach

Single coordinated polish pass. All changes are additive (comments, docs, new files) or non-breaking (README rewrite). Estimated total: ~325-375 lines changed.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `README.md` | Modified | Complete rewrite with setup guide, architecture, troubleshooting, badges |
| `agents/agent.py` | Modified | Add code comments (design decisions, routing) |
| `agents/orchestrator.py` | Modified | Add code comments (orchestration logic) |
| `agents/recordatorio_agent.py` | Modified | Add code comments |
| `agents/info_salud_agent.py` | Modified | Add code comments |
| `agents/__init__.py` | Modified | Add module-level docstring |
| `mcp_servers/calendar_mcp.py` | Modified | Add code comments (MCP protocol, security) |
| `mcp_servers/pdf_mcp.py` | Modified | Add code comments (MCP protocol, security) |
| `mcp_servers/__init__.py` | Modified | Add module-level docstring |
| `Dockerfile` | New | Container config for Cloud Run deployment |
| `.dockerignore` | New | Standard Docker exclusions |
| `WRITEUP.md` | Modified | Embed architecture diagram reference, polish sections |
| `skills/SKILL.md` | Modified | Refine format and content |
| `.env.example` | Modified | Document all variables with descriptions |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Approaches 400-line review budget | Medium | Monitor during task breakdown; chain PRs if needed |
| README too verbose vs Kaggle conciseness expectations | Low | Balance — completeness for judges, skimmable for devs |

## Rollback Plan

All changes are additive or README-only. Rollback via `git checkout` on any problematic file. No schema, API, or behavioral changes to revert.

## Dependencies

None.

## Success Criteria

- [ ] All source files have explanatory comments in every module
- [ ] README meets Kaggle documentation expectations (setup, architecture, troubleshooting)
- [ ] Dockerfile produces a working container image
- [ ] .env.example documents every configuration variable with purpose
- [ ] WRITEUP.md includes a clear architecture diagram reference
- [ ] All 18 existing tests still pass
