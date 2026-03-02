---
phase: 6
plan: 1
wave: 2
---

# Plan 6.1: JavaScript Interactivity & API Integration

## Objective

Wire up the frontend with JavaScript to call the backend API, render analysis results with pass/fail badges and CCPA section explanations, manage loading states, and handle errors gracefully.

## Context

- .gsd/SPEC.md
- .gsd/ARCHITECTURE.md — API contract (POST /analyze → {harmful, articles}, GET /health)
- frontend/index.html — HTML structure (from Phase 5)
- frontend/styles.css — CSS classes (.hidden, .loading, .pass, .fail)
- iisc_openHack_package/ccpa_hackathon_package/validate_format.py — test cases

## Tasks

<task type="auto">
  <name>Create app.js with API integration and result rendering</name>
  <files>frontend/app.js</files>
  <action>
    Create `frontend/app.js` with:

    1. Configuration:
       - API_BASE_URL = "http://localhost:8000" (easily changeable)
       - ANALYZE_ENDPOINT, HEALTH_ENDPOINT

    2. CCPA Section Explanations Map:
       - Object mapping common section numbers to human-readable explanations:
         - "1798.100" → "Right to Know: Consumers have the right to know what personal information is being collected about them and how it is used."
         - "1798.105" → "Right to Delete: Consumers can request deletion of their personal information held by businesses."
         - "1798.110" → "Right to Know (Disclosure): Businesses must disclose what personal information they collect, sell, or share."
         - "1798.115" → "Right to Know (Categories): Consumers can request categories of personal information sold or disclosed."
         - "1798.120" → "Right to Opt-Out: Consumers have the right to opt out of the sale of their personal information."
         - "1798.125" → "Non-Discrimination: Businesses cannot discriminate against consumers who exercise their CCPA rights."
         - "1798.130" → "Notice Requirements: Businesses must provide specific notices about data practices."
         - "1798.135" → "Opt-Out Link: Businesses must provide 'Do Not Sell My Personal Information' link."
         - "1798.140" → "Definitions: Definitions of personal information and related terms."
         - "1798.150" → "Private Right of Action: Consumers can sue for data breaches involving unencrypted data."
       - Include a fallback for unrecognized sections

    3. Health Check (on DOMContentLoaded):
       - fetch GET /health
       - Update status indicator: green dot + "Live" on 200, red dot + "Offline" on error
       - Re-check every 30 seconds

    4. Analyze Handler:
       - On "Analyze" button click:
         a. Validate textarea is not empty (show inline error if empty)
         b. Set loading state: disable button, show spinner, update button text to "Analyzing..."
         c. Show a progress message after 10s ("LLM inference in progress, this may take up to 2 minutes...")
         d. POST to /analyze with {"prompt": text}
         e. On success: call renderResults(response)
         f. On error: show error message (timeout, connection refused, unexpected)
         g. Always: remove loading state, re-enable button

    5. renderResults(data):
       - Show results section (remove .hidden class)
       - If data.harmful === false:
         - Show green pass badge with shield icon (✓ COMPLIANT)
         - Show message: "No CCPA violations detected in this text."
         - Hide violations container
       - If data.harmful === true:
         - Show red fail badge with alert icon (⚠ VIOLATION DETECTED)
         - For each article in data.articles:
           - Extract section number (parse from string like "Section 1798.120" or "1798.120")
           - Look up explanation from CCPA map
           - Create violation card with: section number, explanation, severity indicator
         - Show violations container
       - Scroll results into view smoothly

    6. Example Card Handlers:
       - On example card click: populate textarea with card's prompt text
       - Optionally auto-focus textarea

    7. Character count:
       - On textarea input: update character count display

    Do NOT use any external libraries — vanilla JS only.
    Use async/await for all fetch calls.
    Use try/catch for all error handling.

  </action>
  <verify>
    Serve frontend with `python3 -m http.server 3000` from frontend/ dir.
    1. Open browser → health check should show "Offline" (no backend running)
    2. Click example card → textarea fills
    3. Click Analyze with empty textarea → show validation error
    4. Click Analyze with text → loading state appears
  </verify>
  <done>app.js handles health checks, form submission, result rendering with CCPA explanations, example card clicks, and error states</done>
</task>

<task type="auto">
  <name>Add micro-animations and final polish</name>
  <files>frontend/styles.css, frontend/index.html</files>
  <action>
    Enhance CSS and HTML with final polish:

    1. In styles.css:
       - Add @keyframes fadeInUp for results reveal (translate + opacity)
       - Add @keyframes pulse for the loading spinner
       - Add @keyframes shimmer for a subtle gradient animation on the header brand
       - Add transition: transform 0.2s ease on all cards for hover lift
       - Add smooth focus styles on textarea (box-shadow glow)
       - Ensure the analyze button has a subtle pulse animation in loading state

    2. In index.html:
       - Add SVG icons inline for:
         - Shield check icon (for pass badge)
         - Alert triangle icon (for fail badge)
         - Lightning bolt icon (for analyze button)
         - Dot icon (for status indicator)
       - Add aria-labels for accessibility on interactive elements
       - Add a subtle tagline under the header: "AI-powered CCPA compliance analysis"

  </action>
  <verify>
    Reload frontend in browser:
    - Hover over cards → smooth lift animation
    - Check badge icons render correctly
    - Verify focus styles on textarea
  </verify>
  <done>Micro-animations working, SVG icons rendering, aria-labels on all interactive elements</done>
</task>

## Success Criteria

- [ ] Health check indicator shows backend status
- [ ] Submitting text calls POST /analyze and renders pass/fail badge
- [ ] Violated sections show with human-readable CCPA explanations
- [ ] Loading state with spinner and progress message works
- [ ] Example cards populate textarea on click
- [ ] Error states handled (timeout, server down, empty input)
- [ ] Micro-animations and hover effects are smooth
