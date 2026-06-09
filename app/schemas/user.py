"""User & Company schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.constants import UserRole


class CompanyBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    industry: str | None = None
    website: str | None = None
    description: str | None = None


class CompanyCreate(CompanyBase):
    slug: str | None = None


class CompanyRead(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    is_active: bool
    created_at: datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)
    company_id: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    is_superuser: bool
    company_id: str | None
    created_at: datetime
