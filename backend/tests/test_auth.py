"""Auth API tests."""


def test_register(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "phone": "13900139000",
            "password": "Password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "user_id" in data["data"]


def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "phone": "13900139001",
            "password": "Password123",
        },
    )
    assert response.status_code == 409


def test_login_success(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"account": "test@example.com", "password": "Test123456"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "access_token" in data["token"]


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"account": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 400


def test_get_current_user(client, auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


def test_unauthorized_access(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403 or response.status_code == 401
