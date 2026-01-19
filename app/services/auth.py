from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_token
from app.models.user import User


def register(db: Session, data) -> User:
    """
    Создаём нового USER.
    Проверка уникальности email делается в роутере (409).
    """
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.fullName,
        age=data.age,
        region=data.region,
        gender=data.gender,
        marital_status=data.maritalStatus,
        role="USER",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str):
    """
    Возвращает (token, user) или None.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    if not user.is_active:
        # по ТЗ 423 на login
        return ("DEACTIVATED", user)

    if not verify_password(password, user.password_hash):
        return None

    token = create_token(str(user.id), user.role)
    return (token, user)
