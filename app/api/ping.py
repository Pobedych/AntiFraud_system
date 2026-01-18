"""
Health-check.
Без авторизации.
Автопроверка начинается именно с этого эндпоинта.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/api/v1/ping")
def ping():
    return {"status": "ok"}
