"""
A thin, uniform wrapper around several AI providers so the rest of the
app doesn't care which one the user picked. The FRONTEND only sends a
provider name + the user's API key — the MODEL for each provider is
decided here, on the backend.

Groq, OpenRouter, and Mistral all expose an OpenAI-compatible
`/chat/completions` endpoint, so they reuse `_call_openai_compatible`
with a different `base_url`. OpenAI itself is just that function with
the default (official) base URL.

To add a new OpenAI-compatible provider: add one entry to PROVIDERS.
To add a provider with its own SDK/shape (like Anthropic or Gemini):
write a `_call_<provider>` function and reference it in PROVIDERS.
"""
from fastapi import HTTPException

SYSTEM_PROMPT = (
    "You are a patient, encouraging study assistant for students. "
    "Explain concepts step by step, use simple language, and give "
    "short code examples when the question is about programming."
)


def _call_openai_compatible(api_key: str, model: str, history: list[dict], base_url: str | None, provider_label: str) -> str:
    """Works for OpenAI, Groq, OpenRouter, and Mistral — all speak the
    same chat-completions API shape."""
    from openai import OpenAI, AuthenticationError, APIError

    client = OpenAI(api_key=api_key, base_url=base_url)
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *history],
            temperature=0.4,
        )
        return resp.choices[0].message.content
    except AuthenticationError:
        raise HTTPException(401, f"{provider_label} rejected that API key.")
    except APIError as e:
        raise HTTPException(502, f"{provider_label} API error: {e}")


def _call_anthropic(api_key: str, model: str, history: list[dict]) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,  # [{"role": "user"/"assistant", "content": "..."}]
        )
        return "".join(block.text for block in resp.content if block.type == "text")
    except anthropic.AuthenticationError:
        raise HTTPException(401, "Anthropic rejected that API key.")
    except anthropic.APIError as e:
        raise HTTPException(502, f"Anthropic API error: {e}")


def _call_gemini(api_key: str, model: str, history: list[dict]) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    try:
        gmodel = genai.GenerativeModel(model, system_instruction=SYSTEM_PROMPT)
        # Gemini wants "model" instead of "assistant" as the role name
        contents = [
            {"role": "model" if m["role"] == "assistant" else "user",
             "parts": [m["content"]]}
            for m in history
        ]
        resp = gmodel.generate_content(contents)
        return resp.text
    except Exception as e:  # google's SDK raises broad exceptions
        msg = str(e)
        if "API_KEY_INVALID" in msg or "PERMISSION_DENIED" in msg:
            raise HTTPException(401, "Gemini rejected that API key.")
        raise HTTPException(502, f"Gemini API error: {msg}")


# ---------------------------------------------------------------------
# Provider registry: one place that defines label, default model, key
# help link, and which call function to use. This is what both the
# chat route and the /api/providers endpoint read from.
# ---------------------------------------------------------------------
PROVIDERS = {
   "groq": {
    "label": "Groq",
    "default_model": "openai/gpt-oss-120b",   # was "llama-3.3-70b-versatile" — Groq retired it
    "base_url": "https://api.groq.com/openai/v1",
    "key_link": "https://console.groq.com/keys",
    "key_hint": "Free tier, very fast inference. Starts with gsk_...",
    "kind": "openai_compatible",
},
    "openrouter": {
        "label": "OpenRouter",
        "default_model": "meta-llama/llama-3.3-70b-instruct:free",
        "base_url": "https://openrouter.ai/api/v1",
        "key_link": "https://openrouter.ai/keys",
        "key_hint": "Free-tier models available (model name ends in :free). Starts with sk-or-...",
        "kind": "openai_compatible",
    },
    "gemini": {
    "label": "Google Gemini",
    "default_model": "gemini-3.1-flash-lite",   # was "gemini-1.5-flash" — fully shut down
    "base_url": None,
    "key_link": "https://aistudio.google.com/app/apikey",
    "key_hint": "Genuinely free tier, no card required. Starts with AIza...",
    "kind": "gemini",
},
    "mistral": {
        "label": "Mistral AI",
        "default_model": "mistral-small-latest",
        "base_url": "https://api.mistral.ai/v1",
        "key_link": "https://console.mistral.ai/api-keys",
        "key_hint": "Free tier available.",
        "kind": "openai_compatible",
    },
    "openai": {
        "label": "OpenAI",
        "default_model": "gpt-4o-mini",
        "base_url": None,
        "key_link": "https://platform.openai.com/api-keys",
        "key_hint": "Paid after trial credit runs out. Starts with sk-...",
        "kind": "openai_compatible",
    },
    "anthropic": {
        "label": "Anthropic (Claude)",
        "default_model": "claude-3-5-haiku-latest",
        "base_url": None,
        "key_link": "https://console.anthropic.com/settings/keys",
        "key_hint": "Paid after trial credit runs out. Starts with sk-ant-...",
        "kind": "anthropic",
    },
}


def get_default_model(provider: str) -> str:
    if provider not in PROVIDERS:
        raise HTTPException(400, f"Unknown provider '{provider}'.")
    return PROVIDERS[provider]["default_model"]


def get_ai_reply(provider: str, api_key: str, history: list[dict]) -> str:
    if provider not in PROVIDERS:
        raise HTTPException(400, f"Unknown provider '{provider}'.")

    cfg = PROVIDERS[provider]
    model = cfg["default_model"]

    if cfg["kind"] == "openai_compatible":
        return _call_openai_compatible(api_key, model, history, cfg["base_url"], cfg["label"])
    if cfg["kind"] == "anthropic":
        return _call_anthropic(api_key, model, history)
    if cfg["kind"] == "gemini":
        return _call_gemini(api_key, model, history)

    raise HTTPException(500, f"Provider '{provider}' has no handler configured.")
