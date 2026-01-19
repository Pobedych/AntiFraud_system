from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.hash import bcrypt
from app.core.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_SECONDS

def hash_password(p: str) -> str:
    return bcrypt.hash(p)

def verify_password(p: str, h: str) -> bool:
    return bcrypt.verify(p, h)

def create_token(user_id: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=JWT_EXPIRE_SECONDS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
