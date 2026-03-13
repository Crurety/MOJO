"""权限服务测试"""

from datetime import datetime, timedelta

import pytest
from app.models import UserPermission
from app.services.permission_service import PermissionService


class TestPermissionService:
    """权限服务测试类"""

    def test_grant_permission_per_use(self, db, test_user):
        """测试授予按次权限"""
        permission_service = PermissionService(db)

        permission = permission_service.grant_permission(
            user_id=test_user.id,
            permission_type="script",
            payment_mode="per_use",
            count=10,
        )

        assert permission.user_id == test_user.id
        assert permission.permission_type == "script"
        assert permission.payment_mode == "per_use"
        assert permission.total_count == 10
        assert permission.used_count == 0
        assert permission.status == 1

    def test_grant_permission_monthly(self, db, test_user):
        """测试授予包月权限"""
        permission_service = PermissionService(db)

        permission = permission_service.grant_permission(
            user_id=test_user.id,
            permission_type="image",
            payment_mode="monthly",
            days=30,
        )

        assert permission.payment_mode == "monthly"
        assert permission.expire_at is not None
        assert permission.expire_at > datetime.now()

    def test_check_permission_valid(self, db, test_user):
        """测试检查权限-有效"""
        permission_service = PermissionService(db)

        # 先授予权限
        permission_service.grant_permission(
            user_id=test_user.id,
            permission_type="video",
            payment_mode="per_use",
            count=5,
        )

        # 检查权限
        has_permission = permission_service.check_permission(test_user.id, "video")

        assert has_permission is True

    def test_check_permission_invalid(self, db, test_user):
        """测试检查权限-无效"""
        permission_service = PermissionService(db)

        has_permission = permission_service.check_permission(test_user.id, "ad")

        assert has_permission is False

    def test_consume_permission(self, db, test_user):
        """测试消耗权限"""
        permission_service = PermissionService(db)

        # 授予权限
        permission_service.grant_permission(
            user_id=test_user.id,
            permission_type="script",
            payment_mode="per_use",
            count=10,
        )

        # 消耗权限
        success = permission_service.consume_permission(test_user.id, "script", 3)

        assert success is True

        # 验证已消耗
        permission = permission_service.get_permission(test_user.id, "script")
        assert permission.used_count == 3
        assert permission.total_count == 10

    def test_consume_permission_insufficient(self, db, test_user):
        """测试消耗权限-次数不足"""
        permission_service = PermissionService(db)

        # 授予少量权限
        permission_service.grant_permission(
            user_id=test_user.id,
            permission_type="script",
            payment_mode="per_use",
            count=2,
        )

        # 尝试消耗超过可用次数
        success = permission_service.consume_permission(test_user.id, "script", 5)

        assert success is False

    def test_consume_permission_across_multiple_rows(self, db, test_user):
        permission_service = PermissionService(db)

        permission_service.grant_permission(test_user.id, "image", "per_use", count=2)
        permission_service.grant_permission(test_user.id, "image", "per_use", count=3)

        assert permission_service.check_permission(test_user.id, "image", required_count=5) is True
        assert permission_service.consume_permission(test_user.id, "image", 4) is True

        permissions = permission_service._get_permissions_for_type(test_user.id, "image")
        assert sum(permission.used_count for permission in permissions) == 4
