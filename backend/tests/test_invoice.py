"""发票功能测试"""

from decimal import Decimal

import pytest


def test_submit_real_name(client, auth_headers):
    """测试提交实名认证"""
    response = client.post(
        "/api/v1/invoice/real-name/submit",
        json={"real_name": "张三", "id_card": "110101199001011234"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0


def test_get_real_name_status(client, auth_headers):
    """测试获取实名认证状态"""
    response = client.get("/api/v1/invoice/real-name/status", headers=auth_headers)
    assert response.status_code == 200


def test_create_invoice_without_real_name(client, auth_headers):
    """测试未实名认证时申请发票"""
    response = client.post(
        "/api/v1/invoice/invoices",
        json={
            "order_id": 1,
            "invoice_type": "normal",
            "invoice_title": "测试公司",
            "tax_no": "123456789012345",
            "amount": 100.00,
            "recipient_name": "张三",
            "recipient_phone": "13800138000",
            "recipient_address": "北京市朝阳区",
        },
        headers=auth_headers,
    )
    # 应该返回400，提示需要实名认证
    assert response.status_code == 400


def test_get_my_invoices(client, auth_headers):
    """测试获取我的发票"""
    response = client.get("/api/v1/invoice/invoices", headers=auth_headers)
    assert response.status_code == 200
