"""Unified exception handlers."""

import os
import traceback

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import AppException
from app.core.logging import logger


async def app_exception_handler(request: Request, exc: AppException):
    logger.error("AppException: %s - Code: %s", exc.detail, exc.code)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.detail,
            "data": None,
            "path": str(request.url),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]

    logger.warning("Validation error: %s", errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "Validation failed",
            "data": {"errors": errors},
            "path": str(request.url),
        },
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error("Database error: %s", str(exc))
    logger.error(traceback.format_exc())

    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "code": 409,
                "message": "Data conflict",
                "data": None,
                "path": str(request.url),
            },
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "Database error",
            "data": None,
            "path": str(request.url),
        },
    )


async def redis_exception_handler(request: Request, exc: RedisError):
    logger.error("Redis error: %s", str(exc))
    logger.error(traceback.format_exc())

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "code": 503,
            "message": "Cache service unavailable",
            "data": None,
            "path": str(request.url),
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", str(exc))
    logger.error(traceback.format_exc())

    if os.getenv("ENVIRONMENT") == "development":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "message": "Internal server error",
                "data": {"error": str(exc), "traceback": traceback.format_exc()},
                "path": str(request.url),
            },
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "Internal server error",
            "data": None,
            "path": str(request.url),
        },
    )


def setup_exception_handlers(app):
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(RedisError, redis_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
