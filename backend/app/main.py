from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.applications import router as applications_router
from app.api.documents import router as documents_router
from app.api.health import router as health_router
from app.core.config import get_settings
from app.core.db import init_db
from app.core.logging import configure_logging
from app.middleware.request_size import RequestSizeLimitMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    if settings.auto_init_db:
        init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)
    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
    app.add_middleware(RequestSizeLimitMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(applications_router)
    app.include_router(documents_router)
    return app


app = create_app()
