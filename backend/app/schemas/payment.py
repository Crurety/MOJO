from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from decimal import Decimal


class OrderCreate(BaseModel):
    order_type: str = Field(..., description="订单类型: permission/balance")
    product_name: str = Field(..., max_length=200)
    amount: Decimal = Field(..., gt=0, description="订单金额，必须大于0")
    payment_method: str = Field(..., description="支付方式: wechat/alipay/unionpay/balance")
    remark: Optional[str] = Field(None, max_length=500)
    
    @field_validator('order_type')
    @classmethod
    def validate_order_type(cls, v):
        if v not in ['permission', 'balance']:
            raise ValueError('订单类型必须是 permission 或 balance')
        return v
    
    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v):
        if v not in ['wechat', 'alipay', 'unionpay', 'balance']:
            raise ValueError('支付方式必须是 wechat、alipay、unionpay 或 balance')
        return v


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    order_no: str
    order_type: str
    product_name: str
    amount: Decimal
    payment_method: Optional[str]
    payment_no: Optional[str]
    status: int
    paid_at: Optional[datetime]
    created_at: datetime


class PaymentCallback(BaseModel):
    order_no: str
    payment_no: str
    payment_method: str
    amount: Decimal


class PermissionPurchase(BaseModel):
    permission_type: str = Field(..., description="权限类型: script/image/video/ad")
    payment_mode: str = Field(..., description="付费模式: per_use/monthly/yearly")
    count: Optional[int] = Field(None, description="购买次数(按次付费时必填)")
    payment_method: str = Field("balance", description="支付方式")
    
    @field_validator('permission_type')
    @classmethod
    def validate_permission_type(cls, v):
        if v not in ['script', 'image', 'video', 'ad']:
            raise ValueError('权限类型必须是 script、image、video 或 ad')
        return v
    
    @field_validator('payment_mode')
    @classmethod
    def validate_payment_mode(cls, v):
        if v not in ['per_use', 'monthly', 'yearly']:
            raise ValueError('付费模式必须是 per_use、monthly 或 yearly')
        return v
    
    @field_validator('count')
    @classmethod
    def validate_count(cls, v, info):
        if info.data.get('payment_mode') == 'per_use' and not v:
            raise ValueError('按次付费时必须指定购买次数')
        if v and v <= 0:
            raise ValueError('购买次数必须大于0')
        return v
    
    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v):
        if v not in ['wechat', 'alipay', 'unionpay', 'balance']:
            raise ValueError('支付方式必须是 wechat、alipay、unionpay 或 balance')
        return v


class UserPermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    permission_type: str
    payment_mode: str
    total_count: int
    used_count: int
    expire_at: Optional[datetime]
    status: int
    created_at: datetime
