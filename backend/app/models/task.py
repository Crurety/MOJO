from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    task_no = Column(String(50), unique=True, nullable=False, index=True, comment="任务编号")
    task_type = Column(String(20), nullable=False, comment="任务类型: script/image/video/ad")
    status = Column(Integer, default=0, nullable=False, comment="状态: 0排队 1处理中 2完成 3失败")
    progress = Column(Integer, default=0, nullable=False, comment="进度百分比")
    parameters = Column(JSON, nullable=True, comment="任务参数JSON")
    result_url = Column(String(500), nullable=True, comment="结果URL")
    error_message = Column(Text, nullable=True, comment="错误信息")
    cost_amount = Column(Integer, default=0, nullable=False, comment="消耗使用量")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    user = relationship("User", back_populates="tasks")
    work = relationship("Work", back_populates="task", uselist=False)
