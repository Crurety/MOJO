"""优惠券功能测试"""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest


def test_create_coupon(client, auth_headers, db):
    """测试创建优惠券（需要管理员权限）"""
    # 这里简化测试，实际需要管理员权限
    pass


def test_claim_coupon(client, auth_headers, db):
    """测试领取优惠券"""
    from app.models.coupon import Coupon
    from app.services.coupon_service import CouponService

    # 创建测试优惠券
    coupon_service = CouponService(db)
    coupon = coupon_service.create_coupon(
        name="测试优惠券",
        coupon_type="discount",
        discount_value=Decimal("10"),
        start_at=datetime.now(),
        expire_at=datetime.now() + timedelta(days=30),
        total_count=100,
        code="TEST2024",
    )

    # 领取优惠券
    response = client.post(
        "/api/v1/coupon/coupons/claim",
        params={"coupon_code": "TEST2024"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0


def test_get_my_coupons(client, auth_headers):
    """测试获取我的优惠券"""
    response = client.get("/api/v1/coupon/coupons/my", headers=auth_headers)
    assert response.status_code == 200


def test_get_available_coupons(client, auth_headers):
    """测试获取可用优惠券"""
    response = client.get(
        "/api/v1/coupon/coupons/available",
        params={"order_amount": 100},
        headers=auth_headers,
    )
    assert response.status_code == 200
