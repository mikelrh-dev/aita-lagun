# Proposal: Brutalist UI Redesign

## Intent

Current chat UI uses teal glassmorphism, rounded bubbles, gradients, and a logo SVG — polished but visually complex and difficult to distinguish from other Kaggle entries. Redesign to an "Accessible Brutalist" aesthetic: flat, high-contrast, zero ornamentation, while maintaining large text and clear affordances for elderly users.

## Scope

### In Scope
- Split monolithic `index.html` into `index.html` (structure), `styles.css` (all styles), `app.js` (JS behavior)
- Zero border-radius, shadows, gradients, or glassmorphism on all elements
- Messages rendered as flat text blocks separated by solid horizontal lines (no bubbles)
- Carbon/black background (`#1a1a1a`), off-white text (`#f0f0f0`), red accent (`#e63946`)
- Remove SVG logo, remove font-size toggle, simplify header to text-only
- Large sans-serif for message text (18-20px), monospace for timestamps
- Keep suggestion chips with new styling
- Keep existing JS fetch logic and rendering pipeline — only change DOM injection

### Out of Scope
- Backend changes to `app/main.py`, `agents/`, `mcp_servers/`, `tests/`, `pyproject.toml`, `requirements.txt`, `Dockerfile`
- Any commit or push
- MCP metadata display in chat flow
- Functional behavior changes (language detection, markdown rendering, API calls)

## Capabilities

### New Capabilities
- `chat-interface`: Visual specification for the chat UI component — layout, typography, color system, responsive breakpoints, and accessibility requirements

### Modified Capabilities
None — pure visual redesign with no spec-level behavior changes.

## Approach

| Layer | Change |
|-------|--------|
| `index.html` | Strip to bare HTML skeleton. Remove inline styles, logo SVG, font-size toggle. Keep semantic structure, `role`/`aria-*` attributes, suggestion chips |
| `styles.css` | New file. Carbon/off-white/red palette. Zero border-radius. Flat header with heavy bold title. Messages separated by `<hr>` lines. Monospace timestamps. High-contrast focus indicators |
| `app.js` | New file. Same fetch/promise chain from existing JS. Same `addMessage`, `renderMarkdown`, `detectLanguage`, `toggleLoading`. Remove size-toggle logic. Update DOM class names |

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app/static/index.html` | Modified | Stripped to skeleton, removed inline CSS/JS |
| `app/static/styles.css` | New | All visual design |
| `app/static/app.js` | New | All JS behavior extracted |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Elderly users struggle with high-contrast brutalist layout | Low | Keep 18-20px body text, clear affordances, focus indicators, skip pure black/white extremes |
| Visual regression on suggestion chips input flow | Low | Keep same JS event handlers, only restyle CSS |
| Lost accessibility (ARIA, keyboard, screen reader) during strip-down | Medium | Preserve all `role`, `aria-*`, semantic HTML — audit in verify phase |

## Rollback Plan

Restore original `app/static/index.html` from git and delete `styles.css` + `app.js`. All changes are contained within `app/static/`.

## Dependencies

- None. Self-contained frontend-only change.

## Success Criteria

- [ ] `index.html` contains zero inline styles — all visual design in `styles.css`
- [ ] All border-radius values are zero — no rounded corners on any element
- [ ] No shadows, gradients, or `backdrop-filter` in any CSS rule
- [ ] Font-size toggle and logo SVG removed from header
- [ ] Messages render as flat blocks separated by `<hr>` — no bubble shapes
- [ ] App maintains accessible contrast ratios and keyboard navigation
- [ ] Chat sends/receives messages identically to current behavior
