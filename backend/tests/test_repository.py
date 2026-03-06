"""Repository测试"""

import pytest
from app.repositories.base import UserRepository, OrderRepository
from app.models import User, Order
from decimal import Decimal


class TestUserRepository:
    """用户Repository测试"""

    def test_create(self, db):
        """测试创建"""
        repo = UserRepository(db)

        user = repo.create(
            {
                "email": "repo@test.com",
                "phone": "13900139000",
                "password": "hashed_password",
                "nickname": "Repo测试",
            }
        )

        assert user.id is not None
        assert user.email == "repo@test.com"

    def test_get_by_id(self, db, test_user):
        """测试根据ID获取"""
        repo = UserRepository(db)

        user = repo.get_by_id(test_user.id)

        assert user is not None
        assert user.id == test_user.id

    def test_find_by(self, db, test_user):
        """测试条件查询"""
        repo = UserRepository(db)

        users = repo.find_by({"email": test_user.email})

        assert len(users) > 0
        assert users[0].email == test_user.email

    def test_update(self, db, test_user):
        """测试更新"""
        repo = UserRepository(db)

        repo.update(test_user.id, {"nickname": "更新后的昵称"})

        user = repo.get_by_id(test_user.id)
        assert user.nickname == "更新后的昵称"

    def test_delete(self, db):
        """测试删除"""
        repo = UserRepository(db)

        # 创建测试用户
        user = repo.create(
            {"email": "delete@test.com", "phone": "13900139001", "password": "password"}
        )

        user_id = user.id

        # 删除
        repo.delete(user_id)

        # 验证已删除
        deleted_user = repo.get_by_id(user_id)
        assert deleted_user is None

    def test_count(self, db, test_user):
        """测试计数"""
        repo = UserRepository(db)

        count = repo.count({"status": 1})

        assert count > 0


class TestOrderRepository:
    """订单Repository测试"""

    def test_get_by_order_no(self, db, test_user):
        """测试根据订单号获取"""
        repo = OrderRepository(db)

        # 创建订单
        order = repo.create(
            {
                "user_id": test_user.id,
                "order_no": "TEST123456",
                "order_type": "permission",
                "product_name": "测试商品",
                "amount": Decimal("100.00"),
                "status": 0,
            }
        )

        # 查询
        found_order = repo.get_by_order_no("TEST123456")

        assert found_order is not None
        assert found_order.order_no == "TEST123456"

    def test_get_user_orders(self, db, test_user):
        """测试获取用户订单"""
        repo = OrderRepository(db)

        # 创建订单
        for i in range(2):
            repo.create(
                {
                    "user_id": test_user.id,
                    "order_no": f"TEST{i}",
                    "order_type": "permission",
                    "product_name": f"商品{i}",
                    "amount": Decimal("50.00"),
                    "status": 0,
                }
            )

        # 查询
        orders = repo.get_user_orders(test_user.id)

        assert len(orders) >= 2
