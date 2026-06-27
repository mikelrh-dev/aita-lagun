# Proposal: Visual Design Assets

## Intent

aita-lagun is CLI-only with zero visual presence. Kaggle evaluators cannot see the UX, design quality, or value proposition at a glance. This change creates the visual assets needed for a professional capstone submission: mockup screens, a design system document, and a polished landing page.

## Scope

### In Scope
- 3 Stitch-generated mockup screens (chat interface, mobile conversation, feature showcase)
- DESIGN.md — export of existing Stitch design system into repo
- Web application (local first):
  - FastAPI backend wrapping the ADK agent
  - Chat frontend (HTML/CSS/JS) using Stitch design tokens
  - MCP servers embedded as subprocesses
  - Local testing with `uvicorn`
- Future: deploy to Cloud Run (optional, post-submission)

### Out of Scope
- Static landing page (replaced by functional web app)
- Multiple page variants
- User authentication/OAuth
- Production-grade scalability

## Capabilities

### New Capabilities
None — purely visual presentation. No new system capabilities introduced.

### Modified Capabilities
None — no existing spec-level behavior changes.

## Approach

| Deliverable | Tool | Method |
|-------------|------|--------|
| 3 mockup screens | Stitch | Generate via `stitch_generate_screen_from_text`, export PNG |
| DESIGN.md | Manual export | Extract tokens from existing Stitch design system |
| Landing page | Handcrafted HTML/CSS | Single responsive page ~400 lines, dark theme with design tokens |
| Deployment | GitHub Pages | Push to repo root or `docs/`, enable Pages in repo settings |

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `docs/` | New | DESIGN.md, landing page files, screenshots |
| `openspec/changes/visual-design-assets/` | New | proposal.md |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Stitch screen quality needs iteration | Medium | Iterate prompts, regenerate as needed |
| GitHub Pages setup friction | Low | Document steps in DESIGN.md |
| Landing page exceeds 400-line budget | Medium | Keep as single scroll page, defer animations |

## Rollback Plan

Additive change — new files only, no existing code modified. Remove `docs/` and disable GitHub Pages to revert.

## Dependencies

- Stitch project `13558646535241964762` already exists with complete design system
- GitHub repository with Pages capability

## Success Criteria

- [ ] 3 Stitch screens generated and committed to repo
- [ ] DESIGN.md documents all design tokens from Stitch
- [ ] Landing page renders correctly on mobile and desktop
- [ ] Landing page hosted and accessible via GitHub Pages
- [ ] Landing page HTML stays under 400 lines total

## Proposal Question Round

Before finalizing, consider these questions to sharpen the proposal:

1. **Landing page depth**: Should the page be a single hero/feature scroll, or include a dedicated "architecture" section showing the multi-agent system?
2. **Screenshot format**: PNG exports from Stitch, or should we capture additional real CLI screenshots to show the actual working tool?
3. **GitHub Pages branch**: Deploy from `main` (root/docs/) or a separate `gh-pages` branch?
4. **Kaggle submission link**: Does the landing page URL need to be included in the Kaggle submission notebook, or is this purely for the GitHub repo README?
