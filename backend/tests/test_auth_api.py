"""Authentication API tests."""


class TestRegister:
    def test_register_success(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "phone": "15900001111",
                "password": "NewUser123",
            },
        )
        assert response.status_code == 200
        assert response.json()["code"] == 0

    def test_register_duplicate_email(self, client, test_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "phone": "15911112222",
                "password": "Test123456",
            },
        )
        assert response.status_code != 200

    def test_register_duplicate_phone(self, client, test_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new2@example.com",
                "phone": "13800138000",
                "password": "Test123456",
            },
        )
        assert response.status_code != 200

    def test_register_weak_password(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "weak@example.com", "phone": "15933334444", "password": "123"},
        )
        assert response.status_code != 200

    def test_register_invalid_email(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "invalid", "phone": "15944445555", "password": "Test123456"},
        )
        assert response.status_code != 200


class TestLogin:
    def test_login_by_email(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"account": "test@example.com", "password": "Test123456"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["token"]

    def test_login_by_phone(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"account": "13800138000", "password": "Test123456"},
        )
        assert response.status_code == 200

    def test_login_wrong_password(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"account": "test@example.com", "password": "WrongPass123"},
        )
        assert response.status_code != 200

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={"account": "ghost@example.com", "password": "Test123456"},
        )
        assert response.status_code != 200

    def test_login_disabled_user(self, client, disabled_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"account": "disabled@example.com", "password": "Test123456"},
        )
        assert response.status_code != 200


class TestMe:
    def test_get_me(self, client, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"

    def test_get_me_no_token(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code in {401, 403}

    def test_get_me_invalid_token(self, client):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer fake.token.here"},
        )
        assert response.status_code == 401


class TestUpdateProfile:
    def test_update_nickname(self, client, auth_headers):
        response = client.put(
            "/api/v1/auth/me",
            json={"nickname": "new_nickname"},
            headers=auth_headers,
        )
        assert response.status_code == 200

        me = client.get("/api/v1/auth/me", headers=auth_headers).json()
        assert me["nickname"] == "new_nickname"

    def test_update_avatar(self, client, auth_headers):
        response = client.put(
            "/api/v1/auth/me",
            json={"avatar": "https://cdn.example.com/avatar.jpg"},
            headers=auth_headers,
        )
        assert response.status_code == 200
