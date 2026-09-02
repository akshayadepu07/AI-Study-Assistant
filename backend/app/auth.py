"""
Google Sign-In verification + our own JWT session tokens.

Flow: frontend gets a Google ID token from the Sign-In button -> POSTs it
to /api/auth/google -> we verify it with Google, find/create a User, and
hand back OUR OWN short-lived JWT. The frontend sends that JWT as
`Authorization: Bearer <token>` on every other request.
"""
import datetime as dt

import jwt
from fastapi import Depends, HTTPException, Header
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from . import models

JWT_ALGORITHM = "HS256"
JWT_EXPIRES_HOURS = 24 * 7  # 1 week


def verify_google_token(token: str) -> dict:
    try:
        return google_id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(401, "Invalid Google token.")


def create_jwt(user: "models.User") -> str:
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "exp": dt.datetime.utcnow() + dt.timedelta(hours=JWT_EXPIRES_HOURS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(
    authorization: str = Header(None), db: Session = Depends(get_db)
) -> "models.User":
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated.")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Session expired, please sign in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid session token.")

    user = db.get(models.User, int(payload["sub"]))
    if not user:
        raise HTTPException(401, "User no longer exists.")
    return user