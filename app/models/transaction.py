"""
Транзакция.
DSL применяется, но в Tier 0 всегда matched = false.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Float, DateTime
from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)

    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)

    status = Column(String, nullable=False)  # APPROVED / DECLINED
    is_fraud = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
