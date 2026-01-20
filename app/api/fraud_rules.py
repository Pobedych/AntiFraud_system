from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_admin
from app.schemas.fraud_rule import FraudRuleCreateRequest, FraudRuleUpdateRequest, FraudRuleResponse, FraudRuleValidateRequest, FraudRuleValidateResponse
from app.services import fraud_rules as svc
from app.dsl.simple_engine import validate_expression

router = APIRouter(prefix="/api/v1/fraud-rules", tags=["fraud-rules"])

def _iso(dt): return dt.isoformat().replace("+00:00", "Z") if dt else None
def _to(r):
    return FraudRuleResponse(
        id=str(r.id), name=r.name, description=r.description, dslExpression=r.dsl_expression,
        enabled=r.enabled, priority=r.priority, createdAt=_iso(r.created_at), updatedAt=_iso(r.updated_at),
    )

@router.post("", response_model=FraudRuleResponse, status_code=201)
def create(data: FraudRuleCreateRequest, db: Session = Depends(get_db), _=Depends(require_admin)):
    if svc.get_by_name(db, data.name):
        raise HTTPException(409, "Rule name already exists")
    return _to(svc.create_rule(db, data))


@router.get("", response_model=list[FraudRuleResponse])
def list_all(db: Session = Depends(get_db), _=Depends(require_admin)):
    return [_to(x) for x in svc.list_rules(db)]


@router.get("/{id}", response_model=FraudRuleResponse)
def get_one(id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    r = svc.get_rule(db, id)
    if not r: raise HTTPException(404, "Not found")
    return _to(r)


@router.put("/{id}", response_model=FraudRuleResponse)
def put(id: str, data: FraudRuleUpdateRequest, db: Session = Depends(get_db), _=Depends(require_admin)):
    r = svc.get_rule(db, id)
    if not r: raise HTTPException(404, "Not found")
    ex = svc.get_by_name(db, data.name)
    if ex and str(ex.id) != str(r.id):
        raise HTTPException(409, "Rule name already exists")
    return _to(svc.update_rule(db, r, data))


@router.delete("/{id}", status_code=204)
def delete(id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    r = svc.get_rule(db, id)
    if not r: raise HTTPException(404, "Not found")
    svc.disable_rule(db, r)
    return Response(status_code=204)


# Tier 0 validate: всегда 200, но isValid=false + DSL_UNSUPPORTED_TIER
@router.post("/validate", response_model=FraudRuleValidateResponse)
def validate(req: FraudRuleValidateRequest):
    res = validate_expression(req.dslExpression)
    return {
        "isValid": res.is_valid,
        "normalizedExpression": res.normalized if res.is_valid else None,
        "errors": [e.__dict__ for e in res.errors],
    }