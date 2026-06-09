"""User & company repositories."""
from __future__ import annotations

from app.models.user import Company, User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return self.get_by(email=email.lower())


class CompanyRepository(BaseRepository[Company]):
    model = Company

    def get_by_slug(self, slug: str) -> Company | None:
        return self.get_by(slug=slug)
