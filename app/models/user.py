"""
Модель пользователя.
USER / ADMIN различаются только полем role.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(254), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    full_name = Column(String(200), nullable=False)
    age = Column(Integer, nullable=True)
    region = Column(String(32), nullable=True)
    gender = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)

    role = Column(String, nullable=False, default="USER")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
