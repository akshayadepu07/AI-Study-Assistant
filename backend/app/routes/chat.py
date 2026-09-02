from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..ai_providers import get_ai_reply, get_default_model
from ..auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=schemas.ChatResponse)
def send_message(
    req: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # 1. Get or create the chat session (model is decided by the backend,
    #    based on which provider was chosen — see ai_providers.PROVIDERS)
    if req.session_id:
        session = db.get(models.ChatSession, req.session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(404, "Session not found")
    else:
        session = models.ChatSession(
            title=req.message[:50],
            provider=req.provider,
            model=get_default_model(req.provider),
            user_id=current_user.id,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # 2. Save the user's message
    user_msg = models.Message(session_id=session.id, role="user", content=req.message)
    db.add(user_msg)
    db.commit()

    # 3. Build conversation history for the AI call (last 20 messages)
    past = (
        db.query(models.Message)
        .filter(models.Message.session_id == session.id)
        .order_by(models.Message.id.asc())
        .all()
    )[-20:]
    history = [{"role": m.role, "content": m.content} for m in past]

    # 4. Call the chosen AI provider with the user's own key (never stored)
    reply_text = get_ai_reply(req.provider, req.api_key, history)

    # 5. Save the assistant's reply
    assistant_msg = models.Message(
        session_id=session.id, role="assistant", content=reply_text
    )
    db.add(assistant_msg)
    db.commit()

    return schemas.ChatResponse(
        session_id=session.id, reply=reply_text, model=session.model
    )