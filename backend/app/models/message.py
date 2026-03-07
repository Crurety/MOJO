from sqlalchemy import Column, Integer, BigInteger, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False, comment="消息标题")
    content = Column(Text, nullable=False, comment="消息内容")
    message_type = Column(String(20), nullable=False, comment="消息类型: system/task/promotion")
    is_read = Column(Integer, default=0, nullable=False, comment="是否已读: 0否 1是")
    link = Column(String(500), nullable=True, comment="相关链接")

    user = relationship("User", back_populates="messages")
