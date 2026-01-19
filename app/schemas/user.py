from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    fullName: str = Field(..., min_length=2, max_length=200)
    age: int | None = Field(None, ge=18, le=120)
    region: str | None = Field(None, max_length=32)
    gender: str | None = Field(None, pattern="^(MALE|FEMALE)$")
    maritalStatus: str | None = Field(None, pattern="^(SINGLE|MARRIED|DIVORCED|WIDOWED)$")


class UserResponse(UserBase):
    id: str
    email: EmailStr
    role: str
    isActive: bool
    createdAt: str | None
    updatedAt: str | None


class UserUpdateRequest(UserBase):
    # PUT = full update (все поля обязаны быть в body)
    pass


class AdminUserCreateRequest(UserBase):
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=72)
    role: str = Field(..., pattern="^(USER|ADMIN)$")


class AdminUserUpdateRequest(UserUpdateRequest):
    # ADMIN может менять role/isActive (необязательные поля)
    role: str | None = Field(None, pattern="^(USER|ADMIN)$")
    isActive: bool | None = None


class UsersListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    size: int
