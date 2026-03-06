"""用户服务测试"""

import pytest
from app.services.user_service import UserService
from app.models import User
from app.core.security import verify_password


class TestUserService:
    """用户服务测试类"""

    def test_create_user(self, db):
        """测试创建用户"""
        user_service = UserService(db)

        user = user_service.create(
            email="test@example.com",
            phone="13800138000",
            password="password123",
            nickname="测试用户",
        )

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.phone == "13800138000"
        assert user.nickname == "测试用户"
        assert verify_password("password123", user.password)

    def test_get_by_email(self, db, test_user):
        """测试根据邮箱获取用户"""
        user_service = UserService(db)

        user = user_service.get_by_email("test@example.com")

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_by_phone(self, db, test_user):
        """测试根据手机号获取用户"""
        user_service = UserService(db)

        user = user_service.get_by_phone("13800138000")

        assert user is not None
        assert user.id == test_user.id
        assert user.phone == test_user.phone

    def test_authenticate_success(self, db, test_user):
        """测试认证成功"""
        user_service = UserService(db)

        user = user_service.authenticate("test@example.com", "password123")

        assert user is not None
        assert user.id == test_user.id

    def test_authenticate_wrong_password(self, db, test_user):
        """测试认证失败-错误密码"""
        user_service = UserService(db)

        user = user_service.authenticate("test@example.com", "wrongpassword")

        assert user is None

    def test_update_user(self, db, test_user):
        """测试更新用户"""
        user_service = UserService(db)

        user_service.update(test_user.id, nickname="新昵称")

        updated_user = user_service.get_by_id(test_user.id)
        assert updated_user.nickname == "新昵称"

    def test_generate_invite_code(self, db, test_user):
        """测试生成邀请码"""
        user_service = UserService(db)

        invite_code = user_service.generate_invite_code(test_user.id)

        assert invite_code is not None
        assert len(invite_code) > 0

        # 验证邀请码已保存
        user = user_service.get_by_id(test_user.id)
        assert user.invite_code == invite_code
