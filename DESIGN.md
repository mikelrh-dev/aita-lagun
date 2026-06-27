# Aita-Lagun Design System

## Design Philosophy: Technological Warmth

Aita-Lagun's visual identity merges **professional AI precision** with **compassionate
human-centred care**. The aesthetic is **Refined Minimalism** with **Glassmorphic**
accents — heavy whitespace (even in dark mode) reduces cognitive load, keeping the
interface calm and dependable for elderly users.

The Basque influence is felt through a sturdy, grounded structural layout and a
palette inspired by the deep Atlantic coast and lush inland valleys. The emotional
response should be one of quiet confidence, security, and effortless accessibility.

---

## Colors

All colours are defined for **dark mode** (the sole mode). The palette is rooted in
deep, atmospheric neutrals that are easy on aging eyes.

### Surface & Background

| Token | Hex | Swatch | Role |
|-------|-----|--------|------|
| `surface` / `background` | `#0b1326` | `▌` | Deepest background, base layer |
| `surface-dim` | `#0b1326` | `▌` | Dim variant (same as surface) |
| `surface-bright` | `#31394d` | `▌` | Brightest surface |
| `surface-container-lowest` | `#060e20` | `▌` | Lowest container |
| `surface-container-low` | `#131b2e` | `▌` | Low-elevation containers |
| `surface-container` | `#171f33` | `▌` | Default container (cards) |
| `surface-container-high` | `#222a3d` | `▌` | Elevated containers |
| `surface-container-highest` | `#2d3449` | `▌` | Highest container (modals) |
| `surface-variant` | `#2d3449` | `▌` | Variant surface |
| `on-surface` | `#dae2fd` | `▌` | Text/icons on surface |
| `on-surface-variant` | `#bacac5` | `▌` | Muted text on surface |
| `inverse-surface` | `#dae2fd` | `▌` | Inverse surface |
| `inverse-on-surface` | `#283044` | `▌` | Text on inverse surface |
| `surface-tint` | `#3cddc7` | `▌` | Surface tint overlay |

### Primary (Teal)

| Token | Hex | Swatch | Role |
|-------|-----|--------|------|
| `primary` | `#57f1db` | `▌` | Vibrant primary — actions, active states, AI feedback |
| `on-primary` | `#003731` | `▌` | Text/icons on primary |
| `primary-container` | `#2dd4bf` | `▌` | Primary container (chat bubbles, buttons) |
| `on-primary-container` | `#00574d` | `▌` | Text on primary container |
| `inverse-primary` | `#006b5f` | `▌` | Inverse primary |
| `primary-fixed` | `#62fae3` | `▌` | Primary fixed |
| `primary-fixed-dim` | `#3cddc7` | `▌` | Dimmed primary fixed |
| `on-primary-fixed` | `#00201c` | `▌` | Text on primary fixed |
| `on-primary-fixed-variant` | `#005047` | `▌` | Muted text on primary fixed |

### Secondary (Deep Teal)

| Token | Hex | Swatch | Role |
|-------|-----|--------|------|
| `secondary` | `#6bd8cb` | `▌` | Subtle accents, secondary buttons |
| `on-secondary` | `#003732` | `▌` | Text/icons on secondary |
| `secondary-container` | `#29a195` | `▌` | Secondary container |
| `on-secondary-container` | `#00302b` | `▌` | Text on secondary container |
| `secondary-fixed` | `#89f5e7` | `▌` | Secondary fixed |
| `secondary-fixed-dim` | `#6bd8cb` | `▌` | Dimmed secondary fixed |
| `on-secondary-fixed` | `#00201d` | `▌` | Text on secondary fixed |
| `on-secondary-fixed-variant` | `#005049` | `▌` | Muted text on secondary fixed |

### Tertiary (Grey)

| Token | Hex | Swatch | Role |
|-------|-----|--------|------|
| `tertiary` | `#d8dadc` | `▌` | Neutral accent |
| `on-tertiary` | `#2d3133` | `▌` | Text on tertiary |
| `tertiary-container` | `#bcbec0` | `▌` | Tertiary container |
| `on-tertiary-container` | `#4a4d4f` | `▌` | Text on tertiary container |
| `tertiary-fixed` | `#e0e3e5` | `▌` | Tertiary fixed |
| `tertiary-fixed-dim` | `#c4c7c9` | `▌` | Dimmed tertiary fixed |
| `on-tertiary-fixed` | `#191c1e` | `▌` | Text on tertiary fixed |
| `on-tertiary-fixed-variant` | `#444749` | `▌` | Muted text on tertiary fixed |

### Error (Red)

| Token | Hex | Swatch | Role |
|-------|-----|--------|------|
| `error` | `#ffb4ab` | `▌` | Error states, emergency actions |
| `on-error` | `#690005` | `▌` | Text on error |
| `error-container` | `#93000a` | `▌` | Error container |
| `on-error-container` | `#ffdad6` | `▌` | Text on error container |

### Outline

| Token | Hex | Swatch | Role |
|-------|-----|--------|------|
| `outline` | `#859490` | `▌` | Borders, dividers |
| `outline-variant` | `#3c4a46` | `▌` | Subtle borders |

> **Note on usage**: Soft teal glows are used sparingly to indicate "AI Presence"
> or "Active Listening" states. The primary `#2dd4bf` is used for user chat
> bubbles, primary buttons, and active UI elements.

---

## Typography

Typography is the primary accessibility lever. Two typefaces create a clear,
legible hierarchy:

### Headlines — Hanken Grotesk

Conveys modern Basque industrial strength and clarity. Used for all headings,
navigation labels, and emphasis text.

| Level | Size | Line Height | Weight | Tracking | Usage |
|-------|------|-------------|--------|----------|-------|
| `headline-lg` | 48px | 56px | Bold (700) | -0.02em | Hero titles, page headings |
| `headline-lg-mobile` | 32px | 40px | Bold (700) | -0.01em | Hero titles on mobile |
| `headline-md` | 32px | 40px | Semi-Bold (600) | normal | Section headings |
| `headline-sm` | 24px | 32px | Semi-Bold (600) | normal | Card titles, sub-sections |

### Body — Atkinson Hyperlegible Next

Specifically designed to **increase character recognition for users with low
vision**. Used for all functional and body text.

| Level | Size | Line Height | Weight | Usage |
|-------|------|-------------|--------|-------|
| `body-lg` | 20px | 30px | Regular (400) | Primary body text, chat messages |
| `body-md` | 18px | 28px | Regular (400) | Secondary body text, descriptions |

### Labels — Hanken Grotesk

| Level | Size | Line Height | Weight | Tracking | Usage |
|-------|------|-------------|--------|----------|-------|
| `label-md` | 16px | 24px | Semi-Bold (600) | 0.05em | Buttons, badges, small labels |

> **Accessibility note**: Font sizes are intentionally larger than standard web
> defaults. Bold weights create a clear "scan path" for elderly users.

---

## Spacing & Layout

An **8px grid system** provides rigorous, professional alignment.

| Token | Value | Usage |
|-------|-------|-------|
| `unit` | 8px | Base grid unit — all spacing is a multiple of this |
| `container-max` | 1200px | Maximum content width on desktop |
| `gutter` | 24px | Column gutters |
| `margin-desktop` | 40px | Page margins on desktop |
| `margin-mobile` | 20px | Page margins on mobile |

**Layout principles:**

- **Desktop**: 12-column fluid grid with wide gutters (24px) for breathing room.
- **Mobile**: Single-column flow with large touch targets. Margins are 20px to
  prevent accidental edge taps.
- **Rhythm**: All spacing (margins, padding, gaps) must be a multiple of the 8px
  base unit.

---

## Shapes & Roundness

Rounded corners avoid the clinical feel of sharp corners while maintaining more
professional structure than fully pill-shaped "playful" UIs.

| Token | Value | Usage |
|-------|-------|-------|
| `sm` | 4px (0.25rem) | Small decorative elements |
| `DEFAULT` | **8px (0.5rem)** | Standard elements — inputs, buttons, chips |
| `md` | 12px (0.75rem) | Medium containers |
| `lg` | 16px (1rem) | Large containers |
| `xl` | **24px (1.5rem)** | Large cards, modals, dialogs |
| `full` | 9999px | Circular elements, avatars, icons |

---

## Elevation & Depth

Depth is communicated through **Tonal Layers** and **Subtle Glows** rather than
traditional heavy shadows.

| Level | Description | Surface Token |
|-------|-------------|---------------|
| Level 0 | Deep background | `surface` / `#0b1326` |
| Level 1 | Card surface (default container) | `surface-container` / `#171f33` |
| Level 2 | Modals, pop-overs, dialogs | `surface-container-highest` / `#2d3449` |

**Glassmorphism**: Overlays use a 12px backdrop blur with a 10% white border-stroke
to simulate polished glass.

**Glows**: Interaction points (primary buttons, active states) feature a soft,
primary-coloured outer glow (15% opacity, 20px spread) to suggest the element is
"active" and powered by AI.

---

## Component Principles

### Buttons

| Property | Primary | Secondary | Emergency |
|----------|---------|-----------|-----------|
| Background | `#2dd4bf` (teal) | Transparent (ghost) | `#ffb4ab` (error) |
| Text | `#003731` (dark) | `#57f1db` (teal text) | `#690005` (dark red) |
| Border | None | 2px solid `#57f1db` | None |
| Min height | 56px | 56px | 56px |
| Corner | 8px | 8px | 8px |
| Hover glow | 15% opacity, 20px spread | None | None |

### Cards

- **Background**: `surface-container` (`#171f33`)
- **Border**: 1px solid `outline` (`#859490` at ~20% opacity)
- **Corner**: 24px (`xl`) for large cards
- **Shadow**: None — depth via colour shifts on hover
- **Padding**: 24px (3× unit)

### Input Fields

- **Background**: `surface-container-high` (`#222a3d`)
- **Text**: `body-md` (18px, Atkinson Hyperlegible Next)
- **Active state**: Teal border glow (`#2dd4bf`)
- **Placeholder**: `on-surface-variant` (`#bacac5`)
- **Corner**: 8px

### Chat Bubbles

| Property | User Message | Assistant Message |
|----------|-------------|-------------------|
| Background | `#2dd4bf` (primary container) | `surface-container-high` (`#222a3d`) |
| Text | `#003731` (on-primary-container) | `#dae2fd` (on-surface) |
| Corner | 8px | 8px |
| Alignment | Right | Left |

### Chips & Badges

- **Background**: Semi-transparent primary colour
- **Text**: Bold, primary-on-surface colour
- **Corner**: 8px
- Example: Language badges (`ES`, `EU`) in the header

### AI Pulse Indicator

- A pulsating circle icon that appears when AI is processing
- Uses a radial gradient of primary (`#57f1db`) and secondary (`#6bd8cb`)
- Subtle glow animation

### Loading Indicators

- Skeleton screens matching card/container shapes
- Teal pulse animation
- Show immediately on any async operation

---

## Accessibility Guidelines

1. **Touch targets**: Minimum 56px for all interactive elements (buttons, inputs,
   chat actions).
2. **Contrast**: All text meets WCAG AA (minimum 4.5:1 for normal text, 3:1 for
   large text). On-surface (`#dae2fd`) on surface (`#0b1326`) exceeds AA.
3. **Typography**: Atkinson Hyperlegible Next is purpose-built for low-vision
   readability. Minimum body text is 18px.
4. **Focus indicators**: Teal outline (2px, 2px offset) on all focusable elements.
5. **Touch feedback**: All interactive elements show a 200ms press state with
   reduced opacity.
6. **Emergency action**: High-contrast red-orange accent (`#ffb4ab`) deviates from
   the teal palette for immediate visibility on critical actions (e.g., "Call
   Caretaker").

---

## File Reference

| Screenshot | File | Description |
|------------|------|-------------|
| Chat Mockup | `docs/chat-mockup.png` | Desktop chat interface with Spanish medication reminder |
| Mobile Conversation | `docs/mobile-conversation.png` | Mobile Basque-language chat view |
| Feature Cards | `docs/feature-cards.png` | Three feature showcase cards |
| Architecture | `docs/architecture-showcase.png` | System architecture diagram |
| Hero Banner | `docs/hero-banner.png` | GitHub README hero banner |

---

*Design system generated from the Aita-Lagun Stitch project
(`projects/13558646535241964762`). Token values are authoritative and match
the Material Design 3 — Fidelity colour variant.*
