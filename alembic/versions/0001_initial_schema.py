"""Initial schema for Celestra Research AI.

Creates the full schema from the SQLAlchemy metadata. This keeps the initial
migration in lock-step with the models; subsequent changes should use
``alembic revision --autogenerate`` for granular diffs.

Revision ID: 0001
Revises:
Create Date: 2026-06-06
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op  # noqa: F401

import app.models  # noqa: F401  ensure models are registered
from app.database.base import Base

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
