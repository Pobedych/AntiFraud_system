from pydantic import BaseModel, Field


class Location(BaseModel):
    country: str = Field(..., min_length=2, max_length=2)
    city: str | None = Field(None, max_length=128)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)


class TransactionCreateRequest(BaseModel):
    """
    userId:
      - ADMIN: обязателен
      - USER: игнорируем, берём sub из JWT
    """
    userId: str | None = None

    amount: float = Field(..., ge=0.01, le=999_999_999.99)
    currency: str = Field(..., min_length=3, max_length=3)
    timestamp: str  # ISO 8601

    merchantId: str | None = Field(None, max_length=64)
    merchantCategoryCode: str | None = Field(None, min_length=4, max_length=4)
    ipAddress: str | None = Field(None, max_length=64)
    deviceId: str | None = Field(None, max_length=128)
    channel: str | None = Field(None, pattern="^(WEB|MOBILE|POS|OTHER)$")

    location: Location | None = None
    metadata: dict | None = None


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
