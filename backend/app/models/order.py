from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_no = Column(String(50), unique=True, nullable=False, index=True, comment="订单编号")
    order_type = Column(String(20), nullable=False, comment="订单类型: permission/balance")
    product_name = Column(String(200), nullable=False, comment="商品名称")
    amount = Column(Numeric(10, 2), nullable=False, comment="订单金额")
    payment_method = Column(String(20), nullable=True, comment="支付方式: wechat/alipay/unionpay/balance")
    payment_no = Column(String(100), nullable=True, comment="第三方支付单号")
    status = Column(Integer, default=0, nullable=False, comment="状态: 0待支付 1已支付 2已取消 3已退款")
    paid_at = Column(DateTime, nullable=True, comment="支付时间")
    remark = Column(Text, nullable=True, comment="备注")

    user = relationship("User", back_populates="orders")
