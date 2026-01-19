"""
Единый формат ошибок по ТЗ:
{ code, message, traceId, timestamp, path }
Для 422: + fieldErrors
"""

import uuid
from datetime import datetime, timezone
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

def _ts():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _base(request: Request, code: str, message: str):
    return {
        "code": code,
        "message": message,
        "traceId": str(uuid.uuid4()),
        "timestamp": _ts(),
        "path": request.url.path,
    }

def register_error_handlers(app):
    @app.exception_handler(RequestValidationError)
    async def pydantic_422(request: Request, exc: RequestValidationError):
        field_errors = []
        for e in exc.errors():
            loc = e.get("loc", [])
            field = loc[-1] if loc else "unknown"
            field_errors.append({
                "field": str(field),
                "issue": e.get("msg", "invalid"),
                "rejectedValue": None,
            })
        payload = _base(request, "VALIDATION_FAILED", "Некоторые поля не прошли валидацию")
        payload["fieldErrors"] = field_errors
        return JSONResponse(status_code=422, content=payload)

    @app.exception_handler(HTTPException)
    async def http_exc(request: Request, exc: HTTPException):
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            423: "USER_DEACTIVATED",
        }
        code = code_map.get(exc.status_code, "ERROR")
        return JSONResponse(
            status_code=exc.status_code,
            content=_base(request, code, str(exc.detail)),
        )

def validation_failed(request: Request, field_errors: list[dict]):
    payload = _base(request, "VALIDATION_FAILED", "Некоторые поля не прошли валидацию")
    payload["fieldErrors"] = field_errors
    return JSONResponse(status_code=422, content=payload)
