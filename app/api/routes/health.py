"""Health & metadata endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}


@router.get("/")
def root() -> dict:
    return {
        "name": settings.APP_NAME,
        "tagline": settings.APP_TAGLINE,
        "docs": "/docs",
        "version": "1.0.0",
        "llm_active": settings.llm_active,
    }
