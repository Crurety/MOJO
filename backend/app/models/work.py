from sqlalchemy import Column, Integer, BigInteger, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Work(Base, TimestampMixin):
    __tablename__ = "works"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    task_id = Column(BigInteger, ForeignKey("tasks.id"), nullable=True, index=True)
    work_type = Column(String(20), nullable=False, comment="作品类型: image/video/ad")
    title = Column(String(200), nullable=True)
    file_url = Column(String(500), nullable=False, comment="文件URL")
    thumbnail_url = Column(String(500), nullable=True, comment="缩略图URL")
    parameters = Column(JSON, nullable=True, comment="生成参数JSON")
    is_public = Column(Integer, default=0, nullable=False, comment="是否公开: 0否 1是")
    quality_score = Column(Integer, nullable=True, comment="质量评分(用于作品集筛选)")

    user = relationship("User", back_populates="works")
    task = relationship("Task", back_populates="work")
