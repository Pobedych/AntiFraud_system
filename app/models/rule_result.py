"""
Результат применения одного правила к одной транзакции.
Обязательно сохраняется для воспроизводимости.
"""

import uuid
from sqlalchemy import Column, String, Boolean, Integer
from app.core.database import Base


class RuleResult(Base):
    __tablename__ = "rule_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, nullable=False)

    rule_id = Column(String, nullable=False)
    rule_name = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)

    matched = Column(Boolean, nullable=False)
    description = Column(String, nullable=False)
