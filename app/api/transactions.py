from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionCreateRequest,
    TransactionDecisionResponse,
    TransactionResponse,
    RuleResultResponse,
    TransactionsListResponse,
    BatchTransactionRequest,
    BatchTransactionResponse,
    BatchItemResult,
)
from app.services.transactions import create_transaction_tier0, get_transaction_with_results

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


def _iso(dt):
    # Transaction.timestamp и created_at храним как datetime
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def _tx_to_response(tx: Transaction) -> TransactionResponse:
    return TransactionResponse(
        id=str(tx.id),
        userId=str(tx.user_id),
        amount=float(tx.amount),
        currency=tx.currency,
        status=tx.status,
        isFraud=bool(tx.is_fraud),
        timestamp=_iso(tx.timestamp),
        createdAt=_iso(tx.created_at),

        merchantId=tx.merchant_id,
        merchantCategoryCode=tx.merchant_category_code,
        ipAddress=tx.ip_address,
        deviceId=tx.device_id,
        channel=tx.channel,
        location=tx.location,
        metadata=tx.extra,
    )


def _results_to_schema(results) -> list[RuleResultResponse]:
    return [
        RuleResultResponse(
            ruleId=r.rule_id,
            ruleName=r.rule_name,
            priority=r.priority,
            enabled=r.enabled,
            matched=r.matched,
            description=r.description,
        )
        for r in results
    ]


@router.post("", response_model=TransactionDecisionResponse, status_code=201)
def create_transaction(
    data: TransactionCreateRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """
    Tier 0:
    - matched=false для всех правил
    - status APPROVED (так как нет совпадений)
    - ruleResults полный список активных правил (enabled=true) в порядке priority,id
    """
    # ADMIN обязан передавать userId
    if current.role == "ADMIN":
        if not data.userId:
            raise HTTPException(status_code=422, detail="userId is required for ADMIN")
        target_user = db.query(User).filter(User.id == data.userId).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        if not target_user.is_active:
            raise HTTPException(status_code=403, detail="User deactivated")
        user_id = str(target_user.id)
    else:
        # USER: игнорируем userId из тела
        user_id = str(current.id)

    tx, results = create_transaction_tier0(db, user_id, data)

    return TransactionDecisionResponse(
        transaction=_tx_to_response(tx),
        ruleResults=_results_to_schema(results),
    )


@router.get("/{id}", response_model=TransactionDecisionResponse)
def get_transaction(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    tx, results = get_transaction_with_results(db, id)
    if not tx:
        raise HTTPException(status_code=404, detail="Not found")

    if current.role != "ADMIN" and str(tx.user_id) != str(current.id):
        raise HTTPException(status_code=403, detail="Forbidden")

    return TransactionDecisionResponse(
        transaction=_tx_to_response(tx),
        ruleResults=_results_to_schema(results),
    )


@router.get("", response_model=TransactionsListResponse)
def list_transactions(
    page: int = 0,
    size: int = 20,
    userId: str | None = None,
    status: str | None = None,
    isFraud: bool | None = None,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """
    Упрощённый листинг (Tier0):
    - USER видит только свои
    - ADMIN видит все, может фильтровать по userId
    - сортировка по времени операции (timestamp desc) по ТЗ
    """
    if page < 0 or size < 1 or size > 100:
        raise HTTPException(status_code=422, detail="Invalid pagination")

    q = db.query(Transaction)

    if current.role != "ADMIN":
        q = q.filter(Transaction.user_id == str(current.id))
    else:
        if userId:
            q = q.filter(Transaction.user_id == userId)

    if status:
        q = q.filter(Transaction.status == status)
    if isFraud is not None:
        q = q.filter(Transaction.is_fraud == isFraud)

    total = q.count()
    items = (
        q.order_by(desc(Transaction.timestamp))
        .offset(page * size)
        .limit(size)
        .all()
    )

    return TransactionsListResponse(
        items=[_tx_to_response(x) for x in items],
        total=total,
        page=page,
        size=size,
    )


@router.post("/batch", response_model=BatchTransactionResponse)
def batch_create(
    body: BatchTransactionRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """
    Батч:
    - каждый элемент обрабатывается независимо
    - 201 если все ок, 207 если частично
    - ошибки не откатывают успешные (мы коммитим поэлементно в сервисе)
    """
    results: list[BatchItemResult] = []
    has_errors = False

    for idx, item in enumerate(body.items):
        try:
            # повторяем логику userId
            if current.role == "ADMIN":
                if not item.userId:
                    raise HTTPException(422, "userId is required for ADMIN")
                target_user = db.query(User).filter(User.id == item.userId).first()
                if not target_user:
                    raise HTTPException(404, "User not found")
                if not target_user.is_active:
                    raise HTTPException(403, "User deactivated")
                user_id = str(target_user.id)
            else:
                user_id = str(current.id)

            tx, rr = create_transaction_tier0(db, user_id, item)
            decision = TransactionDecisionResponse(
                transaction=_tx_to_response(tx),
                ruleResults=_results_to_schema(rr),
            )
            results.append(BatchItemResult(index=idx, decision=decision))
        except HTTPException as e:
            has_errors = True
            # В батче в error нужен машиночитаемый code (в ТЗ пример VALIDATION_FAILED)
            code = "VALIDATION_FAILED" if e.status_code == 422 else "ERROR"
            results.append(
                BatchItemResult(
                    index=idx,
                    error={"code": code, "message": str(e.detail)},
                )
            )

    # 201 если без ошибок, иначе 207
    # FastAPI позволяет вернуть Response(status_code=207, ...)
    from fastapi.responses import JSONResponse
    payload = BatchTransactionResponse(items=results).model_dump()

    if has_errors:
        return JSONResponse(status_code=207, content=payload)
    return JSONResponse(status_code=201, content=payload)
