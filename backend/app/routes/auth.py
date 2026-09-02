from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..auth import verify_google_token, create_jwt, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class GoogleLoginRequest(BaseModel):
    credential: str  # the Google ID token from the frontend button


@router.post("/google", response_model=schemas.AuthResponse)
def google_login(req: GoogleLoginRequest, db: Session = Depends(get_db)):
    payload = verify_google_token(req.credential)

    user = db.query(models.User).filter(models.User.google_sub == payload["sub"]).first()
    if not user:
        user = models.User(
            google_sub=payload["sub"],
            email=payload["email"],
            name=payload.get("name", payload["email"]),
            picture=payload.get("picture"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return schemas.AuthResponse(token=create_jwt(user), user=user)


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user