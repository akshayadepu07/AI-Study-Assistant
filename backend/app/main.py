from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .routes import chat, history, providers, auth


# Auto-create tables on startup (fine for a student project; use
# Alembic migrations instead if this grows into something bigger).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Study Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(history.router)
app.include_router(providers.router)
app.include_router(auth.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
