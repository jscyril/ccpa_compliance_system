# CCPA Compliance Analyzer — Frontend

A premium, AI-powered enterprise frontend for analyzing business practices and privacy policies against the California Consumer Privacy Act (CCPA).

---

## 📁 File Structure

```
frontend/
├── index.html   — App shell & HTML layout
├── styles.css   — All styles (dark glassmorphism theme)
├── app.js       — Logic: API calls, rendering, health checks
└── README.md    — This file
```

---

## 🖥️ Running the Frontend

The frontend is pure HTML/CSS/JS — no build step needed. Serve it with any static file server:

```bash
# Python (recommended, already running)
cd frontend/
python3 -m http.server 8080
```

Then open **http://localhost:8080** in your browser.

> ⚠️ The backend must also be running on **port 8000** for analysis to work.

---

## ⚙️ How It Works

### Layout
- **Split-pane design**: 40% left (input) / 60% right (output)
- Left pane: text area for policy input + "Run Analysis" button
- Right pane: Verdict card + raw JSON output block

### User Flow
1. User pastes privacy policy text into the left pane
2. Clicks **Run Analysis** (or `Ctrl+Enter`)
3. `app.js` sends a `POST /analyze` request to the backend
4. The right pane updates with:
   - A **Verdict Card** — "Compliant" (green) or "Review Required" (red)
   - A **raw JSON block** with syntax-highlighted engine output

### Health Check
- On page load and every 30 seconds, `app.js` pings `GET /health`
- The header status dot turns 🟢 green (online) or 🔴 red (offline)

---

## 🔌 Backend API Contract

The frontend communicates with the backend over **HTTP on `localhost:8000`**. Two endpoints are required:

---

### `GET /health`

Used by the frontend to check if the backend is alive.

**Expected response:** `HTTP 200 OK` (any body is fine)

```http
GET http://localhost:8000/health
```

---

### `POST /analyze`

The core analysis endpoint. Receives plain text and returns a compliance verdict.

**Request:**
```http
POST http://localhost:8000/analyze
Content-Type: application/json
```
```json
{
  "prompt": "We collect geolocation data and share it with third-party advertisers without user consent."
}
```

**Required Response Fields:**

| Field | Type | Description |
|---|---|---|
| `harmful` | `boolean` | `true` if a CCPA violation was detected, `false` if compliant |
| `articles` | `string[]` | List of violated CCPA article references (e.g. `"Cal. Civ. Code § 1798.120"`) |

**Minimum valid response (compliant):**
```json
{
  "harmful": false,
  "articles": []
}
```

**Minimum valid response (violation detected):**
```json
{
  "harmful": true,
  "articles": [
    "Cal. Civ. Code § 1798.120",
    "Cal. Civ. Code § 1798.135"
  ]
}
```

> Any additional fields (e.g. `confidence`, `reasoning`, `retrieved_chunks`) are also rendered in the raw JSON block as-is.

---

## ⚡ Key Configuration (in `app.js`)

| Constant | Default | Purpose |
|---|---|---|
| `API_URL` | `http://localhost:8000/analyze` | Main analysis endpoint |
| `HEALTH_URL` | `http://localhost:8000/health` | Health check endpoint |
| Health interval | `30000` ms | How often the dot is refreshed |

To point the frontend at a different backend host/port, change the two URL constants at the top of `app.js`:

```js
const API_URL    = 'http://localhost:8000/analyze';
const HEALTH_URL = 'http://localhost:8000/health';
```

---

## 🎨 Tech Stack

| Concern | Technology |
|---|---|
| Structure | Vanilla HTML5 |
| Styles | Vanilla CSS (glassmorphism, CSS variables) |
| Logic | Vanilla JavaScript (ES2022, no frameworks) |
| Fonts | Inter (UI) + JetBrains Mono (code block) via Google Fonts |
| HTTP | Native `fetch` API |

No `npm`, no bundler, no dependencies.
