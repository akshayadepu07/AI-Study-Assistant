"""
Pydantic request/response schemas.
"""
from typing import Literal, Optional
import datetime as dt

from pydantic import BaseModel, Field


Provider = Literal["groq", "openrouter", "gemini", "mistral", "openai", "anthropic"]


class ChatRequest(BaseModel):
    session_id: Optional[int] = None       # None -> create a new session
    message: str = Field(..., min_length=1)
    provider: Provider
    api_key: str = Field(..., min_length=1)   # never persisted, used once
    # NOTE: no `model` field — the backend picks the default model for
    # whichever provider is chosen (see app/ai_providers.py PROVIDERS).


class ChatResponse(BaseModel):
    session_id: int
    reply: str
    model: str   # which model actually answered, so the UI can show it


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: dt.datetime

    class Config:
        from_attributes = True


class SessionOut(BaseModel):
    id: int
    title: str
    provider: str
    model: str
    created_at: dt.datetime

    class Config:
        from_attributes = True


class SessionDetailOut(SessionOut):
    messages: list[MessageOut]


class FeedbackRequest(BaseModel):
    message_id: int
    rating: Literal["up", "down"]
    comment: Optional[str] = None
class UserOut(BaseModel):
    id: int
    email: str
    name: str
    picture: Optional[str] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    token: str
    user: UserOut