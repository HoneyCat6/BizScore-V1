from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from dynamo import create_tables
from routers import auth, wallet, transactions, accounting, scoring, report, chat
from services.data_simulator import seed_personas


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DynamoDB tables
    try:
        create_tables()
        seed_personas()  # Seed demo accounts
        print("DynamoDB tables ready.")
    except Exception as e:
        print(f"Warning: Could not create DynamoDB tables: {e}")
    yield


app = FastAPI(
    title=settings.app_name,
    description="Business e-wallet with built-in accounting and performance scoring for financial inclusion",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router)
app.include_router(wallet.router)
app.include_router(transactions.router)
app.include_router(accounting.router)
app.include_router(scoring.router)
app.include_router(report.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}
