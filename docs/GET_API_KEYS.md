# How to get an API key for each provider

The app lets the *user* paste their own key, so you (and anyone using your
deployed app) each need to grab one. **Groq, Gemini, OpenRouter, and
Mistral all have usable free tiers** — start with one of those if you just
want to demo the app without spending anything.

The model used for each provider is fixed on the backend (see
`backend/app/ai_providers.py` → `PROVIDERS`), so you only ever need to pick
a *provider*, not a specific model.

## Groq — free, very fast (recommended default)

1. Go to https://console.groq.com and sign up / log in.
2. Open https://console.groq.com/keys.
3. Click **Create API Key**, name it, and copy it — shown once.
4. Groq's free tier is generous and needs no card. Current default model
   in this app: `llama-3.3-70b-versatile`.
5. Paste the key (starts with `gsk_...`) into the app with **Groq** selected.

## OpenRouter — free-tier models available

1. Go to https://openrouter.ai and sign up / log in.
2. Open https://openrouter.ai/keys.
3. Click **Create Key**, name it, and copy it.
4. This app defaults to a `:free`-suffixed model
   (`meta-llama/llama-3.3-70b-instruct:free`) so no payment is required to
   try it — OpenRouter rate-limits free models but doesn't charge for them.
5. Paste the key (starts with `sk-or-...`) into the app with **OpenRouter** selected.

## Google Gemini — free tier, no card required

1. Go to https://aistudio.google.com and sign in with a Google account.
2. Open https://aistudio.google.com/app/apikey.
3. Click **Create API key** (choose or create a Google Cloud project when prompted).
4. Copy the key.
5. Paste the key (starts with `AIza...`) into the app with **Gemini** selected.

## Mistral AI — free tier available

1. Go to https://console.mistral.ai and sign up / log in.
2. Open https://console.mistral.ai/api-keys.
3. Click **Create new key**, name it, and copy it.
4. Paste the key into the app with **Mistral** selected.

## OpenAI — paid after trial credit

1. Go to https://platform.openai.com/signup and create an account (or log in).
2. Open https://platform.openai.com/api-keys.
3. Click **Create new secret key**, name it, and copy it immediately.
4. New accounts get a small free credit; after that, add a card at
   https://platform.openai.com/settings/organization/billing.
5. Paste the key (starts with `sk-...`) into the app with **OpenAI** selected.

## Anthropic (Claude) — paid after trial credit

1. Go to https://console.anthropic.com and sign up / log in.
2. Open https://console.anthropic.com/settings/keys.
3. Click **Create Key**, name it, and copy it.
4. New accounts get a small free credit; check limits at
   https://console.anthropic.com/settings/plans.
5. Paste the key (starts with `sk-ant-...`) into the app with **Anthropic** selected.

## Keeping keys safe

- Never commit a real key to Git. Only `.env.example` files (with placeholder
  values) belong in the repo — your real `.env` files are already covered by
  `.gitignore`.
- This app's backend never writes the API key to MySQL; it's used once per
  request and discarded. The frontend stores it in the browser's
  `localStorage` only, per provider, so mention this in your resume/demo as
  a deliberate security choice.
- If you ever paste a key into a public place by accident, revoke it
  immediately from the provider's dashboard (the links above) and generate
  a new one.
