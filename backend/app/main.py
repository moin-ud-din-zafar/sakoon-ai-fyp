"""FastAPI application entry point for Sakoon AI."""

import app.utils.env_patch  # noqa: F401 — must run before transformers imports

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, chat, session, user, admin, tts
from app.api.routes.assessment_routes import router as assessment_router
from app.api.routes.mood_routes import router as mood_router
from app.api.routes.avatar_routes import router as avatar_router
from app.config import UPLOAD_DIR

app = FastAPI(
    title="Sakoon AI",
    description="Virtual AI Therapist for Inclusive Mental Health Support",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(session.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(tts.router, prefix="/api/v1")
app.include_router(assessment_router, prefix="/api/v1")
app.include_router(mood_router, prefix="/api/v1")
app.include_router(avatar_router, prefix="/api/v1")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
def root():
    return {"message": "Sakoon AI API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
