import os
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import AppException
from app.core.logging import logger
from app.core.rate_limit import limiter, rate_limit_handler
from app.models import Base

# Create tables only outside test runs.
if not os.getenv("TESTING"):
    Base.metadata.create_all(bind=engine)

logger.info("Starting %s v%s", settings.PROJECT_NAME, settings.VERSION)
logger.info("API base URL: %s", settings.API_V1_STR)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI platform API service",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info("Request: %s %s", request.method, request.url.path)

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info("Response: %s - %.4fs", response.status_code, process_time)
    return response


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.error("AppException: %s - Code: %s", exc.detail, exc.code)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.detail, "data": None},
    )


app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {"message": "AI platform API", "version": settings.VERSION, "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
