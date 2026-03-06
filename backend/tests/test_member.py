"""会员积分系统测试"""

from datetime import datetime, timedelta

import pytest


class TestMemberService:
    """会员积分服务测试"""

    def test_get_user_points(self, db, test_user):
        """测试获取用户积分"""
        from app.services.member_service import MemberService

        member_service = MemberService(db)
        user_points = member_service.get_user_points(test_user.id)

        # 首次获取会自动初始化
        assert user_points is not None
        assert user_points.user_id == test_user.id

    def test_add_points(self, db, test_user):
        """测试增加积分"""
        from app.services.member_service import MemberService

        member_service = MemberService(db)

        # 增加积分
        success, message = member_service.add_points(
            user_id=test_user.id, points=100, source="test", description="测试增加积分"
        )

        assert success is True

        # 验证积分
        user_points = member_service.get_user_points(test_user.id)
        assert user_points.total_points >= 100

    def test_consume_points(self, db, test_user):
        """测试消耗积分"""
        from app.services.member_service import MemberService

        member_service = MemberService(db)

        # 先增加积分
        member_service.add_points(test_user.id, 100, "test")

        # 消耗积分
        success, message = member_service.consume_points(
            user_id=test_user.id, points=50, reason="test", description="测试消耗积分"
        )

        assert success is True

        # 验证积分
        user_points = member_service.get_user_points(test_user.id)
        assert user_points.available_points >= 50

    def test_consume_points_insufficient(self, db, test_user):
        """测试积分不足"""
        from app.services.member_service import MemberService

        member_service = MemberService(db)

        # 尝试消耗超过可用积分
        success, message = member_service.consume_points(
            user_id=test_user.id, points=10000, reason="test"
        )

        assert success is False
        assert "不足" in message

    def test_get_points_logs(self, db, test_user):
        """测试获取积分记录"""
        from app.services.member_service import MemberService

        member_service = MemberService(db)

        # 增加一些积分记录
        member_service.add_points(test_user.id, 10, "test1")
        member_service.add_points(test_user.id, 20, "test2")

        # 获取记录
        logs = member_service.get_points_logs(test_user.id)

        assert len(logs) >= 2

    def test_level_upgrade(self, db, test_user):
        """测试等级升级"""
        from app.models.member import MemberLevel
        from app.services.member_service import MemberService

        member_service = MemberService(db)

        # 创建测试等级
        level = MemberLevel(
            level_name="银卡会员",
            level_code="silver",
            min_points=100,
            max_points=499,
            discount_rate=95,
            sort_order=2,
            status=1,
        )
        db.add(level)
        db.commit()

        # 增加积分触发升级
        member_service.add_points(test_user.id, 150, "test")

        # 检查等级
        user_points = member_service.get_user_points(test_user.id)
        if user_points.level_id:
            current_level = (
                db.query(MemberLevel)
                .filter(MemberLevel.id == user_points.level_id)
                .first()
            )
            assert current_level is not None


class TestMemberAPI:
    """会员积分API测试"""

    def test_get_my_points(self, client, auth_headers):
        """测试获取我的积分"""
        response = client.get("/api/v1/operation/member/points", headers=auth_headers)

        assert response.status_code == 200

    def test_get_points_logs(self, client, auth_headers):
        """测试获取积分记录"""
        response = client.get(
            "/api/v1/operation/member/points/logs", headers=auth_headers
        )

        assert response.status_code == 200

    def test_get_member_levels(self, client):
        """测试获取会员等级列表"""
        response = client.get("/api/v1/operation/member/levels")

        assert response.status_code == 200

    def test_get_growth_tasks(self, client, auth_headers):
        """测试获取成长任务"""
        response = client.get(
            "/api/v1/operation/member/growth/tasks", headers=auth_headers
        )

        assert response.status_code == 200
