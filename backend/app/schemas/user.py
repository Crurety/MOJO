from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, validator
import re


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    nickname: Optional[str] = Field(None, max_length=50)
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v:
            # 验证手机号格式
            if not re.match(r'^1[3-9]\d{9}$', v):
                raise ValueError('手机号格式不正确')
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        # 密码强度验证：至少包含字母和数字
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[^\s]{6,}$', v):
            raise ValueError('密码至少包含6个字符，且必须包含字母和数字')
        return v


class UserLogin(BaseModel):
    account: str = Field(..., description="邮箱或手机号")
    password: str
    
    @field_validator('account')
    @classmethod
    def validate_account(cls, v):
        # 验证账号是邮箱或手机号
        if not (re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v) or re.match(r'^1[3-9]\d{9}$', v)):
            raise ValueError('账号必须是邮箱或手机号')
        return v


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = Field(None, max_length=500)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: Optional[str]
    phone: Optional[str]
    nickname: Optional[str]
    avatar: Optional[str]
    status: int
    balance: float
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(BaseModel):
    user: UserResponse
    token: TokenResponse
