"""Domain-level exceptions mapped to HTTP responses."""
from __future__ import annotations

from fastapi import status


class CelestraError(Exception):
    """Base class for all application errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_error"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None, *, code: str | None = None):
        if message:
            self.message = message
        if code:
            self.code = code
        super().__init__(self.message)


class NotFoundError(CelestraError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    message = "Resource not found."


class ConflictError(CelestraError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"
    message = "Resource already exists."


class ValidationError(CelestraError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "validation_error"
    message = "Validation failed."


class AuthenticationError(CelestraError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "authentication_error"
    message = "Could not validate credentials."


class PermissionDeniedError(CelestraError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "permission_denied"
    message = "You do not have permission to perform this action."


class AgentError(CelestraError):
    status_code = status.HTTP_502_BAD_GATEWAY
    code = "agent_error"
    message = "An intelligence agent failed to produce a result."
