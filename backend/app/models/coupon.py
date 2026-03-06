"""优惠券模型"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from datetime import datetime


class Coupon(Base, TimestampMixin):
    """优惠券表"""
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment="优惠券码")
    name = Column(String(200), nullable=False, comment="优惠券名称")
    coupon_type = Column(String(20), nullable=False, comment="类型: discount/amount/permission")
    discount_value = Column(Numeric(10, 2), nullable=True, comment="折扣值或金额")
    permission_type = Column(String(20), nullable=True, comment="权限类型（如果是权限券）")
    permission_days = Column(Integer, nullable=True, comment="权限天数（如果是权限券）")
    min_amount = Column(Numeric(10, 2), default=0, nullable=False, comment="最低消费金额")
    max_discount = Column(Numeric(10, 2), nullable=True, comment="最大优惠金额")
    total_count = Column(Integer, default=1, nullable=False, comment="总发放数量")
    used_count = Column(Integer, default=0, nullable=False, comment="已使用数量")
    start_at = Column(DateTime, nullable=False, comment="开始时间")
    expire_at = Column(DateTime, nullable=False, comment="过期时间")
    status = Column(Integer, default=1, nullable=False, comment="状态: 0禁用 1启用")

    user_coupons = relationship("UserCoupon", back_populates="coupon", cascade="all, delete-orphan")


class UserCoupon(Base, TimestampMixin):
    """用户优惠券表"""
    __tablename__ = "user_coupons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    status = Column(Integer, default=0, nullable=False, comment="状态: 0未使用 1已使用 2已过期")
    used_at = Column(DateTime, nullable=True, comment="使用时间")

    user = relationship("User")
    coupon = relationship("Coupon", back_populates="user_coupons")
    order = relationship("Order")
