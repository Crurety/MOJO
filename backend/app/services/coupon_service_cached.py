"""优惠券服务（带缓存优化）"""
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
        # 延迟导入避免循环依赖
        try:
            from app.services.cache_service import cache_service
            self.cache = cache_service
        except:
            self.cache = None

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
        """创建优惠券"""
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
            existing = self.db.query(Coupon).filter(Coupon.code == code).first()
            if not existing:
                return code

    def get_coupon_by_code(self, code: str) -> Optional[Coupon]:
        """根据优惠券码获取优惠券（带缓存）"""
        # 尝试从缓存获取
        if self.cache:
            cached = self.cache.get_coupon(code)
            if cached:
                return self._dict_to_coupon(cached)

        # 从数据库查询
        coupon = self.db.query(Coupon).filter(Coupon.code == code).first()

        # 存入缓存
        if coupon and self.cache:
            self.cache.set_coupon(code, self._coupon_to_dict(coupon))

        return coupon

    def _coupon_to_dict(self, coupon: Coupon) -> dict:
        """优惠券对象转字典"""
        return {
            'id': coupon.id,
            'code': coupon.code,
            'name': coupon.name,
            'coupon_type': coupon.coupon_type,
            'discount_value': float(coupon.discount_value) if coupon.discount_value else None,
            'permission_type': coupon.permission_type,
            'permission_days': coupon.permission_days,
            'min_amount': float(coupon.min_amount),
            'max_discount': float(coupon.max_discount) if coupon.max_discount else None,
            'total_count': coupon.total_count,
            'used_count': coupon.used_count,
            'start_at': coupon.start_at.isoformat() if coupon.start_at else None,
            'expire_at': coupon.expire_at.isoformat() if coupon.expire_at else None,
            'status': coupon.status
        }

    def _dict_to_coupon(self, data: dict) -> Coupon:
        """字典转优惠券对象"""
        coupon = Coupon()
        coupon.id = data['id']
        coupon.code = data['code']
        coupon.name = data['name']
        coupon.coupon_type = data['coupon_type']
        coupon.discount_value = Decimal(str(data['discount_value'])) if data['discount_value'] else None
        coupon.permission_type = data['permission_type']
        coupon.permission_days = data['permission_days']
        coupon.min_amount = Decimal(str(data['min_amount']))
        coupon.max_discount = Decimal(str(data['max_discount'])) if data['max_discount'] else None
        coupon.total_count = data['total_count']
        coupon.used_count = data['used_count']
        coupon.start_at = datetime.fromisoformat(data['start_at']) if data['start_at'] else None
        coupon.expire_at = datetime.fromisoformat(data['expire_at']) if data['expire_at'] else None
        coupon.status = data['status']
        return coupon

    def claim_coupon(self, user_id: int, coupon_code: str) -> tuple[bool, str, Optional[UserCoupon]]:
        """领取优惠券"""
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

        existing = self.db.query(UserCoupon).filter(
            UserCoupon.user_id == user_id,
            UserCoupon.coupon_id == coupon.id
        ).first()

        if existing:
            return False, "您已领取过该优惠券", None

        user_coupon = UserCoupon(
            user_id=user_id,
            coupon_id=coupon.id,
            status=0
        )

        coupon.used_count += 1

        self.db.add(user_coupon)
        self.db.commit()
        self.db.refresh(user_coupon)

        # 清除缓存
        if self.cache:
            self.cache.delete_coupon(coupon_code)

        return True, "领取成功", user_coupon

    def get_user_coupons(
        self,
        user_id: int,
        status: Optional[int] = None
    ) -> List[UserCoupon]:
        """获取用户优惠券列表"""
        query = self.db.query(UserCoupon).filter(UserCoupon.user_id == user_id)

        if status is not None:
            query = query.filter(UserCoupon.status == status)

        return query.order_by(UserCoupon.created_at.desc()).all()

    def get_available_coupons(self, user_id: int, order_amount: Decimal) -> List[UserCoupon]:
        """获取可用优惠券"""
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
        """使用优惠券"""
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
        """计算优惠金额"""
        if coupon.coupon_type == "discount":
            discount = order_amount * (Decimal(1) - coupon.discount_value / Decimal(100))
        elif coupon.coupon_type == "amount":
            discount = coupon.discount_value
        else:
            return Decimal(0)

        if coupon.max_discount and discount > coupon.max_discount:
            discount = coupon.max_discount

        if discount > order_amount:
            discount = order_amount

        return discount

    def expire_coupons(self) -> int:
        """标记过期优惠券"""
        now = datetime.now()

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
