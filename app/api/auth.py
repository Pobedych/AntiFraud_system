from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    AuthUserResponse,
)
from app.services import auth as auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register(db, data)
    token, _ = auth_service.login(db, data.email, data.password)

    return AuthResponse(
        accessToken=token,
        expiresIn=3600,
        user=AuthUserResponse(
            id=str(user.id),
            email=user.email,
            fullName=user.fullName,
            age=user.age,
            region=user.region,
            gender=user.gender,
            maritalStatus=user.maritalStatus,
            role=user.role,
            isActive=user.isActive,
            createdAt=str(user.createdAt),
            updatedAt=str(user.updatedAt),
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    result = auth_service.login(db, data.email, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token, user = result

    return AuthResponse(
        accessToken=token,
        expiresIn=3600,
        user=AuthUserResponse(
            id=str(user.id),
            email=user.email,
            fullName=user.fullName,
            age=user.age,
            region=user.region,
            gender=user.gender,
            maritalStatus=user.maritalStatus,
            role=user.role,
            isActive=user.isActive,
            createdAt=str(user.createdAt),
            updatedAt=str(user.updatedAt),
        ),
    )
