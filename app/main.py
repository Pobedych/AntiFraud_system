"""
Точка входа приложения.
Создает таблицы и начального администратора.
"""

from fastapi import FastAPI
from app.core.database import Base, engine, SessionLocal
from app.core.config import ADMIN_EMAIL, ADMIN_FULLNAME, ADMIN_PASSWORD
from app.core.security import hash_password
from app.models.user import User
from app.api import ping, auth, users, fraud_rules, transactions

app = FastAPI(title="AntiFraud Service")

# Подключаем все роутеры
app.include_router(ping.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(fraud_rules.router)
app.include_router(transactions.router)

# Создаем таблицы
Base.metadata.create_all(bind=engine)


def create_admin():
    """
    Создаем администратора при старте, если его еще нет.
    Это КРИТИЧНО для автотестов.
    """
    db = SessionLocal()
    exists = db.query(User).filter(User.role == "ADMIN").first()
    if not exists:
        admin = User(
            email=ADMIN_EMAIL,
            fullName=ADMIN_FULLNAME,
            password_hash=hash_password(ADMIN_PASSWORD),
            role="ADMIN",
        )
        db.add(admin)
        db.commit()
    db.close()


create_admin()
