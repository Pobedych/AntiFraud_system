from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import JWT_SECRET, JWT_ALGORITHM
from app.core.database import get_db
from app.models.user import User

bearer = HTTPBearer(auto_error=False)

def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(401, "Unauthorized")

    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Unauthorized")

    uid = payload.get("sub")
    if not uid:
        raise HTTPException(401, "Unauthorized")

    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(401, "Unauthorized")
    if not user.is_active:
        raise HTTPException(403, "Forbidden")
    return user

def require_admin(u: User = Depends(get_current_user)) -> User:
    if u.role != "ADMIN":
        raise HTTPException(403, "Forbidden")
    return u
