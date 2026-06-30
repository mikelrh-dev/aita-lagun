# Chat Interface Specification

## Purpose

Visual, layout, accessibility, and architecture requirements for the Aita-Lagun chat interface — "Accessible Brutalist" aesthetic. Scoped to `app/static/` only.

## Requirements

### Requirement: Color Palette

Flat, high-contrast palette. Zero border-radius, shadows, gradients, glassmorphism.

| Token | Value |
|-------|-------|
| `--bg-primary` | `#1a1a1a` |
| `--bg-secondary` | `#222222` |
| `--text-primary` | `#f0f0f0` |
| `--text-secondary` | `#a0a0a0` |
| `--accent` | `#e63946` |
| `--border` | `#333333` |

#### Scenario: Zero decorative effects
- GIVEN any element — WHEN inspecting computed styles — THEN `border-radius` MUST be `0` AND `box-shadow`, `text-shadow`, gradient `background-image`, `backdrop-filter` MUST be absent.

### Requirement: Typography

Body sans-serif 18px min. Timestamps monospace. No font-size toggle.

| Token | Value |
|-------|-------|
| `--font-body` | `'Helvetica Neue', Arial, sans-serif` |
| `--font-mono` | `'Courier New', Courier, monospace` |
| `--font-size-body` | `18px` |
| `--line-height` | `1.6` |

#### Scenario: Minimum font size
- GIVEN body text — WHEN measuring — THEN font-size MUST be ≥ 18px.

#### Scenario: No toggle
- GIVEN the page — WHEN inspecting header — THEN no font-size control SHALL exist.

### Requirement: Message Display

Flat blocks separated by `<hr>`. No bubbles, backgrounds, or rounded containers.

#### Scenario: Flat blocks
- GIVEN multiple messages — THEN each MUST have `<hr>` above (`border-top: 1px solid #333`) and `padding: 16px 0` with no background.

#### Scenario: Sender metadata
- GIVEN a message — THEN sender bold (700), timestamp monospace secondary-color, body in base font below.

### Requirement: Header

Text-only. No logo, SVG, or images. Title 32px bold, subtitle 16px.

#### Scenario: No logo
- GIVEN page loads — WHEN inspecting header — THEN no `<svg>`, `<img>`, or logo SHALL exist.

### Requirement: Suggestion Chips

Preserved with restyled appearance.

#### Scenario: Restyled
- GIVEN chips displayed — THEN `border: 1px solid #333`, `background: #222`, `color: #f0f0f0`, `border-radius: 0`. Click handlers SHALL NOT change.

### Requirement: Responsive Layout

| Breakpoint | Container max-width |
|------------|-------------------|
| ≥ 1024px | 720px, centered |
| 768–1023px | full + 32px padding |
| < 768px | full + 16px padding |

#### Scenario: Width adapts
- GIVEN viewport resized across breakpoints — THEN container width MUST change without horizontal overflow.

### Requirement: Accessibility

WCAG 2.1 AA contrast. Visible focus indicators.

#### Scenario: Contrast
- GIVEN palette applied — WHEN measuring `#f0f0f0`/`#1a1a1a` — THEN ratio MUST exceed 4.5:1. `#e63946`/`#1a1a1a` MUST exceed 3:1.

#### Scenario: Focus
- GIVEN keyboard tabbing — THEN each focusable element MUST show `outline: 2px solid #e63946` `outline-offset: 2px`.

### Requirement: Three-File Architecture

| File | Role |
|------|------|
| `index.html` | Structure, semantic attributes, `role`/`aria-*` |
| `styles.css` | All visual CSS — zero inline styles |
| `app.js` | All JS behavior extracted from original |

#### Scenario: No inline CSS
- GIVEN rendered page — WHEN checking inline `style` or `<style>` — THEN none SHALL exist.

#### Scenario: Backend untouched
- GIVEN implementation done — THEN `app/main.py`, `agents/`, `mcp_servers/`, `tests/` SHALL be unmodified.

### Requirement: Rollback

Revert by restoring `index.html` from git and deleting `styles.css` + `app.js`.

#### Scenario: Full revert
- GIVEN redesign deployed — WHEN `git checkout -- app/static/index.html` and removing CSS/JS files — THEN chat functions identically to pre-change state.

### Requirement: Behavioral Preservation

Message fetch, markdown rendering, language detection, API calls — all MUST behave identically.

#### Scenario: Flow unchanged
- GIVEN user submits a message — THEN fetch pipeline, response handling, DOM rendering MUST produce identical functional output.

### Out of Scope

- Backend: `app/main.py`, `agents/`, `mcp_servers/`, `tests/`
- Build: `pyproject.toml`, `requirements.txt`, `Dockerfile`
- Behavior: language detection, markdown, API handlers, MCP metadata
- Git: no commit or push
