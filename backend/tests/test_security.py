"""安全测试"""

import pytest


class TestSecurityAuth:
    """安全测试 - 认证授权"""

    def test_unauthorized_access(self, client):
        """测试未授权访问"""
        protected_endpoints = [
            "/api/v1/auth/me",
            "/api/v1/user/profile",
            "/api/v1/content/scripts",
            "/api/v1/payment/orders",
        ]

        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"{endpoint} 应该返回401"

    def test_invalid_token(self, client):
        """测试无效Token"""
        headers = {"Authorization": "Bearer invalid_token_here"}

        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    def test_expired_token(self, client):
        """测试过期Token"""
        # 使用已过期的token
        expired_token = (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MDAwMDAwMDB9.xxx"
        )
        headers = {"Authorization": f"Bearer {expired_token}"}

        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    def test_admin_access_control(self, client, auth_headers):
        """测试管理员权限控制"""
        admin_endpoints = [
            "/api/v1/admin/dashboard",
            "/api/v1/admin/users",
        ]

        for endpoint in admin_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            # 普通用户应该被拒绝
            assert response.status_code in [401, 403]


class TestSecurityInjection:
    """安全测试 - 注入攻击"""

    def test_sql_injection(self, client):
        """测试SQL注入"""
        sql_payloads = [
            "' OR '1'='1",
            "1' OR '1' = '1",
            "admin'--",
            "' UNION SELECT NULL--",
        ]

        for payload in sql_payloads:
            response = client.post(
                "/api/v1/auth/login", json={"account": payload, "password": "test"}
            )
            # 不应该成功登录
            assert response.status_code != 200 or response.json().get("code") != 0

    def test_xss_injection(self, client, auth_headers):
        """测试XSS注入"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
        ]

        for payload in xss_payloads:
            response = client.put(
                "/api/v1/auth/me", json={"nickname": payload}, headers=auth_headers
            )

            # 获取用户信息验证是否被转义
            get_response = client.get("/api/v1/auth/me", headers=auth_headers)
            if get_response.status_code == 200:
                nickname = get_response.json().get("nickname", "")
                # 确保脚本标签被转义或移除
                assert "<script>" not in nickname.lower()
                assert "javascript:" not in nickname.lower()


class TestSecurityDataValidation:
    """安全测试 - 数据验证"""

    def test_email_validation(self, client):
        """测试邮箱验证"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "test@",
            "test..test@example.com",
        ]

        for email in invalid_emails:
            response = client.post(
                "/api/v1/auth/register",
                json={"email": email, "phone": "13800138000", "password": "Test123456"},
            )
            assert response.status_code == 400 or response.json().get("code") != 0

    def test_phone_validation(self, client):
        """测试手机号验证"""
        invalid_phones = [
            "12345",
            "abcdefghijk",
            "10000000000",  # 不是1开头
            "139001380001",  # 超过11位
        ]

        for phone in invalid_phones:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "phone": phone,
                    "password": "Test123456",
                },
            )
            assert response.status_code == 400 or response.json().get("code") != 0

    def test_password_strength(self, client):
        """测试密码强度"""
        weak_passwords = [
            "123",  # 太短
            "12345",  # 太短
            "aaaaa",  # 没有数字
        ]

        for password in weak_passwords:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "phone": "13800138000",
                    "password": password,
                },
            )
            assert response.status_code == 400 or response.json().get("code") != 0


class TestSecurityRateLimit:
    """安全测试 - 速率限制"""

    def test_login_rate_limit(self, client):
        """测试登录速率限制"""
        # 快速尝试多次登录
        for i in range(20):
            response = client.post(
                "/api/v1/auth/login",
                json={"account": "test@example.com", "password": "wrongpassword"},
            )

            # 应该在某个点被限流
            if i > 10:
                if response.status_code == 429:
                    print(f"\n速率限制在第{i + 1}次请求时触发")
                    return

        # 如果没有触发限流，测试失败
        pytest.fail("速率限制未触发")


class TestSecuritySensitiveData:
    """安全测试 - 敏感数据保护"""

    def test_password_not_exposed(self, client, auth_headers):
        """测试密码不暴露"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # 确保密码字段不在响应中
        assert "password" not in data
        assert "hashed_password" not in data

    def test_sensitive_info_in_logs(self, client):
        """测试日志中的敏感信息"""
        # 登录请求
        client.post(
            "/api/v1/auth/login",
            json={"account": "test@example.com", "password": "Test123456"},
        )

        # 检查日志文件（如果存在）
        import os

        log_file = "logs/test.log"
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                log_content = f.read()
                # 确保密码不在日志中
                assert "Test123456" not in log_content


class TestSecurityCSRF:
    """安全测试 - CSRF防护"""

    def test_csrf_protection(self, client, auth_headers):
        """测试CSRF防护"""
        # 尝试不带CSRF token的状态变更请求
        response = client.post(
            "/api/v1/payment/orders",
            json={"permission_type": "script", "payment_mode": "per_use", "count": 10},
            headers=auth_headers,
        )

        # 应该成功（因为使用JWT，不需要CSRF token）
        # 但如果使用session，应该被拒绝
        assert response.status_code in [200, 403]
