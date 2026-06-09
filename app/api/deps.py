"""Shared FastAPI dependencies: auth, RBAC, tenancy."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import ROLE_HIERARCHY, UserRole
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import ACCESS_TOKEN, decode_token
from app.database.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login/oauth", auto_error=False
)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> User:
    if not token:
        raise AuthenticationError("Not authenticated.")
    payload = decode_token(token, expected_type=ACCESS_TOKEN)
    user = UserRepository(db).get(payload["sub"])
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_company_id(user: CurrentUser) -> str:
    if not user.company_id:
        raise PermissionDeniedError("User is not associated with any company.")
    return user.company_id


CompanyId = Annotated[str, Depends(get_current_company_id)]


def require_role(minimum: UserRole):
    """Dependency factory enforcing a minimum role level."""

    def _checker(user: CurrentUser) -> User:
        if ROLE_HIERARCHY.get(user.role, 0) < ROLE_HIERARCHY[minimum]:
            raise PermissionDeniedError(
                f"Requires at least '{minimum.value}' role."
            )
        return user

    return _checker


# Convenience role guards
RequireAnalyst = Annotated[User, Depends(require_role(UserRole.ANALYST))]
RequireManager = Annotated[User, Depends(require_role(UserRole.RESEARCH_MANAGER))]
RequireFounder = Annotated[User, Depends(require_role(UserRole.FOUNDER))]
RequireAdmin = Annotated[User, Depends(require_role(UserRole.ADMIN))]
