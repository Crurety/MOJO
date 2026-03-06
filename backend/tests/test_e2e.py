"""E2E smoke tests for primary user journey."""

from decimal import Decimal


class TestE2EUserJourney:
    def test_register_login_and_profile(self, client):
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "journey@test.com",
                "phone": "13900000001",
                "password": "Test123456",
            },
        )
        assert register_response.status_code == 200

        login_response = client.post(
            "/api/v1/auth/login",
            json={"account": "journey@test.com", "password": "Test123456"},
        )
        assert login_response.status_code == 200

        token = login_response.json()["token"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "journey@test.com"


class TestE2EPaymentFlow:
    def test_create_and_pay_permission_order_by_balance(self, client, db):
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "buyer@test.com",
                "phone": "13900000009",
                "password": "Test123456",
            },
        )
        assert register_response.status_code == 200

        login_response = client.post(
            "/api/v1/auth/login",
            json={"account": "buyer@test.com", "password": "Test123456"},
        )
        token = login_response.json()["token"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        from app.models import User

        user = db.query(User).filter(User.email == "buyer@test.com").first()
        user.balance = Decimal("200.00")
        db.commit()

        order_response = client.post(
            "/api/v1/payment/orders",
            json={
                "permission_type": "script",
                "payment_mode": "per_use",
                "count": 5,
                "payment_method": "balance",
            },
            headers=headers,
        )
        assert order_response.status_code == 200
        order_no = order_response.json()["data"]["order_no"]

        pay_response = client.post(
            f"/api/v1/payment/orders/{order_no}/pay", headers=headers
        )
        assert pay_response.status_code == 200

        balance_response = client.get("/api/v1/auth/me/balance", headers=headers)
        assert balance_response.status_code == 200
        assert balance_response.json()["balance"] == 195.0


class TestE2EContentFlow:
    def test_create_script_after_login(self, client):
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "writer@test.com",
                "phone": "13900000011",
                "password": "Test123456",
            },
        )
        assert register_response.status_code == 200

        login_response = client.post(
            "/api/v1/auth/login",
            json={"account": "writer@test.com", "password": "Test123456"},
        )
        token = login_response.json()["token"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        script_response = client.post(
            "/api/v1/content/scripts",
            json={
                "title": "My First Script",
                "content": "A short commercial script about innovation.",
                "output_type": "video",
            },
            headers=headers,
        )
        assert script_response.status_code == 200

        list_response = client.get("/api/v1/content/scripts", headers=headers)
        assert list_response.status_code == 200
        assert len(list_response.json()) >= 1
