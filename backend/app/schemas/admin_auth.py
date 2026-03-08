from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import TokenResponse


class AdminLogin(BaseModel):
    account: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: Optional[str]
    nickname: Optional[str]
    role: str
    status: int
    created_at: datetime


class AdminLoginResponse(BaseModel):
    user: AdminUserResponse
    token: TokenResponse
