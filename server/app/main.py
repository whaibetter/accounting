import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.dependencies import require_auth
from app.middleware import register_middlewares
from app.routers import account, bill, category, tag, statistics, export, import_data, auth, llm

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)

ENV = os.getenv("APP_ENV", "development")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="记账软件API",
    description="个人记账软件后端API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if ENV == "development" else None,
    redoc_url="/redoc" if ENV == "development" else None,
    openapi_url="/openapi.json" if ENV == "development" else None,
)

ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

register_middlewares(app)

app.include_router(auth.router)
app.include_router(account.router, dependencies=[Depends(require_auth)])
app.include_router(bill.router, dependencies=[Depends(require_auth)])
app.include_router(category.router, dependencies=[Depends(require_auth)])
app.include_router(tag.router, dependencies=[Depends(require_auth)])
app.include_router(statistics.router, dependencies=[Depends(require_auth)])
app.include_router(export.router, dependencies=[Depends(require_auth)])
app.include_router(import_data.router, dependencies=[Depends(require_auth)])
app.include_router(llm.router, dependencies=[Depends(require_auth)])


@app.get("/health", tags=["系统"])
def health_check():
    return {"status": "ok"}
