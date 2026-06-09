"""Authentication endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import LoginRequest, RefreshRequest, TokenPair
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: DbSession) -> UserRead:
    user = AuthService(db).register(data)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenPair)
def login(data: LoginRequest, db: DbSession) -> TokenPair:
    return AuthService(db).login(data.email, data.password)


@router.post("/login/oauth", response_model=TokenPair, include_in_schema=False)
def login_oauth(db: DbSession, form: OAuth2PasswordRequestForm = Depends()) -> TokenPair:
    """OAuth2 password flow so the Swagger 'Authorize' button works."""
    return AuthService(db).login(form.username, form.password)


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshRequest, db: DbSession) -> TokenPair:
    return AuthService(db).refresh(data.refresh_token)


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
