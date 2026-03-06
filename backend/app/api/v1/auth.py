"""Authentication API routes."""

from __future__ import annotations

import time

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import BadRequestException
from app.core.rate_limit import RATE_LIMITS, limiter
from app.models import User
from app.schemas import BaseResponse, LoginResponse, UserCreate, UserLogin, UserResponse
from app.services import UserService

router = APIRouter()

LOGIN_WINDOW_SECONDS = 60
MAX_LOGIN_ATTEMPTS = 10
_login_attempts: dict[str, list[float]] = {}


def _get_login_rate_key(request: Request, account: str) -> str:
    client_ip = request.client.host if request.client else "unknown"
    return f"{client_ip}:{account.lower()}"


def _is_rate_limited(key: str) -> bool:
    now = time.time()
    attempts = [t for t in _login_attempts.get(key, []) if now - t < LOGIN_WINDOW_SECONDS]
    _login_attempts[key] = attempts
    return len(attempts) >= MAX_LOGIN_ATTEMPTS


def _record_failed_attempt(key: str):
    now = time.time()
    attempts = [t for t in _login_attempts.get(key, []) if now - t < LOGIN_WINDOW_SECONDS]
    attempts.append(now)
    _login_attempts[key] = attempts


def _clear_attempts(key: str):
    _login_attempts.pop(key, None)


@limiter.limit(RATE_LIMITS["auth"])
@router.post("/register", response_model=BaseResponse)
def register(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.create(user_in)
    return BaseResponse(message="注册成功", data={"user_id": user.id})


@limiter.limit(RATE_LIMITS["auth"])
@router.post("/login", response_model=LoginResponse)
def login(user_in: UserLogin, request: Request, db: Session = Depends(get_db)):
    rate_key = _get_login_rate_key(request, user_in.account)

    user_service = UserService(db)
    user = user_service.authenticate(user_in.account, user_in.password)
    if not user:
        _record_failed_attempt(rate_key)
        if _is_rate_limited(rate_key):
            raise HTTPException(status_code=429, detail="Too many requests")
        raise BadRequestException(detail="账号或密码错误")

    if user.status != 1:
        raise BadRequestException(detail="账号已被禁用")

    _clear_attempts(rate_key)
    user_service.update_last_login(user.id, request.client.host if request.client else None)

    access_token = user_service.generate_token(user.id)
    return LoginResponse(
        user=UserResponse.model_validate(user),
        token={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 604800,
        },
    )


@limiter.limit(RATE_LIMITS["general"])
@router.get("/me", response_model=UserResponse)
def get_current_user_info(request: Request, current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@limiter.limit(RATE_LIMITS["general"])
@router.put("/me", response_model=BaseResponse)
def update_user_info(
    user_in: dict,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    from app.schemas import UserUpdate

    user_service.update(current_user.id, UserUpdate(**user_in))
    return BaseResponse(message="更新成功")


@limiter.limit(RATE_LIMITS["general"])
@router.get("/me/balance")
def get_user_balance(request: Request, current_user: User = Depends(get_current_user)):
    return {"balance": float(current_user.balance)}
