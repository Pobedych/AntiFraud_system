from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field, field_validator, model_validator


class Location(BaseModel):
    country: str = Field(..., pattern=r"^[A-Z]{2}$")  # ISO 3166-1 alpha-2 (2 заглавные буквы)
    city: str | None = Field(None, max_length=128)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)

    @model_validator(mode="after")
    def lat_lon_pair(self):
        """
        ТЗ: latitude обязательно вместе с longitude и наоборот.
        """
        lat = self.latitude
        lon = self.longitude
        if (lat is None) != (lon is None):
            raise ValueError("latitude and longitude must be provided together")
        return self


class TransactionCreateRequest(BaseModel):
    """
    userId:
      - ADMIN: обязателен (проверяем в роутере)
      - USER: игнорируем, берём sub из JWT
    """
    userId: str | None = None

    amount: float = Field(..., ge=0.01, le=999_999_999.99)
    currency: str = Field(..., pattern=r"^[A-Z]{3}$")  # ISO 4217 (3 заглавные буквы)

    # Сразу парсим как datetime (Pydantic умеет ISO 8601 строки)
    timestamp: datetime

    merchantId: str | None = Field(None, max_length=64)
    merchantCategoryCode: str | None = Field(None, pattern=r"^\d{4}$")  # MCC 4 цифры
    ipAddress: str | None = Field(None, max_length=64)
    deviceId: str | None = Field(None, max_length=128)
    channel: str | None = Field(None, pattern=r"^(WEB|MOBILE|POS|OTHER)$")

    location: Location | None = None
    metadata: dict | None = None

    @field_validator("timestamp")
    @classmethod
    def timestamp_not_too_future(cls, v: datetime):
        """
        ТЗ: timestamp не более 5 минут в будущем.
        """
        # приводим к aware UTC
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if v > now + timedelta(minutes=5):
            raise ValueError("timestamp must not be more than 5 minutes in the future")
        return v


class TransactionResponse(BaseModel):
    id: str
    userId: str
    amount: float
    currency: str
    status: str
    isFraud: bool
    timestamp: str
    createdAt: str

    merchantId: str | None
    merchantCategoryCode: str | None
    ipAddress: str | None
    deviceId: str | None
    channel: str | None
    location: dict | None
    metadata: dict | None


class RuleResultResponse(BaseModel):
    ruleId: str
    ruleName: str
    priority: int
    enabled: bool
    matched: bool
    description: str


class TransactionDecisionResponse(BaseModel):
    transaction: TransactionResponse
    ruleResults: list[RuleResultResponse]


class TransactionsListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    size: int


class BatchTransactionRequest(BaseModel):
    items: list[TransactionCreateRequest] = Field(..., min_items=1, max_items=500)


class BatchItemResult(BaseModel):
    index: int
    decision: TransactionDecisionResponse | None = None
    error: dict | None = None


class BatchTransactionResponse(BaseModel):
    items: list[BatchItemResult]
