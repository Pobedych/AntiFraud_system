from sqlalchemy.orm import Session

from app.models.transaction import Transaction


def create_transaction(db: Session, data, user_id: str):
    tx = Transaction(
        userId=user_id,
        amount=data.amount,
        currency=data.currency,
        timestamp=data.timestamp,
        status="APPROVED",
        isFraud=False,
        merchantId=data.merchantId,
        merchantCategoryCode=data.merchantCategoryCode,
        ipAddress=data.ipAddress,
        deviceId=data.deviceId,
        channel=data.channel,
        location=data.location.model_dump() if data.location else None,
        metadata=data.metadata,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx
