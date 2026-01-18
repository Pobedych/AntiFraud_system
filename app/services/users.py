from sqlalchemy.orm import Session

from app.models.user import User


def list_users(db: Session, skip: int, limit: int):
    items = db.query(User).offset(skip).limit(limit).all()
    total = db.query(User).count()
    return items, total
