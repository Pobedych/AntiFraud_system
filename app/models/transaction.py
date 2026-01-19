import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Numeric, JSON
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)

    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    timestamp = Column(DateTime, nullable=False)

    status = Column(String, nullable=False)   # APPROVED/DECLINED
    is_fraud = Column(Boolean, default=False)

    merchant_id = Column(String(64), nullable=True)
    merchant_category_code = Column(String(4), nullable=True)
    ip_address = Column(String(64), nullable=True)
    device_id = Column(String(128), nullable=True)
    channel = Column(String, nullable=True)

    location = Column(JSON, nullable=True)
    metadata_ = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
