from __future__ import annotations

from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def _engine_options(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(
        settings.database_url,
        future=True,
        pool_pre_ping=True,
        **_engine_options(settings.database_url),
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )


async def get_db() -> AsyncGenerator[Session, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    import app.models.application  # noqa: F401
    import app.models.document  # noqa: F401
    import app.models.document_page  # noqa: F401
    import app.models.extracted_field  # noqa: F401
    import app.models.review_action  # noqa: F401
    import app.models.validation_flag  # noqa: F401

    Base.metadata.create_all(bind=get_engine())


def clear_db_state() -> None:
    if get_engine.cache_info().currsize:
        get_engine().dispose()

    get_session_factory.cache_clear()
    get_engine.cache_clear()
