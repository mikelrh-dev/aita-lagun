# Tasks: Brutalist UI Redesign

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~550–710 |
| 400-line budget risk | High |
| Chained PRs recommended | No |
| Suggested split | Single write (no git — file-only delivery per constraint) |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: High

## Phase 1: Foundation — CSS Design System

- [x] 1.1 Create `app/static/styles.css` with `:root` custom properties (`--bg-primary`, `--accent`, etc.), zero border-radius/shadows/gradients
- [x] 1.2 Add layout rules: `.app` flex column full viewport, `.chat-messages` scroll, `.input-area` sticky bottom
- [x] 1.3 Style header: flat dark bg, `.app-title` 32px bold `--accent`, `.app-subtitle` 16px secondary color
- [x] 1.4 Style messages: flat `.entry` blocks with `padding: 12px 0`, `<hr>` separator via `border-top: 1px solid var(--border)`, timestamps `--font-mono` secondary color
- [x] 1.5 Style input area: `--surface-dim` background, textarea no border-radius, send button `--accent` bg
- [x] 1.6 Style empty state + suggestion chips: centered flex, chips `border: 1px solid var(--border)` no border-radius
- [x] 1.7 Add responsive breakpoints: ≥1024px (720px), 768–1023px (full+32px pad), <768px (full+16px pad)
- [x] 1.8 Add `focus-visible` outlines: `2px solid var(--accent)` with `outline-offset: 2px`
- [x] 1.9 Style loading indicator: three dots animation without border-radius, accent color

## Phase 2: Core — JS Extraction

- [x] 2.1 Create `app/static/app.js` with same IIFE pattern, remove `sizeToggle` listener + DOM ref
- [x] 2.2 Adapt `addMessage()`: insert `<hr>` before each new message, flat `.entry` class (no user/assistant alignment), keep `renderMarkdown`, `detectLanguage`, `escapeHtml`, `toggleLoading`, `scrollToBottom`

## Phase 3: Structural — HTML Rewrite

- [x] 3.1 Rewrite `app/static/index.html` to minimal skeleton: remove `<style>`, remove `<script>` block, logo SVG, font-size toggle, old Google Fonts `<link>` tags
- [x] 3.2 Add `<link rel="stylesheet" href="styles.css">` + `<script src="app.js">`
- [x] 3.3 Preserve semantic attributes: `role="log"`, `aria-live="polite"`, `aria-label`, suggestion chips with `data-msg`, footer links
- [x] 3.4 Update class names: `.app-header`, `.app-subtitle`, `.input-area`, `.chat-messages`, `.chat-form`, `.app-footer`

## Phase 4: Verification

- [x] 4.2 Check `git diff --name-only` shows only `app/static/` files (no backend changes)
- [ ] 4.1 Visual check: open in browser — verify zero border-radius/shadows/gradients on all elements
- [ ] 4.3 Submit message → fetch POST succeeds → reply renders as flat block with `<hr>` separator
- [ ] 4.4 Click suggestion chip → populates input → auto-submits → reply renders correctly
- [ ] 4.5 Loading indicator appears during fetch, disappears on response
- [ ] 4.6 Verify no Google Fonts, no SVG/logo, no size toggle in DOM
- [ ] 4.7 Tab through interactive elements — verify `focus-visible` red outline on each
