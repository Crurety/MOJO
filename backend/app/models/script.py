from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Script(Base, TimestampMixin):
    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False, comment="脚本内容")
    output_type = Column(String(20), nullable=False, comment="输出类型: image_set/single_image/video")
    parameters = Column(JSON, nullable=True, comment="生成参数JSON")
    status = Column(Integer, default=1, nullable=False, comment="状态: 0草稿 1已生成")

    user = relationship("User", back_populates="scripts")
