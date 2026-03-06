"""Order service tests."""

from decimal import Decimal

from app.services.order_service import OrderService


class TestOrderService:
    def test_create_order(self, db, test_user):
        order_service = OrderService(db)

        order = order_service.create(
            user_id=test_user.id,
            order_type="permission",
            product_name="script-per_use",
            amount=Decimal("10.00"),
            payment_method="alipay",
        )

        assert order.user_id == test_user.id
        assert order.order_type == "permission"
        assert order.amount == Decimal("10.00")
        assert order.status == 0
        assert order.order_no

    def test_get_by_order_no(self, db, test_user):
        order_service = OrderService(db)

        order = order_service.create(
            user_id=test_user.id,
            order_type="balance",
            product_name="balance-100",
            amount=Decimal("100.00"),
            payment_method="wechat",
        )

        found_order = order_service.get_by_order_no(order.order_no)

        assert found_order is not None
        assert found_order.id == order.id
        assert found_order.order_no == order.order_no

    def test_update_payment(self, db, test_user):
        order_service = OrderService(db)

        order = order_service.create(
            user_id=test_user.id,
            order_type="permission",
            product_name="test-product",
            amount=Decimal("50.00"),
            payment_method="wechat",
        )

        updated = order_service.update_payment(
            order_no=order.order_no,
            payment_no="WX123456789",
            payment_method="wechat",
        )

        assert updated.status == 1
        assert updated.payment_method == "wechat"
        assert updated.payment_no == "WX123456789"
        assert updated.paid_at is not None

    def test_get_user_orders(self, db, test_user):
        order_service = OrderService(db)

        for i in range(3):
            order_service.create(
                user_id=test_user.id,
                order_type="permission",
                product_name=f"product-{i}",
                amount=Decimal(f"{10 * (i + 1)}.00"),
                payment_method="alipay",
            )

        orders = order_service.get_user_orders(test_user.id)
        assert len(orders) == 3
