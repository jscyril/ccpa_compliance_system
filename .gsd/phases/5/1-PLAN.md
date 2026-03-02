---
phase: 5
plan: 1
wave: 1
---

# Plan 5.1: HTML Structure & Dark Theme CSS

## Objective

Create the complete HTML page structure and premium dark-themed CSS for the CCPA compliance analyzer frontend. After this plan, the UI should render correctly in a browser with full visual styling — no interactivity yet.

## Context

- .gsd/SPEC.md
- .gsd/ARCHITECTURE.md — API contract (POST /analyze, GET /health)
- iisc_openHack_package/ccpa_hackathon_package/validate_format.py — test cases for example prompts

## Tasks

<task type="auto">
  <name>Create index.html with full page structure</name>
  <files>frontend/index.html</files>
  <action>
    Create `frontend/index.html` with:
    1. HTML5 boilerplate, meta viewport, Google Fonts (Inter), link to styles.css and app.js (defer)
    2. Header section:
       - App logo/icon + "CCPA Analyzer" title
       - Backend status indicator (a small dot with text "Live" / "Offline")
    3. Main analysis card:
       - "New Analysis" heading
       - Large textarea (min 6 rows) with placeholder: "Paste your privacy policy text, data collection clause, or marketing copy here..."
       - Character count indicator
       - "Analyze Compliance" button (prominent, centered below textarea)
    4. Results section (initially hidden via CSS class):
       - Badge area: large pass/fail badge (icon + text)
       - Violations list container: cards for each violated section
       - Each violation card: section number, section title, explanation text
    5. Example prompts section:
       - Section heading: "Try an Example"
       - 3 clickable cards:
         a. SAFE: "We provide a clear privacy policy and allow customers to opt out of data selling at any time."
         b. RISKY: "We are selling our customers' personal information to third-party data brokers without informing them."
         c. SAFE: "We deleted all personal data within 45 days after receiving the consumer's verified request."
    6. Footer with hackathon branding
    
    Use semantic HTML (main, section, article). All interactive elements must have unique IDs for JS binding.
    Do NOT add any inline styles — all styling goes in styles.css.
  </action>
  <verify>Open frontend/index.html in browser — page should render with unstyled but complete structure</verify>
  <done>index.html contains header, textarea, button, results area, example cards, footer — all with unique IDs</done>
</task>

<task type="auto">
  <name>Create premium dark-themed CSS</name>
  <files>frontend/styles.css</files>
  <action>
    Create `frontend/styles.css` with a premium dark theme:

    1. CSS custom properties (design tokens):
       - --bg-primary: #0a0e17 (deep dark navy)
       - --bg-card: #111827 (slightly lighter)
       - --bg-card-hover: #1a2332
       - --border-color: rgba(56, 189, 248, 0.15) (subtle cyan glow)
       - --text-primary: #e2e8f0
       - --text-secondary: #94a3b8
       - --accent-cyan: #38bdf8
       - --accent-green: #22c55e
       - --accent-red: #ef4444
       - --font-body: 'Inter', system-ui, sans-serif
       - --font-mono: 'JetBrains Mono', 'Fira Code', monospace

    2. Base styles:
       - Dark background on body, Inter font, smooth scrolling
       - Container max-width 720px, centered

    3. Header:
       - Flexbox row, logo left, status indicator right
       - Status dot: 8px circle with glow (green when live, red when offline)

    4. Analysis card:
       - Dark card with subtle border, rounded corners (16px)
       - Glassmorphism: backdrop-filter blur, semi-transparent background
       - Box shadow with subtle cyan glow on hover

    5. Textarea:
       - Dark background (#0d1117), monospace font
       - Cyan border on focus with glow transition
       - Smooth resize

    6. Analyze button:
       - Gradient background (cyan to blue)
       - Hover: brighten + subtle lift (translateY)
       - Disabled state: muted, no pointer events
       - Loading state class: show spinner

    7. Results section:
       - Hidden by default (.hidden class: display none)
       - Badge: large centered badge with icon
       - .badge-pass: green background/border, shield icon area
       - .badge-fail: red background/border, alert icon area
       - Violation cards: dark cards with red left border, section number prominent

    8. Example cards:
       - Grid layout (3 columns on desktop, 1 on mobile)
       - Card with tag ("SAFE" green / "RISKY" red)
       - Hover: lift + border glow
       - Cursor pointer

    9. Loading spinner:
       - CSS keyframe animation (rotate)
       - Circular border spinner

    10. Responsive:
        - @media max-width 768px: single column, smaller padding
        - @media max-width 480px: reduce font sizes

    11. Transitions:
        - All interactive elements: transition 0.2s ease
        - Results reveal: fade-in animation (opacity 0→1)

    Avoid any !important. Use class-based state management (.hidden, .loading, .pass, .fail).

  </action>
  <verify>Serve with `python3 -m http.server 3000` from frontend/ and open http://localhost:3000 — dark theme renders, cards visible, responsive layout works</verify>
  <done>Full dark theme CSS with glassmorphism, responsive breakpoints, state classes for pass/fail/loading/hidden, and smooth transitions</done>
</task>

## Success Criteria

- [ ] frontend/index.html renders a complete page structure in a browser
- [ ] Dark theme with premium aesthetic is applied
- [ ] Layout is responsive (desktop + mobile)
- [ ] All interactive elements have unique IDs
- [ ] No JavaScript required for visual rendering
