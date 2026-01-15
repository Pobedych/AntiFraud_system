from fastapi import FastAPI
from app.core.database import Base, engine
from app.routers import auth, users, fraud_rules, transactions
from app.services.admin_init import create_admin_if_not_exists
from contextlib import contextmanager


@contextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    create_admin_if_not_exists()
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/api/v1/ping")
def ping():
    return {"status": "ok"}

app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(users.router, prefix="/api/v1/users")
app.include_router(fraud_rules.router, prefix="/api/v1/fraud-rules")
app.include_router(transactions.router, prefix="/api/v1/transactions")