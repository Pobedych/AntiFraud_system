"""
Антифрод-правило.
DSL НЕ парсится (Tier 0), хранится как строка.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime
from app.core.database import Base


class FraudRule(Base):
    __tablename__ = "fraud_rules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(120), unique=True, nullable=False)
    description = Column(String(500), nullable=True)

    dsl_expression = Column(String(2000), nullable=False)

    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=100)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
