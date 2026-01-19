"""
Вся логика безопасности:
- хеширование паролей
- создание JWT
"""

from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.hash import bcrypt
from app.core.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_SECONDS
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer(auto_error=False)

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
        "iat": datetime.now(),
        "exp": datetime.now() + timedelta(seconds=JWT_EXPIRE_SECONDS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid")


def get_current_claims(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing token")
    return decode_token(creds.credentials)







