"""会员等级和积分系统模型"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class MemberLevel(Base, TimestampMixin):
    """会员等级表"""

    __tablename__ = "member_levels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    level_name = Column(String(50), nullable=False, comment="等级名称")
    level_code = Column(String(20), unique=True, nullable=False, comment="等级代码")
    min_points = Column(Integer, default=0, nullable=False, comment="最低积分")
    max_points = Column(Integer, nullable=True, comment="最高积分")
    discount_rate = Column(
        Numeric(5, 2), default=100, nullable=False, comment="折扣率（100=无折扣）"
    )

    # 权益
    free_tasks_monthly = Column(
        Integer, default=0, nullable=False, comment="每月免费任务数"
    )
    priority_support = Column(
        Integer, default=0, nullable=False, comment="优先客服: 0否 1是"
    )
    exclusive_features = Column(Text, nullable=True, comment="专属功能，JSON格式")

    # 显示
    icon = Column(String(200), nullable=True, comment="等级图标")
    color = Column(String(20), nullable=True, comment="等级颜色")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序")
    status = Column(Integer, default=1, nullable=False, comment="状态: 0禁用 1启用")


class UserPoints(Base, TimestampMixin):
    """用户积分表"""

    __tablename__ = "user_points"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True
    )
    total_points = Column(Integer, default=0, nullable=False, comment="总积分")
    available_points = Column(Integer, default=0, nullable=False, comment="可用积分")
    used_points = Column(Integer, default=0, nullable=False, comment="已使用积分")
    level_id = Column(
        Integer, ForeignKey("member_levels.id"), nullable=True, comment="当前等级"
    )

    user = relationship("User")
    level = relationship("MemberLevel")


class PointsLog(Base, TimestampMixin):
    """积分变动记录表"""

    __tablename__ = "points_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    points = Column(Integer, nullable=False, comment="积分变动（正数增加，负数减少）")
    reason = Column(String(100), nullable=False, comment="变动原因")
    related_type = Column(
        String(50), nullable=True, comment="关联类型: order/task/activity"
    )
    related_id = Column(Integer, nullable=True, comment="关联ID")
    balance_after = Column(Integer, nullable=False, comment="变动后余额")

    user = relationship("User")


class Activity(Base, TimestampMixin):
    """营销活动表"""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_code = Column(
        String(50), unique=True, nullable=False, index=True, comment="活动代码"
    )
    activity_name = Column(String(200), nullable=False, comment="活动名称")
    activity_type = Column(
        String(50), nullable=False, comment="活动类型: discount/gift/points/newuser"
    )
    description = Column(Text, nullable=True, comment="活动描述")

    # 活动规则
    rules = Column(Text, nullable=True, comment="活动规则，JSON格式")

    # 活动时间
    start_at = Column(DateTime, nullable=False, comment="开始时间")
    end_at = Column(DateTime, nullable=False, comment="结束时间")

    # 参与限制
    max_participants = Column(Integer, nullable=True, comment="最大参与人数")
    current_participants = Column(
        Integer, default=0, nullable=False, comment="当前参与人数"
    )
    user_limit = Column(Integer, default=1, nullable=False, comment="每人参与次数限制")

    # 活动状态
    status = Column(
        Integer, default=1, nullable=False, comment="状态: 0禁用 1启用 2已结束"
    )

    # 展示
    banner_url = Column(String(500), nullable=True, comment="活动横幅")
    priority = Column(Integer, default=0, nullable=False, comment="优先级")


class ActivityParticipation(Base, TimestampMixin):
    """活动参与记录表"""

    __tablename__ = "activity_participations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(
        Integer, ForeignKey("activities.id"), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    participation_count = Column(Integer, default=1, nullable=False, comment="参与次数")
    rewards = Column(Text, nullable=True, comment="获得奖励，JSON格式")

    activity = relationship("Activity")
    user = relationship("User")


class UserGrowth(Base, TimestampMixin):
    """用户成长任务表"""

    __tablename__ = "user_growth"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    task_type = Column(
        String(50), nullable=False, comment="任务类型: daily/weekly/achievement"
    )
    task_code = Column(String(50), nullable=False, comment="任务代码")
    task_name = Column(String(200), nullable=False, comment="任务名称")
    progress = Column(Integer, default=0, nullable=False, comment="当前进度")
    target = Column(Integer, nullable=False, comment="目标值")
    reward_points = Column(Integer, default=0, nullable=False, comment="奖励积分")
    status = Column(
        Integer, default=0, nullable=False, comment="状态: 0进行中 1已完成 2已领取"
    )
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    user = relationship("User")
