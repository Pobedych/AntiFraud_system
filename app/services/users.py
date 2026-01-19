from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.security import hash_password
from app.models.user import User


def get_user(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session, page: int, size: int):
    total = db.query(User).count()
    items = (
        db.query(User)
        .order_by(desc(User.created_at))
        .offset(page * size)
        .limit(size)
        .all()
    )
    return items, total


def update_user_full(db: Session, user: User, data) -> User:
    user.full_name = data.fullName
    user.age = data.age
    user.region = data.region
    user.gender = data.gender
    user.marital_status = data.maritalStatus
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def admin_update_user_full(db: Session, user: User, data) -> User:
    user.full_name = data.fullName
    user.age = data.age
    user.region = data.region
    user.gender = data.gender
    user.marital_status = data.maritalStatus

    if data.role is not None:
        user.role = data.role
    if data.isActive is not None:
        user.is_active = data.isActive

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def admin_create_user(db: Session, data) -> User:
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.fullName,
        age=data.age,
        region=data.region,
        gender=data.gender,
        marital_status=data.maritalStatus,
        role=data.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user: User) -> None:
    if user.is_active:
        user.is_active = False
        db.add(user)
        db.commit()
