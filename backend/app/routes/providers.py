from fastapi import APIRouter

from ..ai_providers import PROVIDERS

router = APIRouter(prefix="/api", tags=["providers"])


@router.get("/providers")
def list_providers():
    """
    Returns everything the frontend needs to build the provider
    dropdown and the 'get an API key' hints — without hardcoding any
    of it in JS. The default model per provider is intentionally
    included here only for display; the backend is what actually
    decides which model gets used (app/ai_providers.py).
    """
    return [
        {
            "id": provider_id,
            "label": cfg["label"],
            "default_model": cfg["default_model"],
            "key_link": cfg["key_link"],
            "key_hint": cfg["key_hint"],
        }
        for provider_id, cfg in PROVIDERS.items()
    ]
