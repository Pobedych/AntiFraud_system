"""
Схемы антифрод-правил.
DSL здесь — просто строка (Tier 0).
"""

from pydantic import BaseModel, Field


class FraudRuleBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)
    description: str | None = Field(None, max_length=500)
    dslExpression: str = Field(..., min_length=3, max_length=2000)
    enabled: bool = True
    priority: int = Field(100, ge=1)


class FraudRuleCreateRequest(FraudRuleBase):
    pass


class FraudRuleUpdateRequest(FraudRuleBase):
    """
    PUT — полное обновление
    """
    pass


class FraudRuleResponse(BaseModel):
    id: str
    name: str
    description: str | None
    dslExpression: str
    enabled: bool
    priority: int
    createdAt: str
    updatedAt: str


class FraudRuleValidateRequest(BaseModel):
    dslExpression: str = Field(..., min_length=3, max_length=2000)


class DslError(BaseModel):
    code: str
    message: str
    position: int | None = None
    near: str | None = None


class FraudRuleValidateResponse(BaseModel):
    isValid: bool
    normalizedExpression: str | None
    errors: list[DslError]
