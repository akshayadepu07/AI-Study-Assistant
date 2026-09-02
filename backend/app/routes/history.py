from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/sessions", response_model=list[schemas.SessionOut])
def list_sessions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return (
        db.query(models.ChatSession)
        .filter(models.ChatSession.user_id == current_user.id)
        .order_by(models.ChatSession.created_at.desc())
        .all()
    )


@router.get("/sessions/{session_id}", response_model=schemas.SessionDetailOut)
def get_session(session_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    session = db.get(models.ChatSession, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(404, "Session not found")
    return session


@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    session = db.get(models.ChatSession, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(404, "Session not found")
    db.delete(session)
    db.commit()
    return {"ok": True}


@router.post("/feedback")
def submit_feedback(req: schemas.FeedbackRequest, db: Session = Depends(get_db)):
    msg = db.get(models.Message, req.message_id)
    if not msg:
        raise HTTPException(404, "Message not found")
    fb = models.Feedback(
        message_id=req.message_id, rating=req.rating, comment=req.comment
    )
    db.add(fb)
    db.commit()
    return {"ok": True}
