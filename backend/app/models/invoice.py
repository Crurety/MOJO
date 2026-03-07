"""发票模型"""
from sqlalchemy import Column, Integer, BigInteger, String, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Invoice(Base, TimestampMixin):
    """发票表"""
    __tablename__ = "invoices"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=True, index=True)
    invoice_no = Column(String(50), unique=True, nullable=False, index=True, comment="发票编号")
    invoice_type = Column(String(20), nullable=False, comment="发票类型: normal普通/special专用")
    invoice_title = Column(String(200), nullable=False, comment="发票抬头")
    tax_no = Column(String(50), nullable=False, comment="税号")
    amount = Column(Numeric(10, 2), nullable=False, comment="发票金额")

    # 企业信息（专用发票必填）
    company_address = Column(String(200), nullable=True, comment="企业地址")
    company_phone = Column(String(50), nullable=True, comment="企业电话")
    bank_name = Column(String(100), nullable=True, comment="开户银行")
    bank_account = Column(String(50), nullable=True, comment="银行账号")

    # 收件信息
    recipient_name = Column(String(50), nullable=False, comment="收件人姓名")
    recipient_phone = Column(String(20), nullable=False, comment="收件人电话")
    recipient_address = Column(String(500), nullable=False, comment="收件地址")

    # 发票状态
    status = Column(Integer, default=0, nullable=False, comment="状态: 0待开具 1已开具 2已邮寄 3已完成 4已拒绝")
    reject_reason = Column(Text, nullable=True, comment="拒绝原因")
    invoice_url = Column(String(500), nullable=True, comment="电子发票URL")
    tracking_no = Column(String(100), nullable=True, comment="快递单号")
    issued_at = Column(DateTime, nullable=True, comment="开具时间")
    mailed_at = Column(DateTime, nullable=True, comment="邮寄时间")

    user = relationship("User")
    order = relationship("Order")


class UserRealName(Base, TimestampMixin):
    """用户实名认证表"""
    __tablename__ = "user_real_names"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    id_card = Column(String(18), nullable=False, comment="身份证号")
    id_card_front = Column(String(500), nullable=True, comment="身份证正面照")
    id_card_back = Column(String(500), nullable=True, comment="身份证背面照")
    status = Column(Integer, default=0, nullable=False, comment="状态: 0待审核 1已通过 2已拒绝")
    reject_reason = Column(Text, nullable=True, comment="拒绝原因")
    verified_at = Column(DateTime, nullable=True, comment="认证通过时间")

    user = relationship("User")
