"""用户服务测试"""
import pytest
from decimal import Decimal
from app.services.user_service import UserService
from app.models import User


class TestUserService:
    """用户服务测试"""

    def test_create_user(self, db):
        """测试创建用户"""
        user_service = UserService(db)
        user = user_service.create_user(
            email="newuser@example.com",
            phone="13800138001",
            password="Test123456",
            nickname="新用户"
        )

        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.phone == "13800138001"
        assert user.nickname == "新用户"
        assert user.status == 1

    def test_get_user_by_email(self, db, test_user):
        """测试通过邮箱获取用户"""
        user_service = UserService(db)
        user = user_service.get_user_by_email("test@example.com")

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_user_by_phone(self, db, test_user):
        """测试通过手机号获取用户"""
        user_service = UserService(db)
        user = user_service.get_user_by_phone("13800138000")

        assert user is not None
        assert user.id == test_user.id
        assert user.phone == test_user.phone

    def test_update_user_profile(self, db, test_user):
        """测试更新用户资料"""
        user_service = UserService(db)
        updated_user = user_service.update_profile(
            test_user.id,
            nickname="新昵称",
            avatar="https://example.com/avatar.png"
        )

        assert updated_user.nickname == "新昵称"
        assert updated_user.avatar == "https://example.com/avatar.png"

    def test_update_user_balance(self, db, test_user):
        """测试更新用户余额"""
        user_service = UserService(db)
        initial_balance = test_user.balance

        user_service.update_balance(test_user.id, Decimal("50.00"))
        db.refresh(test_user)

        assert test_user.balance == initial_balance + Decimal("50.00")

    def test_disable_user(self, db, test_user):
        """测试禁用用户"""
        user_service = UserService(db)
        user_service.disable_user(test_user.id)
        db.refresh(test_user)

        assert test_user.status == 0

    def test_enable_user(self, db, disabled_user):
        """测试启用用户"""
        user_service = UserService(db)
        user_service.enable_user(disabled_user.id)
        db.refresh(disabled_user)

        assert disabled_user.status == 1

    def test_generate_invite_code(self, db, test_user):
        """测试生成邀请码"""
        user_service = UserService(db)
        invite_code = user_service.generate_invite_code(test_user.id)

        assert invite_code is not None
        assert len(invite_code) == 8

        db.refresh(test_user)
        assert test_user.invite_code == invite_code

    def test_user_authentication(self, db, test_user):
        """测试用户认证"""
        user_service = UserService(db)
        
        # 正确密码
        authenticated = user_service.authenticate(
            "test@example.com",
            "Test123456"
        )
        assert authenticated is not None
        assert authenticated.id == test_user.id

        # 错误密码
        authenticated = user_service.authenticate(
            "test@example.com",
            "wrongpassword"
        )
        assert authenticated is None

        # 不存在的用户
        authenticated = user_service.authenticate(
            "nonexistent@example.com",
            "Test123456"
        )
        assert authenticated is None
