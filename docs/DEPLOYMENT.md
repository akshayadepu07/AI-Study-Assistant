# Deployment guide (optional, but great for your resume link)

You don't have to deploy this to put it on your resume — a good README +
demo video is enough. But a live link is more impressive. Here's the
easiest free path.

## 1. Database — Railway (or PlanetScale / any managed MySQL)

1. Create a free account at https://railway.app.
2. **New Project → Provision MySQL.**
3. Open the MySQL service's **Variables** tab and note `MYSQLHOST`,
   `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`.

## 2. Backend — Render

1. Push this project to a GitHub repo.
2. Go to https://render.com → **New → Web Service** → connect your repo.
3. Root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (from step 1): `DB_HOST`, `DB_PORT`,
   `DB_USER`, `DB_PASSWORD`, `DB_NAME`, plus `CORS_ORIGINS` set to your
   deployed frontend URL (fill this in after step 3).
7. Deploy. Note the resulting backend URL, e.g. `https://ai-study-assistant.onrender.com`.

## 3. Frontend — Vercel or Netlify

1. Go to https://vercel.com (or https://netlify.com) → **New Project** →
   import the same repo, root directory `frontend`.
2. Framework preset: Vite.
3. Add environment variable `VITE_API_BASE_URL` = your Render backend URL
   from step 2.
4. Deploy. Note the resulting frontend URL, e.g. `https://ai-study-assistant.vercel.app`.
5. Go back to Render and update `CORS_ORIGINS` to this frontend URL, then
   redeploy the backend so it accepts requests from it.

## 4. Put it on your resume

```
AI Study Assistant — React, Python (FastAPI), MySQL, OpenAI/Anthropic/Gemini APIs
Multi-provider AI chatbot for students with a Python REST backend and MySQL-persisted
chat history; users choose their own AI provider/model and supply their own API key.
github.com/yourname/ai-study-assistant · live demo: your-deployed-url.vercel.app
```

## If deployment feels heavy

Skip it — record a 60–90 second screen capture (Loom, OBS, or your phone)
showing: picking a provider, pasting a key, asking a question, getting a
reply, and the chat history persisting after a refresh. Link the video and
the GitHub repo instead. That's a completely normal and accepted substitute
for a live deployment on a student resume.
