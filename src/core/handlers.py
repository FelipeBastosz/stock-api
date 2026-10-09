from http import HTTPStatus
from typing import Any, Dict
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.exceptions import AppException
from src.core.logging import logger


def format_error_response(
    status_code: int,
    error: str,
    message: str,
    details: Any = None,
) -> JSONResponse:
    content: Dict[str, Any] = {
        "status_code": status_code,
        "error": error,
        "message": message,
        "details": details,
    }
    return JSONResponse(status_code=status_code, content=content)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    try:
        http_phrase = HTTPStatus(exc.status_code).phrase
    except ValueError:
        http_phrase = "Bad Request"

    logger.warning(
        f"[{exc.status_code}] {http_phrase} em {request.method} {request.url.path}: {exc.message}"
    )

    return format_error_response(
        status_code=exc.status_code,
        error=http_phrase,
        message=exc.message,
        details=exc.details,
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    try:
        http_phrase = HTTPStatus(exc.status_code).phrase
    except ValueError:
        http_phrase = "HTTP Error"

    logger.warning(
        f"[{exc.status_code}] {http_phrase} em {request.method} {request.url.path}: {exc.detail}"
    )

    return format_error_response(
        status_code=exc.status_code,
        error=http_phrase,
        message=str(exc.detail),
        details=None,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    formatted_errors = []
    for err in exc.errors():
        loc = " -> ".join(str(item) for item in err.get("loc", []))
        formatted_errors.append(
            {
                "field": loc,
                "message": err.get("msg", "Entrada inválida"),
                "type": err.get("type", "value_error"),
            }
        )

    logger.warning(
        f"[422] Erro de validação em {request.method} {request.url.path}: {formatted_errors}"
    )

    return format_error_response(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        error="Unprocessable Entity",
        message="Dados da requisição inválidos ou malformados.",
        details=formatted_errors,
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.opt(exception=exc).error(
        f"[500] Erro interno em {request.method} {request.url.path}: {str(exc)}"
    )

    return format_error_response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        error="Internal Server Error",
        message="Ocorreu um erro interno no servidor.",
        details=None,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
