"""Rate limit configuration."""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    retry_after = getattr(exc, "retry_after", 60)
    return JSONResponse(
        status_code=429,
        content={
            "code": 429,
            "message": "Too many requests, please try again later.",
            "data": None,
            "path": str(request.url),
        },
        headers={"Retry-After": str(retry_after)},
    )


RATE_LIMITS = {
    "general": "60/minute",
    "auth": "10/minute",
    "content": "20/minute",
    "payment": "15/minute",
}
