from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UsersListResponse, UserResponse
from app.services.users import list_users

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
