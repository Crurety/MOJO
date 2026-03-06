"""Payment API tests."""

from decimal import Decimal
from unittest.mock import patch


class TestPaymentAPI:
    def test_create_permission_order(self, client, auth_headers):
        response = client.post(
            "/api/v1/payment/orders",
            json={
                "permission_type": "script",
                "payment_mode": "per_use",
                "count": 10,
                "payment_method": "balance",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "order_no" in data["data"]

    def test_create_balance_recharge_order(self, client, auth_headers):
        response = client.post(
            "/api/v1/payment/orders/balance?amount=100&payment_method=alipay",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["code"] == 0

    def test_get_my_orders(self, client, auth_headers):
        response = client.get("/api/v1/payment/orders", headers=auth_headers)
        assert response.status_code == 200

    def test_get_order_detail(self, client, auth_headers):
        create_resp = client.post(
            "/api/v1/payment/orders",
            json={
                "permission_type": "script",
                "payment_mode": "per_use",
                "count": 1,
                "payment_method": "balance",
            },
            headers=auth_headers,
        )
        order_no = create_resp.json()["data"]["order_no"]

        response = client.get(
            f"/api/v1/payment/orders/{order_no}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["order_no"] == order_no

    def test_balance_pay(self, client, auth_headers, db):
        from app.models import User

        user = db.query(User).filter(User.email == "test@example.com").first()
        user.balance = Decimal("100.00")
        db.commit()

        create_resp = client.post(
            "/api/v1/payment/orders",
            json={
                "permission_type": "script",
                "payment_mode": "per_use",
                "count": 10,
                "payment_method": "balance",
            },
            headers=auth_headers,
        )
        order_no = create_resp.json()["data"]["order_no"]

        response = client.post(
            f"/api/v1/payment/orders/{order_no}/pay", headers=auth_headers
        )
        assert response.status_code == 200

        db.refresh(user)
        assert user.balance == Decimal("90.00")

    def test_balance_pay_insufficient(self, client, auth_headers, db):
        from app.models import User

        user = db.query(User).filter(User.email == "test@example.com").first()
        user.balance = Decimal("0.00")
        db.commit()

        create_resp = client.post(
            "/api/v1/payment/orders",
            json={
                "permission_type": "script",
                "payment_mode": "per_use",
                "count": 10,
                "payment_method": "balance",
            },
            headers=auth_headers,
        )
        order_no = create_resp.json()["data"]["order_no"]

        response = client.post(
            f"/api/v1/payment/orders/{order_no}/pay", headers=auth_headers
        )
        assert response.status_code == 400

    @patch("app.payment.payment_service.create_payment")
    def test_online_pay_link(self, mock_create_payment, client, auth_headers):
        mock_create_payment.return_value = {
            "success": True,
            "pay_url": "https://pay.example.com/mock",
        }

        create_resp = client.post(
            "/api/v1/payment/orders",
            json={
                "permission_type": "image",
                "payment_mode": "monthly",
                "payment_method": "alipay",
            },
            headers=auth_headers,
        )
        order_no = create_resp.json()["data"]["order_no"]

        response = client.post(
            f"/api/v1/payment/orders/{order_no}/pay", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["data"]["pay_url"] == "https://pay.example.com/mock"
