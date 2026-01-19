from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UsersListResponse, UserResponse
from app.services.users import list_users, get_user_by_id
from app.core.security import get_current_claims


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("", response_model=UsersListResponse)
def get_users(
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db),
):
    skip = (page - 1) * size
    items, total = list_users(db, skip, size)

    return {
        "items": [
            UserResponse(
                id=str(u.id),
                email=u.email,
                fullName=u.fullName,
                age=u.age,
                region=u.region,
                gender=u.gender,
                maritalStatus=u.maritalStatus,
                role=u.role,
                isActive=u.isActive,
                createdAt=str(u.createdAt),
                updatedAt=str(u.updatedAt),
            )
            for u in items
        ],
        "total": total,
        "page": page,
        "size": size,
    }

@router.get("/me", response_model=UserResponse)
def get_me(
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.isActive:
        # По ТЗ деактивированный пользователь не может пользоваться системой
        raise HTTPException(status_code=423, detail="User is deactivated")

    return UserResponse(
        id=str(user.id),
        email=user.email,
        fullName=user.fullName,
        age=user.age,
        region=user.region,
        gender=user.gender,
        maritalStatus=user.maritalStatus,
        role=user.role,
        isActive=user.isActive,
        createdAt=user.createdAt.isoformat() + "Z" if hasattr(user.createdAt, "isoformat") else str(user.createdAt),
        updatedAt=user.updatedAt.isoformat() + "Z" if hasattr(user.updatedAt, "isoformat") else str(user.updatedAt),
    )