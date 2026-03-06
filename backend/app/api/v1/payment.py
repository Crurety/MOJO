"""Payment API routes."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Tuple

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.rate_limit import RATE_LIMITS, limiter
from app.models import Order, User
from app.payment import payment_service
from app.schemas import BaseResponse, OrderResponse, PermissionPurchase
from app.services import OrderService, PermissionService

router = APIRouter()

ONLINE_PAYMENT_METHODS = {"wechat", "alipay", "unionpay"}


def _build_permission_order_payload(order_in: PermissionPurchase) -> dict:
    return {
        "permission_type": order_in.permission_type,
        "payment_mode": order_in.payment_mode,
        "count": order_in.count or 0,
    }


def _parse_permission_order_payload(order: Order) -> Tuple[str, str, int]:
    payload: Dict[str, Any] = {}
    if order.remark:
        try:
            payload = json.loads(order.remark)
        except json.JSONDecodeError:
            payload = {}

    permission_type = payload.get("permission_type")
    payment_mode = payload.get("payment_mode")
    count = int(payload.get("count") or 0)

    # Fallback for legacy product names.
    if not permission_type or not payment_mode:
        parts = (order.product_name or "").split("-")
        if len(parts) >= 2:
            permission_type = permission_type or parts[0].replace("权限", "")
            payment_mode = payment_mode or parts[1]

    if not permission_type or payment_mode not in {"per_use", "monthly", "yearly"}:
        raise BadRequestException(detail="Invalid permission order payload")

    if payment_mode == "per_use" and count <= 0:
        count = 1

    return permission_type, payment_mode, count


def _apply_paid_order_effects(
    order: Order, db: Session, permission_service: PermissionService
) -> None:
    if order.order_type == "permission":
        permission_type, payment_mode, count = _parse_permission_order_payload(order)
        if payment_mode == "per_use":
            permission_service.grant_permission(
                order.user_id,
                permission_type,
                "per_use",
                count=count,
            )
        elif payment_mode == "monthly":
            permission_service.grant_permission(
                order.user_id,
                permission_type,
                "monthly",
                days=30,
            )
        elif payment_mode == "yearly":
            permission_service.grant_permission(
                order.user_id,
                permission_type,
                "yearly",
                days=365,
            )
        return

    if order.order_type == "balance":
        user = db.query(User).filter(User.id == order.user_id).first()
        if not user:
            raise NotFoundException(detail="User not found")

        user.balance = Decimal(user.balance) + Decimal(order.amount)
        db.commit()
        db.refresh(user)


@limiter.limit(RATE_LIMITS["payment"])
@router.post("/orders", response_model=BaseResponse)
def create_order(
    order_in: PermissionPurchase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)
    permission_service = PermissionService(db)

    amount = permission_service.get_permission_price(
        order_in.permission_type,
        order_in.payment_mode,
    )

    if order_in.payment_mode == "per_use" and order_in.count:
        amount *= order_in.count

    product_name = f"{order_in.permission_type}权限-{order_in.payment_mode}"
    remark = json.dumps(_build_permission_order_payload(order_in), ensure_ascii=False)

    order = order_service.create(
        user_id=current_user.id,
        order_type="permission",
        product_name=product_name,
        amount=amount,
        payment_method=order_in.payment_method,
        remark=remark,
    )

    return BaseResponse(
        message="Order created",
        data={"order_no": order.order_no, "amount": str(amount)},
    )


@limiter.limit(RATE_LIMITS["payment"])
@router.post("/orders/balance", response_model=BaseResponse)
def create_balance_order(
    amount: Decimal,
    payment_method: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if amount <= 0:
        raise BadRequestException(detail="Amount must be greater than 0")

    if payment_method not in ONLINE_PAYMENT_METHODS:
        raise BadRequestException(
            detail="Balance recharge only supports online payment methods"
        )

    order_service = OrderService(db)
    order = order_service.create(
        user_id=current_user.id,
        order_type="balance",
        product_name=f"余额充值-{amount}元",
        amount=amount,
        payment_method=payment_method,
    )

    return BaseResponse(
        message="Order created",
        data={"order_no": order.order_no, "amount": str(amount)},
    )


@limiter.limit(RATE_LIMITS["general"])
@router.get("/orders", response_model=List[OrderResponse])
def get_user_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: int | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)
    orders = order_service.get_user_orders(current_user.id, skip, limit, status)
    return [OrderResponse.model_validate(o) for o in orders]


@limiter.limit(RATE_LIMITS["general"])
@router.get("/orders/{order_no}", response_model=OrderResponse)
def get_order_detail(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)
    order = order_service.get_by_order_no(order_no)
    if not order or order.user_id != current_user.id:
        raise NotFoundException(detail="Order not found")
    return OrderResponse.model_validate(order)


@limiter.limit(RATE_LIMITS["payment"])
@router.post("/orders/{order_no}/pay", response_model=BaseResponse)
async def pay_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)
    permission_service = PermissionService(db)

    order = order_service.get_by_order_no(order_no)
    if not order or order.user_id != current_user.id:
        raise NotFoundException(detail="Order not found")

    if order.status != 0:
        raise BadRequestException(detail="Order status is invalid")

    if order.payment_method == "balance":
        if order.order_type == "balance":
            raise BadRequestException(
                detail="Balance cannot be used to recharge balance"
            )

        if Decimal(current_user.balance) < Decimal(order.amount):
            raise BadRequestException(detail="Insufficient balance")

        current_user.balance = Decimal(current_user.balance) - Decimal(order.amount)
        order.status = 1
        order.paid_at = datetime.utcnow()
        db.commit()
        db.refresh(order)

        _apply_paid_order_effects(order, db, permission_service)
        return BaseResponse(message="Payment succeeded")

    result = await payment_service.create_payment(
        payment_method=order.payment_method,
        order_no=order.order_no,
        amount=float(order.amount),
        description=order.product_name,
    )

    if not result.get("success"):
        raise BadRequestException(
            detail=result.get("error", "Failed to create payment")
        )

    return BaseResponse(
        message="Payment link created",
        data={
            "pay_url": result.get("pay_url") or result.get("code_url"),
            "order_no": order.order_no,
        },
    )


def _handle_callback(payment_method: str, payload: Any, db: Session) -> bool:
    order_service = OrderService(db)
    permission_service = PermissionService(db)

    result = payment_service.verify_callback(payment_method, payload)
    if not result.get("success"):
        return False

    order_no = result.get("order_no")
    payment_no = result.get("transaction_id")
    if not order_no or not payment_no:
        return False

    order = order_service.get_by_order_no(order_no)
    if not order:
        return False

    if order.status == 1:
        return True

    try:
        order = order_service.update_payment(order_no, payment_no, payment_method)
    except BadRequestException:
        # idempotent callback
        return True

    _apply_paid_order_effects(order, db, permission_service)
    return True


@router.post("/callback/wechat")
async def wechat_callback(request: Request, db: Session = Depends(get_db)):
    xml_data = (await request.body()).decode()
    success = _handle_callback("wechat", xml_data, db)
    if not success:
        return "<xml><return_code><![CDATA[FAIL]]></return_code></xml>"
    return "<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>"


@router.post("/callback/alipay")
async def alipay_callback(request: Request, db: Session = Depends(get_db)):
    form_data = dict(await request.form())
    success = _handle_callback("alipay", form_data, db)
    return "success" if success else "failure"


@router.post("/callback/unionpay")
async def unionpay_callback(request: Request, db: Session = Depends(get_db)):
    form_data = dict(await request.form())
    success = _handle_callback("unionpay", form_data, db)
    return "success" if success else "failure"
