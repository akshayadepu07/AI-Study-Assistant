# AI Study Assistant

A multi-provider AI study assistant. Sign in with Google, pick an AI provider,
paste in **your own** API key, and start chatting — no model dropdown needed,
the backend picks the right model for whichever provider you choose. Chat
history is saved per-user in MySQL, so it's there when you come back.

**Live app:** https://ai-study-assistant-ten-iota.vercel.app
**API:** https://ai-study-assistant-b1ud.onrender.com

**Stack:** React (Vite) · Python FastAPI · MySQL · Google OAuth · Groq / OpenRouter / Gemini / Mistral / OpenAI / Anthropic / Grok
ai-study-assistant/
├── backend/ FastAPI REST API + MySQL models
│ ├── app/
│ │ ├── main.py FastAPI app entrypoint
│ │ ├── config.py env-based settings
│ │ ├── database.py SQLAlchemy engine/session
│ │ ├── models.py User / ChatSession / Message / Feedback tables
│ │ ├── schemas.py Pydantic request/response models
│ │ ├── auth.py Google OAuth verification + JWT session tokens
│ │ ├── ai_providers.py provider registry + call wrappers — default
│ │ │ model per provider lives here
│ │ └── routes/
│ │ ├── auth.py POST /api/auth/google, GET /api/auth/me
│ │ ├── chat.py POST /api/chat
│ │ ├── history.py session list/detail/delete, feedback
│ │ └── providers.py GET /api/providers (feeds the frontend dropdown)
│ ├── requirements.txt
│ ├── init_db.sql
│ └── .env.example
├── frontend/ React chat UI
│ └── src/
│ ├── App.jsx
│ ├── api.js
│ └── components/
│ ├── ChatWindow.jsx
│ ├── MessageBubble.jsx
│ ├── ProviderSelector.jsx provider-only dropdown (no model picker)
│ ├── ApiKeyModal.jsx
│ ├── LoginScreen.jsx Google sign-in
│ └── Sidebar.jsx chat history + account menu (bottom-left)
└── docs/
├── GET_API_KEYS.md how to get a key from each provider
└── DEPLOYMENT.md deployment notes (Render + Vercel + Railway)

## How sign-in + "bring your own key" works together

- Sign-in is Google OAuth only. The frontend gets a Google ID token, sends it
  to `POST /api/auth/google`, the backend verifies it with Google, creates or
  finds a `User` row, and returns its **own** JWT. That JWT is stored in the
  browser and sent as `Authorization: Bearer <token>` on every request after
  that — chat history and sessions are scoped to whoever's logged in.
- Once signed in, the user picks a **provider only** (no model dropdown) from
  the account menu in the bottom-left of the sidebar, then adds their AI
  provider API key. The key is stored **only** in the browser's
  `localStorage`, one per provider, and sent with each chat request — the
  backend uses it once, to call that provider, then discards it. It is
  **never written to MySQL.**
- The backend decides which model to use for each provider
  (`app/ai_providers.py` → `PROVIDERS`) — that's the single place to edit if
  a provider's default model changes; the frontend never needs updating.

See `docs/GET_API_KEYS.md` for exact steps to get a key from each supported
provider (Groq, OpenRouter, and Gemini all have usable free tiers).

---

## Step-by-step: run it locally

### Prerequisites

- Python 3.11 or 3.12 (not 3.13+ — some dependencies don't have prebuilt
  wheels for the newest Python yet)
- Node.js 18+
- MySQL Server 8+ running locally, or a free hosted instance (see
  `docs/DEPLOYMENT.md`)
- A Google Cloud OAuth Client ID (see below)

### Step 1 — Google OAuth setup

1. https://console.cloud.google.com/apis/credentials → **Create Credentials
   → OAuth client ID** → Web application
2. Authorized JavaScript origins: `http://localhost:5173`
3. Copy the Client ID (ends in `.apps.googleusercontent.com`)

### Step 2 — Create the database

```bash
mysql -u root -p < backend/init_db.sql
```

This creates an empty `ai_study_assistant` database. Tables (`users`,
`chat_sessions`, `messages`, `feedback`) are created automatically the first
time the backend starts.

### Step 3 — Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# open .env and fill in: MySQL credentials, GOOGLE_CLIENT_ID, JWT_SECRET
```

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health → `{"status": "ok"}`

### Step 4 — Frontend setup

In a **new terminal**:

```bash
cd frontend
npm install
cp .env.example .env
# open .env and fill in VITE_GOOGLE_CLIENT_ID (same value as the backend's)
npm run dev
```

Open http://localhost:5173.

### Step 5 — Use the app

1. Sign in with Google.
2. Click your name/avatar at the bottom of the sidebar to open the account
   menu.
3. Pick a provider (Groq is free and fast — good default) and add your API
   key (see `docs/GET_API_KEYS.md`).
4. Start chatting. Refresh the page — your chat history is still there,
   loaded from MySQL.

---

## Deployment

Currently deployed as:

- **Frontend** → Vercel (`frontend/`, Vite build)
- **Backend** → Render (`backend/`, FastAPI + Uvicorn)
- **Database** → Railway MySQL (public TCP proxy, since Render and Railway
  are different hosts and can't reach each other's private networks)

Full walkthrough, including the exact environment variables each service
needs, is in `docs/DEPLOYMENT.md`.

## Adding a new AI provider

Most providers (anything with an OpenAI-compatible `/chat/completions`
endpoint — this covers Groq, OpenRouter, Mistral, and OpenAI itself) can be
added with a single new entry in the `PROVIDERS` dict in
`backend/app/ai_providers.py`:

```python
"newprovider": {
    "label": "New Provider",
    "default_model": "some-model-name",
    "base_url": "https://api.newprovider.com/v1",
    "key_link": "https://newprovider.com/api-keys",
    "key_hint": "Starts with np-...",
    "kind": "openai_compatible",
},
```

The frontend dropdown and the "add your key" modal both pull from
`GET /api/providers` at runtime, so nothing in `frontend/` needs editing.
Providers with a different API shape (Anthropic, Gemini) need their own
small `_call_<provider>()` wrapper function — see the existing ones in
`ai_providers.py` for the pattern.

## Resume line