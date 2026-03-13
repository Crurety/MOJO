"""Enhanced API tests aligned with current routes."""

from decimal import Decimal


class TestContentAPIEnhanced:
    def test_create_script_with_permission(self, client, auth_headers, test_permission, monkeypatch):
        from app.api.v1 import content as content_api

        async def fake_generate_from_keywords(**kwargs):
            return {"script": "Enhanced generated script."}

        monkeypatch.setattr(content_api.script_generator, "generate_from_keywords", fake_generate_from_keywords)

        response = client.post(
            "/api/v1/content/scripts",
            json={
                "title": "test script",
                "keywords": "tech,innovation",
                "output_type": "video",
                "parameters": {"style": "sci-fi"},
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["script"]["content"] == "Enhanced generated script."
        assert "script_id" in data["data"]

    def test_create_script_without_permission(self, client, auth_headers):
        response = client.post(
            "/api/v1/content/scripts",
            json={
                "title": "test script",
                "keywords": "tech,innovation",
                "output_type": "video",
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_create_script_returns_error_when_ai_generation_fails(self, client, auth_headers, test_permission, monkeypatch):
        from app.api.v1 import content as content_api

        async def fake_generate_from_keywords(**kwargs):
            raise RuntimeError("provider unavailable")

        monkeypatch.setattr(content_api.script_generator, "generate_from_keywords", fake_generate_from_keywords)

        response = client.post(
            "/api/v1/content/scripts",
            json={
                "title": "test script",
                "keywords": "tech,innovation",
                "output_type": "video",
            },
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert response.json()["message"] == "Script generation failed. Check AI configuration and try again."

    def test_get_my_scripts(self, client, auth_headers, test_script):
        response = client.get("/api/v1/content/scripts", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_task_requires_permission(self, client, auth_headers):
        response = client.post(
            "/api/v1/content/tasks",
            json={
                "task_type": "image",
                "parameters": {"prompt": "a beautiful sunset", "clarity": "1080p"},
            },
            headers=auth_headers,
        )

        assert response.status_code in [200, 400]
        if response.status_code == 200:
            assert response.json().get("code") != 0

    def test_get_task_status(self, client, auth_headers, test_task):
        response = client.get(f"/api/v1/content/tasks/{test_task.task_no}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "progress" in data

    def test_get_my_works(self, client, auth_headers, test_work):
        response = client.get("/api/v1/content/works", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_delete_work(self, client, auth_headers, test_work):
        response = client.delete(f"/api/v1/content/works/{test_work.id}", headers=auth_headers)
        assert response.status_code == 200

    def test_get_public_works(self, client):
        response = client.get("/api/v1/content/gallery", params={"skip": 0, "limit": 10})
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestPaymentAPIEnhanced:
    def test_create_order_permission(self, client, auth_headers):
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

    def test_create_order_balance(self, client, auth_headers):
        response = client.post(
            "/api/v1/payment/orders/balance?amount=100&payment_method=alipay",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_get_my_orders(self, client, auth_headers, test_order):
        response = client.get("/api/v1/payment/orders", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_order_detail(self, client, auth_headers, test_order):
        response = client.get(f"/api/v1/payment/orders/{test_order.order_no}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["order_no"] == test_order.order_no

    def test_pay_order_with_balance(self, client, auth_headers, test_order, db):
        from app.models import User

        user = db.query(User).filter(User.email == "test@example.com").first()
        user.balance = Decimal("1000.00")
        test_order.payment_method = "balance"
        db.commit()

        response = client.post(f"/api/v1/payment/orders/{test_order.order_no}/pay", headers=auth_headers)
        assert response.status_code == 200


class TestAuthAPIEnhanced:
    def test_register_with_existing_email(self, client, test_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "phone": "13900139000",
                "password": "Test123456",
            },
        )
        assert response.status_code == 400 or response.json().get("code") != 0

    def test_register_with_existing_phone(self, client, test_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "phone": "13800138000",
                "password": "Test123456",
            },
        )
        assert response.status_code == 400 or response.json().get("code") != 0

    def test_login_with_email(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"account": "test@example.com", "password": "Test123456"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "token" in data

    def test_login_with_phone(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"account": "13800138000", "password": "Test123456"},
        )

        assert response.status_code == 200
        assert "token" in response.json()

    def test_get_current_user(self, client, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "phone" in data

    def test_update_profile(self, client, auth_headers):
        response = client.put(
            "/api/v1/auth/me",
            json={"nickname": "new_nickname", "avatar": "https://example.com/avatar.png"},
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_get_balance(self, client, auth_headers):
        response = client.get("/api/v1/auth/me/balance", headers=auth_headers)
        assert response.status_code == 200
        assert "balance" in response.json()
