from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.domain.shared.exceptions import DomainError

STATUS_BY_CODE: dict[str, int] = {
    "validation": 400,
    "bad_request": 400,
    "invalid_credentials": 401,
    "unauthorized": 401,
    "not_found": 404,
    "conflict": 409,
    "too_many_attempts": 429,
    "internal": 500,
}


def _envelope(code: str, message: str, status: int) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def _domain(_: Request, exc: DomainError) -> JSONResponse:
        return _envelope(exc.code, exc.message, STATUS_BY_CODE.get(exc.code, 500))

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0]["msg"] if exc.errors() else "Invalid input"
        return _envelope("validation", first, 400)

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
        return _envelope("internal", "Internal server error", 500)
