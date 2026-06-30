# Design: Brutalist UI Redesign

## Technical Approach

Split monolithic `index.html` (~330 lines) into three single-responsibility files. JS fetch/render pipeline extracted verbatim; only DOM class names and structure change. CSS adopts brutalist design system via custom properties — zero border-radius, shadows, gradients.

## Architecture Decisions

### Decision: Flat message blocks via `<hr>` separator

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Keep bubble containers | Minimal change but incompatible with brutalist aesthetic | Reject |
| Single flat `<div>` per message | Simpler DOM, loses semantic grouping | Reject |
| `<hr>` between flat messages | Adds N-1 elements, clear visual separation, matches spec | **Accept** |

**Rationale**: Messages get `padding: 16px 0`, no background. `<hr>` (`border-top: 1px solid #333`) separates them. First message has no leading `<hr>` via `:first-child` selector.

### Decision: Extract JS verbatim, adapt only DOM references

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Rewrite with modern patterns | Behavioral regression risk, violates scope | Reject |
| Extract IIFE as-is, update class/ID refs | Minimal diff, preserves tested logic | **Accept** |

**Rationale**: Existing IIFE stays. Changes: remove `sizeToggle`, flatten message classes (no `.user`/`.assistant` alignment), add `<hr>` in `addMessage`.

### Decision: Remove font-size toggle, logo SVG, Google Fonts

Spec requirement. Delete `size-toggle` button + handler, `.logo-row`/`.logo`/`.large-text` CSS, Google Fonts `<link>` tags.

## Data Flow

```
form submit → addMessage(text,'user') → flat div + <hr> + timestamp
           → fetch POST /api/chat
                → success: addMessage(data.reply,'assistant')
                → error: addMessage(msg,'error')
           → toggleLoading(false)
```

Identical to current — only DOM rendering changes.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `app/static/index.html` | Modify | Strip to skeleton: remove `<style>`, `<script>`, logo SVG, size toggle. Keep semantic HTML, aria attributes, suggestion chips, footer. Link `styles.css` + `app.js` |
| `app/static/styles.css` | Create | All visual design via CSS custom properties. Zero border-radius, shadows, gradients. `<hr>` separation. Responsive breakpoints |
| `app/static/app.js` | Create | Extracted IIFE from original. Remove `sizeToggle` refs. Adapt `addMessage` for flat `<hr>` structure. Unchanged: `fetch`, `renderMarkdown`, `detectLanguage`, `toggleLoading`, `scrollToBottom` |

## Interfaces / Contracts

### CSS Variables

| Variable | Value | Usage |
|----------|-------|-------|
| `--bg-primary` | `#1a1a1a` | Body background |
| `--bg-secondary` | `#222222` | Input area, chips background |
| `--text-primary` | `#f0f0f0` | Body text, messages |
| `--text-secondary` | `#a0a0a0` | Timestamps, subtitle |
| `--accent` | `#e63946` | Header title, focus outlines, hover states, links |
| `--border` | `#333333` | `<hr>` lines, chip borders, input border |
| `--font-body` | `'Helvetica Neue', Arial, sans-serif` | Body text |
| `--font-mono` | `'Courier New', Courier, monospace` | Timestamps |
| `--font-size-body` | `18px` | Base text |
| `--line-height` | `1.6` | Body line height |

### DOM Structure (after change)

```html
<div class="app" id="app">
  <header class="app-header">
    <h1 class="app-title">Aita-Lagun</h1>
    <p class="app-subtitle">Elderly Care Assistant</p>
  </header>
  <div class="chat-messages" id="chat-messages" role="log" ...>
    <div class="empty-state" id="empty-state">
      <h2>How can I help you today?</h2>
      <p>Try one of these examples:</p>
      <div class="suggestions" id="suggestions">
        <button data-msg="...">...</button>
      </div>
    </div>
    <!-- messages injected here by JS -->
  </div>
  <div class="input-area">
    <form class="chat-form" id="chat-form">
      <textarea id="message-input" ...></textarea>
      <button type="submit" id="send-btn">Send</button>
    </form>
    <footer class="app-footer">...</footer>
  </div>
</div>
```

### JS Function Map

| Function | Origin | Change |
|----------|--------|--------|
| `addMessage(text, type)` | Original | Insert `<hr>` before each new message (skip first). Remove bubble classes. Flat `.message` class. Keep `msg-time`, `lang-badge`, rendering |
| `toggleLoading(show)` | Original | Unchanged |
| `renderMarkdown(text)` | Original | Unchanged |
| `detectLanguage(text)` | Original | Unchanged |
| `scrollToBottom()` | Original | Unchanged |
| `escapeHtml(t)` | Original | Unchanged |
| Form submit handler | Original | Unchanged |
| Suggestion click handler | Original | Unchanged |
| `sizeToggle` handler | Original | **Removed** |

## Responsive Strategy

| Breakpoint | Container | Chat messages padding |
|------------|-----------|----------------------|
| ≥ 1024px | 720px, centered | 24px 0 |
| 768–1023px | full + 32px padding | 20px 0 |
| < 768px | full + 16px padding | 16px 0 |

Mobile input area: 12px 0 padding. Body font stays 18px (no reduction).

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| JS extraction breaks IIFE scope | Low | Same `(function(){...})()` wrap pattern. Test loaded |
| `<hr>` off-by-one (leading hr) | Low | CSS `.message:first-child hr { display: none }` |
| Wrong file linked | Low | 2 tags in index.html — trivial to verify |
| CSS variable typo | Medium | Single `:root` block, referenced consistently |

## Rollback

`git checkout -- app/static/index.html && rm app/static/styles.css app/static/app.js`
