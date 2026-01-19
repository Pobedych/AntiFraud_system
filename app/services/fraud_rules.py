from sqlalchemy.orm import Session
from sqlalchemy import asc
from app.models.fraud_rule import FraudRule
from app.core.redis import cache_invalidate_active_rules


def get_rule(db: Session, rid: str):
    return db.query(FraudRule).filter(FraudRule.id == rid).first()


def get_by_name(db: Session, name: str):
    return db.query(FraudRule).filter(FraudRule.name == name).first()


def list_rules(db: Session):
    return db.query(FraudRule).order_by(asc(FraudRule.priority), asc(FraudRule.id)).all()


def create_rule(db: Session, data):
    rule = FraudRule(
        name=data.name,
        description=data.description,
        dsl_expression=data.dslExpression,
        enabled=data.enabled,
        priority=data.priority,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    cache_invalidate_active_rules()
    return rule


def update_rule(db: Session, rule: FraudRule, data):
    rule.name = data.name
    rule.description = data.description
    rule.dsl_expression = data.dslExpression
    rule.enabled = data.enabled
    rule.priority = data.priority
    db.add(rule)
    db.commit()
    db.refresh(rule)
    cache_invalidate_active_rules()
    return rule


def disable_rule(db: Session, rule: FraudRule):
    if rule.enabled:
        rule.enabled = False
        db.add(rule)
        db.commit()
        cache_invalidate_active_rules()
