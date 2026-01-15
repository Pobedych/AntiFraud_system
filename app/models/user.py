from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.core.database import Base

import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    fullname = Column(String, nullable=False)

    age = Column(Integer, nullable=False)
    region = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    material_status = Column(String, nullable=False)

    role = Column(String, nullable=False, default='USER')
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())