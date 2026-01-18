"""
Вся логика безопасности:
- хеширование паролей
- создание JWT
"""

from datetime import datetime, timedelta
from jose import jwt
from passlib.hash import bcrypt
from app.core.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_SECONDS


def hash_password(password: str) -> str:
    """Хешируем пароль перед сохранением в БД"""
    return bcrypt.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Проверяем пароль при логине"""
    return bcrypt.verify(password, hashed)


def create_access_token(user_id: str, role: str) -> str:
    """
    Генерируем JWT-токен.
    payload строго по ТЗ: sub, role, iat, exp
    """
    payload = {
        "sub": user_id,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXPIRE_SECONDS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
