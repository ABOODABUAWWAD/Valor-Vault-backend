"""Domain error hierarchy. Each carries a stable lowercase `code` the
presentation layer maps to an HTTP status + the nested error envelope."""

from __future__ import annotations


class DomainError(Exception):
    code: str = "internal"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(DomainError):
    code = "validation"


class NotFoundError(DomainError):
    code = "not_found"


class ConflictError(DomainError):
    code = "conflict"


class UnauthenticatedError(DomainError):
    code = "unauthorized"


class InvalidCredentialsError(DomainError):
    code = "invalid_credentials"


class TooManyAttemptsError(DomainError):
    code = "too_many_attempts"
