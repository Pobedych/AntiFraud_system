from sqlalchemy.orm import Session

from app.models.user import User


def list_users(db: Session, skip: int, limit: int):
    items = db.query(User).offset(skip).limit(limit).all()
    total = db.query(User).count()
    return items, total


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()