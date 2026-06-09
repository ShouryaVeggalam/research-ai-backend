"""Startup bootstrap: ensure schema & seed the first admin user."""
from __future__ import annotations

from app.core.config import settings
from app.core.constants import UserRole
from app.core.logging import get_logger
from app.database.base import Base
from app.database.session import engine, session_scope
from app.repositories.user import CompanyRepository, UserRepository
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate

logger = get_logger("bootstrap")


def create_schema() -> None:
    """Create tables if they do not exist (idempotent, dev convenience)."""
    import app.models  # noqa: F401  ensure models are registered

    Base.metadata.create_all(bind=engine)


def seed_admin() -> None:
    with session_scope() as db:
        users = UserRepository(db)
        if users.get_by_email(settings.FIRST_ADMIN_EMAIL):
            return
        companies = CompanyRepository(db)
        company = companies.get_by_slug("celestra")
        if not company:
            company = companies.create(name="Celestra", slug="celestra")
        db.flush()
        AuthService(db).register(
            UserCreate(
                email=settings.FIRST_ADMIN_EMAIL,
                password=settings.FIRST_ADMIN_PASSWORD,
                full_name=settings.FIRST_ADMIN_NAME,
                role=UserRole.ADMIN,
                company_id=company.id,
            ),
            default_company=False,
        )
        logger.info("bootstrap.admin_created", email=settings.FIRST_ADMIN_EMAIL)


def run_bootstrap(create_tables: bool = True) -> None:
    if create_tables:
        create_schema()
    try:
        seed_admin()
    except Exception as exc:  # pragma: no cover - non-fatal seeding
        logger.warning("bootstrap.seed_failed", error=str(exc))
