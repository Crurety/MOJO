"""客服工单模型"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Ticket(Base, TimestampMixin):
    """工单表"""
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    ticket_no = Column(String(50), unique=True, nullable=False, index=True, comment="工单编号")
    category = Column(String(50), nullable=False, comment="工单分类")
    subject = Column(String(200), nullable=False, comment="工单主题")
    content = Column(Text, nullable=False, comment="工单内容")
    priority = Column(Integer, default=1, nullable=False, comment="优先级: 1低 2中 3高 4紧急")
    status = Column(Integer, default=0, nullable=False, comment="状态: 0待处理 1处理中 2已回复 3已解决 4已关闭")
    assigned_to = Column(Integer, nullable=True, index=True, comment="分配给客服ID")
    resolved_at = Column(DateTime, nullable=True, comment="解决时间")
    closed_at = Column(DateTime, nullable=True, comment="关闭时间")

    user = relationship("User")
    replies = relationship("TicketReply", back_populates="ticket", cascade="all, delete-orphan")


class TicketReply(Base, TimestampMixin):
    """工单回复表"""
    __tablename__ = "ticket_replies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True, comment="回复人ID")
    is_staff = Column(Integer, default=0, nullable=False, comment="是否客服: 0用户 1客服")
    content = Column(Text, nullable=False, comment="回复内容")
    attachments = Column(Text, nullable=True, comment="附件URL，逗号分隔")

    ticket = relationship("Ticket", back_populates="replies")


class Feedback(Base, TimestampMixin):
    """用户反馈表"""
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    feedback_type = Column(String(50), nullable=False, comment="反馈类型")
    content = Column(Text, nullable=False, comment="反馈内容")
    contact = Column(String(100), nullable=True, comment="联系方式")
    status = Column(Integer, default=0, nullable=False, comment="状态: 0待处理 1已处理")
    reply = Column(Text, nullable=True, comment="回复内容")
    replied_at = Column(DateTime, nullable=True, comment="回复时间")

    user = relationship("User")
