from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password
import os


def create_admin_if_not_exists():
    db: Session = SessionLocal()

    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    full_name = os.getenv("ADMIN_FULLNAME")

    if not email or not password:
        return

    admin = db.query(User).filter(User.email == email).first()
    if admin:
        return

    admin = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role="ADMIN",
        is_active=True
    )

    db.add(admin)
    db.commit()
    db.close()
