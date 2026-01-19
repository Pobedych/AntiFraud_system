"""
Pydantic-схемы для аутентификации:
- регистрация
- логин
- ответ с JWT
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=72)
    fullName: str = Field(..., min_length=2, max_length=200)

    age: int | None = Field(None, ge=18, le=120)
    region: str | None = Field(None, max_length=32)
    gender: str | None = Field(None, pattern="^(MALE|FEMALE)$")
    maritalStatus: str | None = Field(None, pattern="^(SINGLE|MARRIED|DIVORCED|WIDOWED)$")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=72)


class AuthUserResponse(BaseModel):
    id: str
    email: EmailStr
    fullName: str
    age: int | None
    region: str | None
    gender: str | None
    maritalStatus: str | None
    role: str
    isActive: bool
    createdAt: str | None
    updatedAt: str | None


class AuthResponse(BaseModel):
    accessToken: str
    expiresIn: int
    user: AuthUserResponse

