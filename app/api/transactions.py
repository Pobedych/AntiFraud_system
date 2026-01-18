from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.transaction import (
    TransactionCreateRequest,
    TransactionDecisionResponse,
    TransactionResponse,
)
from app.services.transactions import create_transaction

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.post("", response_model=TransactionDecisionResponse)
def create(
    data: TransactionCreateRequest,
    db: Session = Depends(get_db),
):
    user_id = data.userId or "system"
    tx = create_transaction(db, data, user_id)

    return {
        "transaction": TransactionResponse(
            id=str(tx.id),
            userId=tx.userId,
            amount=tx.amount,
            currency=tx.currency,
            status=tx.status,
            isFraud=tx.isFraud,
            timestamp=tx.timestamp,
            createdAt=str(tx.createdAt),
            merchantId=tx.merchantId,
            merchantCategoryCode=tx.merchantCategoryCode,
            ipAddress=tx.ipAddress,
            deviceId=tx.deviceId,
            channel=tx.channel,
            location=tx.location,
            metadata=tx.metadata,
        ),
        "ruleResults": [],
    }
