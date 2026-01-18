from sqlalchemy.orm import Session

from app.models.fraud_rule import FraudRule


def create_rule(db: Session, data):
    rule = FraudRule(
        name=data.name,
        description=data.description,
        dslExpression=data.dslExpression,
        enabled=data.enabled,
        priority=data.priority,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule
