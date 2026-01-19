from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import asc

from app.models.transaction import Transaction
from app.models.rule_result import RuleResult
from app.models.fraud_rule import FraudRule

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
    """
    Tier 0: DSL не считаем, matched=false всегда.
    Но ruleResults обязаны быть:
    - полные (для всех enabled правил)
    - в порядке priority,id (мы так и грузим)
    - description не пустой
    - сохраняем в БД для воспроизводимости
    """
    # timestamp: в схеме приходит строка ISO
    ts = datetime.fromisoformat(data.timestamp.replace("Z", "+00:00"))
    if ts > datetime.now(timezone.utc).replace(tzinfo=timezone.utc) + timedelta(minutes=5):
        # лучше пусть pydantic валидирует, но оставим минимально
        pass

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
        metadata=data.metadata_,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    rules = _load_active_rules(db)
    results: list[RuleResult] = []

    for r in rules:
        rr = RuleResult(
            transaction_id=str(tx.id),
            rule_id=r["id"],
            rule_name=r["name"],
            priority=r["priority"],
            enabled=r["enabled"],
            matched=False,
            description=f"Tier0: not evaluated ({r['dsl']})",
        )
        db.add(rr)
        results.append(rr)

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
