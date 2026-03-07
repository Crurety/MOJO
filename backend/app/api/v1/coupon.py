"""优惠券API路由"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.models import User
from app.schemas import BaseResponse
from app.services.coupon_service import CouponService
from app.core.rate_limit import limiter, RATE_LIMITS
from typing import List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal


router = APIRouter()


class CouponCreate(BaseModel):
    name: str
    coupon_type: str
    discount_value: Decimal
    start_at: datetime
    expire_at: datetime
    total_count: int = 1
    min_amount: Decimal = Decimal(0)
    max_discount: Decimal | None = None
    permission_type: str | None = None
    permission_days: int | None = None
    code: str | None = None


class CouponResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    code: str
    name: str
    coupon_type: str
    discount_value: Decimal | None
    permission_type: str | None
    permission_days: int | None
    min_amount: Decimal
    max_discount: Decimal | None
    total_count: int
    used_count: int
    start_at: datetime
    expire_at: datetime
    status: int


class UserCouponResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    coupon_id: int
    status: int
    used_at: datetime | None
    created_at: datetime
    coupon: CouponResponse


@limiter.limit(RATE_LIMITS["general"])
@router.post("/coupons/claim", response_model=BaseResponse)
def claim_coupon(
    request: Request,
    coupon_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """领取优惠券

    Args:
        coupon_code: 优惠券码
        current_user: 当前用户
        db: 数据库会话

    Returns:
        BaseResponse: 领取结果
    """
    coupon_service = CouponService(db)
    success, message, user_coupon = coupon_service.claim_coupon(
        current_user.id, coupon_code
    )

    if not success:
        return BaseResponse(code=400, message=message)

    return BaseResponse(message=message, data={"user_coupon_id": user_coupon.id})


@limiter.limit(RATE_LIMITS["general"])
@router.get("/coupons/my", response_model=List[UserCouponResponse])
def get_my_coupons(
    request: Request,
    status: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的优惠券

    Args:
        status: 状态 (0未使用/1已使用/2已过期)
        current_user: 当前用户
        db: 数据库会话

    Returns:
        List[UserCouponResponse]: 优惠券列表
    """
    coupon_service = CouponService(db)
    user_coupons = coupon_service.get_user_coupons(current_user.id, status)
    return [UserCouponResponse.model_validate(uc) for uc in user_coupons]


@limiter.limit(RATE_LIMITS["general"])
@router.get("/coupons/available")
def get_available_coupons(
    request: Request,
    order_amount: Decimal,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取可用优惠券

    Args:
        order_amount: 订单金额
        current_user: 当前用户
        db: 数据库会话

    Returns:
        List: 可用优惠券列表
    """
    coupon_service = CouponService(db)
    user_coupons = coupon_service.get_available_coupons(current_user.id, order_amount)

    result = []
    for uc in user_coupons:
        discount = coupon_service.calculate_discount(uc.coupon, order_amount)
        result.append({
            "user_coupon_id": uc.id,
            "coupon": CouponResponse.model_validate(uc.coupon),
            "discount_amount": float(discount)
        })

    return result


# 管理员接口
@router.post("/admin/coupons", response_model=BaseResponse)
def create_coupon(
    coupon_in: CouponCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建优惠券（管理员）

    Args:
        coupon_in: 优惠券信息
        current_admin: 当前管理员
        db: 数据库会话

    Returns:
        BaseResponse: 创建结果
    """
    coupon_service = CouponService(db)
    coupon = coupon_service.create_coupon(
        name=coupon_in.name,
        coupon_type=coupon_in.coupon_type,
        discount_value=coupon_in.discount_value,
        start_at=coupon_in.start_at,
        expire_at=coupon_in.expire_at,
        total_count=coupon_in.total_count,
        min_amount=coupon_in.min_amount,
        max_discount=coupon_in.max_discount,
        permission_type=coupon_in.permission_type,
        permission_days=coupon_in.permission_days,
        code=coupon_in.code
    )

    return BaseResponse(
        message="优惠券创建成功",
        data={"coupon_id": coupon.id, "code": coupon.code}
    )


@router.get("/admin/coupons", response_model=List[CouponResponse])
def get_all_coupons(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取所有优惠券（管理员）

    Args:
        skip: 跳过数量
        limit: 返回数量
        current_admin: 当前管理员
        db: 数据库会话

    Returns:
        List[CouponResponse]: 优惠券列表
    """
    from app.models.coupon import Coupon
    coupons = db.query(Coupon).offset(skip).limit(limit).all()
    return [CouponResponse.model_validate(c) for c in coupons]
