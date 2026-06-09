"""Authentication & user management service."""
from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.core.constants import UserRole
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
)
from app.core.security import (
    REFRESH_TOKEN,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user import CompanyRepository, UserRepository
from app.schemas.auth import TokenPair
from app.schemas.user import UserCreate


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "company"


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.companies = CompanyRepository(db)

    def register(self, data: UserCreate, *, default_company: bool = True) -> User:
        if self.users.get_by_email(data.email):
            raise ConflictError("A user with this email already exists.")

        company_id = data.company_id
        if not company_id and default_company:
            base_slug = _slugify(data.email.split("@")[0])
            slug = base_slug
            i = 1
            while self.companies.get_by_slug(slug):
                slug = f"{base_slug}-{i}"
                i += 1
            company = self.companies.create(name=f"{data.email.split('@')[0]}'s Org", slug=slug)
            company_id = company.id

        user = self.users.create(
            email=data.email.lower(),
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=data.role.value if isinstance(data.role, UserRole) else data.role,
            company_id=company_id,
        )
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Incorrect email or password.")
        if not user.is_active:
            raise AuthenticationError("This account is disabled.")
        return user

    def issue_tokens(self, user: User) -> TokenPair:
        claims = {"role": user.role, "company_id": user.company_id}
        return TokenPair(
            access_token=create_access_token(user.id, claims),
            refresh_token=create_refresh_token(user.id),
        )

    def login(self, email: str, password: str) -> TokenPair:
        user = self.authenticate(email, password)
        return self.issue_tokens(user)

    def refresh(self, refresh_token: str) -> TokenPair:
        payload = decode_token(refresh_token, expected_type=REFRESH_TOKEN)
        user = self.users.get(payload["sub"])
        if not user or not user.is_active:
            raise AuthenticationError("Invalid refresh token.")
        return self.issue_tokens(user)

    def get_user(self, user_id: str) -> User:
        user = self.users.get(user_id)
        if not user:
            raise NotFoundError("User not found.")
        return user
