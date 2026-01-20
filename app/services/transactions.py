from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import asc

from app.models.transaction import Transaction
from app.models.rule_result import RuleResult
from app.models.fraud_rule import FraudRule
from app.dsl.simple_engine import evaluate_simple
from app.models.user import User


from app.core.redis import cache_get_active_rules, cache_set_active_rules


def _load_active_rules(db: Session) -> list[dict]:
    """
    Сначала пробуем Redis.
    В кэше храним только нужные поля, чтобы не сериализовать ORM.
    """
    cached = cache_get_active_rules()
    if cached is not None:
        return cached

    rules = (
        db.query(FraudRule)
        .filter(FraudRule.enabled == True)
        .order_by(asc(FraudRule.priority), asc(FraudRule.id))
        .all()
    )
    data = [
        {
            "id": str(r.id),
            "name": r.name,
            "priority": r.priority,
            "enabled": r.enabled,
            "dsl": r.dsl_expression,
        }
        for r in rules
    ]
    cache_set_active_rules(data, ttl_seconds=30)
    return data


def create_transaction_tier0(db: Session, user_id: str, data) -> tuple[Transaction, list[RuleResult]]:
    ts = data.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)

    tx = Transaction(
        user_id=user_id,
        amount=data.amount,
        currency=data.currency,
        timestamp=ts,
        status="APPROVED",
        is_fraud=False,
        merchant_id=data.merchantId,
        merchant_category_code=data.merchantCategoryCode,
        ip_address=data.ipAddress,
        device_id=data.deviceId,
        channel=data.channel,
        location=data.location.model_dump() if data.location else None,
        extra=data.metadata,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    rules = _load_active_rules(db)
    results: list[RuleResult] = []

    tx_ctx = {
        "amount": float(tx.amount),
        "currency": tx.currency,
        "merchantId": tx.merchant_id,
        "merchantCategoryCode": tx.merchant_category_code,
        "ipAddress": tx.ip_address,
        "deviceId": tx.device_id,
        "channel": tx.channel,
        "location": tx.location or {},
    }

    # user context (Tier 5)
    user = db.query(User).filter(User.id == user_id).first()
    user_ctx = {
        "age": user.age if user else None,
        "region": user.region if user else None,
    }

    any_matched = False

    for r in rules:
        try:
            matched = evaluate_simple(r["dsl"], tx_ctx, user_ctx)
        except Exception:
            matched = False

        if matched:
            any_matched = True

        rr = RuleResult(
            transaction_id=str(tx.id),
            rule_id=r["id"],
            rule_name=r["name"],
            priority=r["priority"],
            enabled=r["enabled"],
            matched=matched,
            description=f"Evaluated: {r['dsl']}",
        )
        db.add(rr)
        results.append(rr)

    if any_matched:
        tx.status = "DECLINED"
        tx.is_fraud = True

    db.commit()
    return tx, results


def get_transaction_with_results(db: Session, tx_id: str):
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        return None, []
    results = db.query(RuleResult).filter(RuleResult.transaction_id == tx_id).order_by(
        asc(RuleResult.priority), asc(RuleResult.rule_id)
    ).all()
    return tx, results
