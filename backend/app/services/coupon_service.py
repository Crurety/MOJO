"""优惠券服务"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.models.coupon import Coupon, UserCoupon
from app.models import User
from decimal import Decimal
import random
import string


class CouponService:
    """优惠券服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_coupon(
        self,
        name: str,
        coupon_type: str,
        discount_value: Decimal,
        start_at: datetime,
        expire_at: datetime,
        total_count: int = 1,
        min_amount: Decimal = Decimal(0),
        max_discount: Optional[Decimal] = None,
        permission_type: Optional[str] = None,
        permission_days: Optional[int] = None,
        code: Optional[str] = None
    ) -> Coupon:
        """创建优惠券

        Args:
            name: 优惠券名称
            coupon_type: 类型 (discount折扣/amount金额/permission权限)
            discount_value: 折扣值或金额
            start_at: 开始时间
            expire_at: 过期时间
            total_count: 总发放数量
            min_amount: 最低消费金额
            max_discount: 最大优惠金额
            permission_type: 权限类型
            permission_days: 权限天数
            code: 优惠券码（不提供则自动生成）

        Returns:
            Coupon: 创建的优惠券
        """
        if not code:
            code = self._generate_coupon_code()

        coupon = Coupon(
            code=code,
            name=name,
            coupon_type=coupon_type,
            discount_value=discount_value,
            permission_type=permission_type,
            permission_days=permission_days,
            min_amount=min_amount,
            max_discount=max_discount,
            total_count=total_count,
            start_at=start_at,
            expire_at=expire_at,
            status=1
        )

        self.db.add(coupon)
        self.db.commit()
        self.db.refresh(coupon)

        return coupon

    def _generate_coupon_code(self, length: int = 12) -> str:
        """生成优惠券码"""
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(chars, k=length))
            # 检查是否已存在
            existing = self.db.query(Coupon).filter(Coupon.code == code).first()
            if not existing:
                return code

    def get_coupon_by_code(self, code: str) -> Optional[Coupon]:
        """根据优惠券码获取优惠券"""
        return self.db.query(Coupon).filter(Coupon.code == code).first()

    def claim_coupon(self, user_id: int, coupon_code: str) -> tuple[bool, str, Optional[UserCoupon]]:
        """领取优惠券

        Args:
            user_id: 用户ID
            coupon_code: 优惠券码

        Returns:
            tuple: (是否成功, 消息, 用户优惠券对象)
        """
        coupon = self.get_coupon_by_code(coupon_code)

        if not coupon:
            return False, "优惠券不存在", None

        if coupon.status != 1:
            return False, "优惠券已禁用", None

        now = datetime.now()
        if now < coupon.start_at:
            return False, "优惠券未开始", None

        if now > coupon.expire_at:
            return False, "优惠券已过期", None

        if coupon.used_count >= coupon.total_count:
            return False, "优惠券已领完", None

        # 检查用户是否已领取
        existing = self.db.query(UserCoupon).filter(
            UserCoupon.user_id == user_id,
            UserCoupon.coupon_id == coupon.id
        ).first()

        if existing:
            return False, "您已领取过该优惠券", None

        # 创建用户优惠券
        user_coupon = UserCoupon(
            user_id=user_id,
            coupon_id=coupon.id,
            status=0
        )

        coupon.used_count += 1

        self.db.add(user_coupon)
        self.db.commit()
        self.db.refresh(user_coupon)

        return True, "领取成功", user_coupon

    def get_user_coupons(
        self,
        user_id: int,
        status: Optional[int] = None
    ) -> List[UserCoupon]:
        """获取用户优惠券列表

        Args:
            user_id: 用户ID
            status: 状态 (0未使用/1已使用/2已过期)

        Returns:
            List[UserCoupon]: 用户优惠券列表
        """
        query = self.db.query(UserCoupon).filter(UserCoupon.user_id == user_id)

        if status is not None:
            query = query.filter(UserCoupon.status == status)

        return query.order_by(UserCoupon.created_at.desc()).all()

    def get_available_coupons(self, user_id: int, order_amount: Decimal) -> List[UserCoupon]:
        """获取可用优惠券

        Args:
            user_id: 用户ID
            order_amount: 订单金额

        Returns:
            List[UserCoupon]: 可用优惠券列表
        """
        now = datetime.now()

        user_coupons = self.db.query(UserCoupon).join(Coupon).filter(
            UserCoupon.user_id == user_id,
            UserCoupon.status == 0,
            Coupon.status == 1,
            Coupon.start_at <= now,
            Coupon.expire_at >= now,
            Coupon.min_amount <= order_amount
        ).all()

        return user_coupons

    def use_coupon(
        self,
        user_coupon_id: int,
        order_id: int,
        user_id: int
    ) -> tuple[bool, str]:
        """使用优惠券

        Args:
            user_coupon_id: 用户优惠券ID
            order_id: 订单ID
            user_id: 用户ID

        Returns:
            tuple: (是否成功, 消息)
        """
        user_coupon = self.db.query(UserCoupon).filter(
            UserCoupon.id == user_coupon_id,
            UserCoupon.user_id == user_id
        ).first()

        if not user_coupon:
            return False, "优惠券不存在"

        if user_coupon.status != 0:
            return False, "优惠券已使用或已过期"

        coupon = user_coupon.coupon
        now = datetime.now()

        if now > coupon.expire_at:
            user_coupon.status = 2
            self.db.commit()
            return False, "优惠券已过期"

        user_coupon.status = 1
        user_coupon.order_id = order_id
        user_coupon.used_at = now

        self.db.commit()

        return True, "使用成功"

    def calculate_discount(
        self,
        coupon: Coupon,
        order_amount: Decimal
    ) -> Decimal:
        """计算优惠金额

        Args:
            coupon: 优惠券对象
            order_amount: 订单金额

        Returns:
            Decimal: 优惠金额
        """
        if coupon.coupon_type == "discount":
            # 折扣券：订单金额 × (1 - 折扣值)
            discount = order_amount * (Decimal(1) - coupon.discount_value / Decimal(100))
        elif coupon.coupon_type == "amount":
            # 金额券：直接减免
            discount = coupon.discount_value
        else:
            # 权限券不参与金额计算
            return Decimal(0)

        # 应用最大优惠限制
        if coupon.max_discount and discount > coupon.max_discount:
            discount = coupon.max_discount

        # 优惠金额不能超过订单金额
        if discount > order_amount:
            discount = order_amount

        return discount

    def expire_coupons(self) -> int:
        """标记过期优惠券

        Returns:
            int: 标记数量
        """
        now = datetime.now()

        # 查找所有未使用但已过期的用户优惠券
        expired_user_coupons = self.db.query(UserCoupon).join(Coupon).filter(
            UserCoupon.status == 0,
            Coupon.expire_at < now
        ).all()

        count = 0
        for uc in expired_user_coupons:
            uc.status = 2
            count += 1

        self.db.commit()

        return count
