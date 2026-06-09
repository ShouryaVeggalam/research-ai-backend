"""SQLAlchemy engine and session management."""
from __future__ import annotations

from collections.abc import Generator, Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

def _build_engine():
    uri = settings.sqlalchemy_database_uri
    if uri.startswith("sqlite"):
        from sqlalchemy.pool import StaticPool

        connect_args = {"check_same_thread": False}
        kwargs: dict = {"connect_args": connect_args, "future": True}
        if ":memory:" in uri or uri.endswith("://"):
            kwargs["poolclass"] = StaticPool
        return create_engine(uri, **kwargs)
    return create_engine(
        uri,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        future=True,
    )


engine = _build_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Context manager for use in workers / scripts with commit + rollback."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
