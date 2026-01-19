"""
Точка входа приложения.
Создает таблицы и начального администратора.
"""

from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.core.database import Base, engine, SessionLocal
from app.core.errors import register_error_handlers
from app.core.config import ADMIN_EMAIL, ADMIN_FULLNAME, ADMIN_PASSWORD
from app.core.security import hash_password

from app.models.user import User
from app.api import ping, auth, users, fraud_rules, transactions, ui

app = FastAPI(title="AntiFraud")

register_error_handlers(app)

# создаём таблицы
Base.metadata.create_all(bind=engine)

def ensure_admin():
    db: Session = SessionLocal()
    admin = db.query(User).filter(User.role == "ADMIN").first()
    if not admin:
        db.add(User(
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            full_name=ADMIN_FULLNAME,
            role="ADMIN",
            is_active=True,
        ))
        db.commit()
    db.close()

ensure_admin()

# роутеры
app.include_router(ping.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(fraud_rules.router)
app.include_router(transactions.router)
app.include_router(ui.router)
