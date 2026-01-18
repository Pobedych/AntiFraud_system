from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


def register(db: Session, data):
    user = User(
        email=data.email,
        passwordHash=hash_password(data.password),
        fullName=data.fullName,
        age=data.age,
        region=data.region,
        gender=data.gender,
        maritalStatus=data.maritalStatus,
        role="USER",
        isActive=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    if not verify_password(password, user.passwordHash):
        return None

    token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role,
        }
    )
    return token, user
