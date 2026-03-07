"""自动化营销模型"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, BigInteger, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class AutomationRule(Base, TimestampMixin):
    """自动化营销规则表"""

    __tablename__ = "automation_rules"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    rule_name = Column(String(200), nullable=False, comment="规则名称")
    rule_type = Column(
        String(50), nullable=False, comment="规则类型: trigger/lifecycle/churn"
    )
    trigger_event = Column(String(100), nullable=False, comment="触发事件")
    trigger_conditions = Column(Text, nullable=True, comment="触发条件，JSON格式")
    actions = Column(Text, nullable=False, comment="执行动作，JSON格式")

    # 统计
    execution_count = Column(Integer, default=0, nullable=False, comment="执行次数")
    success_count = Column(Integer, default=0, nullable=False, comment="成功次数")

    # 状态
    status = Column(Integer, default=1, nullable=False, comment="状态: 0禁用 1启用")


class AutomationExecution(Base, TimestampMixin):
    """自动化执行记录表"""

    __tablename__ = "automation_executions"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    rule_id = Column(
        BigInteger, ForeignKey("automation_rules.id"), nullable=False, index=True
    )
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    trigger_data = Column(Text, nullable=True, comment="触发数据，JSON格式")
    status = Column(Integer, nullable=False, comment="状态: 1成功 2失败")
    error_message = Column(Text, nullable=True, comment="错误信息")
    executed_at = Column(DateTime, nullable=False, comment="执行时间")

    rule = relationship("AutomationRule")
    user = relationship("User")
