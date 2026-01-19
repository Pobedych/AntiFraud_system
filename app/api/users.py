from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.core.errors import validation_failed
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    UsersListResponse,
    UserUpdateRequest,
    AdminUserCreateRequest,
    AdminUserUpdateRequest,
)
from app.services import users as users_service

router = APIRouter(prefix="/api/v1/users", tags=["users"])

# PUT обязан содержать все ключи (missing -> 422)
REQUIRED_PUT_KEYS = {"fullName", "age", "region", "gender", "maritalStatus"}


def _iso(dt):
    return dt.isoformat().replace("+00:00", "Z") if dt else None


def _to(u: User) -> UserResponse:
    return UserResponse(
        id=str(u.id),
        email=u.email,
        fullName=u.full_name,
        age=u.age,
        region=u.region,
        gender=u.gender,
        maritalStatus=u.marital_status,
        role=u.role,
        isActive=u.is_active,
        createdAt=_iso(u.created_at),
        updatedAt=_iso(u.updated_at),
    )


async def _require_full_put(request: Request):
    """
    ТЗ: PUT = full update.
    - отсутствие ключа => 422
    - наличие ключа со значением null => очистка (ok для nullable)
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    missing = [k for k in REQUIRED_PUT_KEYS if k not in body]
    if missing:
        return validation_failed(
            request,
            [{"field": k, "issue": "field is required", "rejectedValue": None} for k in missing],
        )
    return body


@router.get("/me", response_model=UserResponse)
def me(current: User = Depends(get_current_user)):
    return _to(current)


@router.put("/me", response_model=UserResponse)
async def update_me(
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    raw = await _require_full_put(request)
    if not isinstance(raw, dict):
        return raw  # это JSONResponse 422 из errors.py

    data = UserUpdateRequest(**raw)
    updated = users_service.update_user_full(db, current, data)
    return _to(updated)


@router.get("/{id}", response_model=UserResponse)
def get_by_id(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if current.role != "ADMIN" and str(current.id) != id:
        raise HTTPException(status_code=403, detail="Forbidden")

    u = users_service.get_user(db, id)
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    return _to(u)


@router.put("/{id}", response_model=UserResponse)
async def update_by_id(
    id: str,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    raw = await _require_full_put(request)
    if not isinstance(raw, dict):
        return raw

    # USER: только себя + нельзя role/isActive
    if current.role != "ADMIN":
        if str(current.id) != id:
            raise HTTPException(status_code=403, detail="Forbidden")
        if "role" in raw or "isActive" in raw:
            raise HTTPException(status_code=403, detail="Forbidden")

        data = UserUpdateRequest(**raw)
        updated = users_service.update_user_full(db, current, data)
        return _to(updated)

    # ADMIN
    u = users_service.get_user(db, id)
    if not u:
        raise HTTPException(status_code=404, detail="Not found")

    data = AdminUserUpdateRequest(**raw)
    updated = users_service.admin_update_user_full(db, u, data)
    return _to(updated)


@router.get("", response_model=UsersListResponse)
def list_all(
    page: int = 0,
    size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if page < 0 or size < 1 or size > 100:
        raise HTTPException(status_code=422, detail="Invalid pagination")

    items, total = users_service.list_users(db, page, size)
    return UsersListResponse(
        items=[_to(x) for x in items],
        total=total,
        page=page,
        size=size,
    )


@router.post("", response_model=UserResponse, status_code=201)
def admin_create(
    data: AdminUserCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if users_service.get_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email already exists")
    u = users_service.admin_create_user(db, data)
    return _to(u)


@router.delete("/{id}", status_code=204)
def admin_delete(
    id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    u = users_service.get_user(db, id)
    if not u:
        raise HTTPException(status_code=404, detail="Not found")

    users_service.deactivate_user(db, u)
    return Response(status_code=204)
