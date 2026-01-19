from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, AuthUserResponse
from app.models.user import User
from app.services import auth as auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _iso(dt):
    return dt.isoformat().replace("+00:00", "Z") if dt else None


def _user_payload(u: User) -> AuthUserResponse:
    return AuthUserResponse(
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


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # 409 если email занят
    exists = db.query(User).filter(User.email == data.email).first()
    if exists:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = auth_service.register(db, data)
    token, _ = auth_service.authenticate(db, data.email, data.password)

    return AuthResponse(accessToken=token, expiresIn=3600, user=_user_payload(user))


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    result = auth_service.authenticate(db, data.email, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token, user = result
    if token == "DEACTIVATED":
        raise HTTPException(status_code=423, detail="User deactivated")

    return AuthResponse(accessToken=token, expiresIn=3600, user=_user_payload(user))
