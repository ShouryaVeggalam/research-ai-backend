"""Generic repository implementing common CRUD operations."""
from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Reusable CRUD repository bound to a single ORM model."""

    model: type[ModelType]

    def __init__(self, db: Session):
        self.db = db

    # ---- create ----
    def create(self, **kwargs: Any) -> ModelType:
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def add(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    # ---- read ----
    def get(self, obj_id: str) -> ModelType | None:
        return self.db.get(self.model, obj_id)

    def get_by(self, **filters: Any) -> ModelType | None:
        stmt = select(self.model).filter_by(**filters).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        order_by: Any | None = None,
        **filters: Any,
    ) -> list[ModelType]:
        stmt = select(self.model).filter_by(**filters)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        else:
            stmt = stmt.order_by(self.model.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count(self, **filters: Any) -> int:
        stmt = select(func.count()).select_from(self.model).filter_by(**filters)
        return int(self.db.execute(stmt).scalar_one())

    # ---- update ----
    def update(self, obj: ModelType, **kwargs: Any) -> ModelType:
        for key, value in kwargs.items():
            if value is not None and hasattr(obj, key):
                setattr(obj, key, value)
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    # ---- delete ----
    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.flush()
