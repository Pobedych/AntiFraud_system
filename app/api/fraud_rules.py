from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.fraud_rule import (
    FraudRuleCreateRequest,
    FraudRuleResponse,
)
from app.services.fraud_rules import create_rule

router = APIRouter(prefix="/api/v1/fraud-rules", tags=["fraud-rules"])


@router.post("", response_model=FraudRuleResponse)
def create(data: FraudRuleCreateRequest, db: Session = Depends(get_db)):
    rule = create_rule(db, data)

    return FraudRuleResponse(
        id=str(rule.id),
        name=rule.name,
        description=rule.description,
        dslExpression=rule.dslExpression,
        enabled=rule.enabled,
        priority=rule.priority,
        createdAt=str(rule.createdAt),
        updatedAt=str(rule.updatedAt),
    )

