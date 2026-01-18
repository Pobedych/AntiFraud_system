"""
Схемы пользователей.
Используются для:
- GET /users/*
- PUT /users/*
- POST /users (ADMIN)
"""

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    fullName: str = Field(..., min_length=2, max_length=200)
    age: int | None = Field(None, ge=18, le=120)
    region: str | None = Field(None, max_length=32)
    gender: str | None = Field(None, pattern="^(MALE|FEMALE)$")
    maritalStatus: str | None = Field(
        None, pattern="^(SINGLE|MARRIED|DIVORCED|WIDOWED)$"
    )


class UserResponse(UserBase):
    """
    Ответ при получении пользователя
    """
    id: str
    email: EmailStr
    role: str
    isActive: bool
    createdAt: str
    updatedAt: str


class UserUpdateRequest(UserBase):
    """
    PUT /users/me и PUT /users/{id}

    ⚠️ PUT = полное обновление:
    все поля ОБЯЗАНЫ присутствовать.
    """
    pass


class AdminUserCreateRequest(UserBase):
    """
    POST /users (ADMIN)
    """
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=72)
    role: str = Field(..., pattern="^(USER|ADMIN)$")


class AdminUserUpdateRequest(UserUpdateRequest):
    """
    PUT /users/{id} для ADMIN
    """
    role: str | None = Field(None, pattern="^(USER|ADMIN)$")
    isActive: bool | None = None


class UsersListResponse(BaseModel):
    """
    GET /users (пагинация)
    """
    items: list[UserResponse]
    total: int
    page: int
    size: int
