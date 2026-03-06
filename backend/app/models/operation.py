"""新用户激励和签到系统"""

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class UserSignIn(Base, TimestampMixin):
    """用户签到表"""

    __tablename__ = "user_sign_ins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sign_date = Column(Date, nullable=False, index=True, comment="签到日期")
    continuous_days = Column(Integer, default=1, nullable=False, comment="连续签到天数")
    reward_points = Column(Integer, default=0, nullable=False, comment="获得积分")

    user = relationship("User")


class NewUserReward(Base, TimestampMixin):
    """新用户奖励记录表"""

    __tablename__ = "new_user_rewards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True
    )
    register_points = Column(Integer, default=100, nullable=False, comment="注册积分")
    welcome_coupon_id = Column(Integer, nullable=True, comment="新人优惠券ID")
    first_order_discount = Column(
        Integer, default=30, nullable=False, comment="首单折扣（百分比）"
    )
    status = Column(Integer, default=0, nullable=False, comment="状态: 0未领取 1已领取")
    claimed_at = Column(DateTime, nullable=True, comment="领取时间")

    user = relationship("User")


class InviteReward(Base, TimestampMixin):
    """邀请奖励记录表"""

    __tablename__ = "invite_rewards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inviter_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True, comment="邀请人ID"
    )
    invitee_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="被邀请人ID",
    )
    inviter_reward_points = Column(
        Integer, default=50, nullable=False, comment="邀请人奖励积分"
    )
    invitee_reward_points = Column(
        Integer, default=50, nullable=False, comment="被邀请人奖励积分"
    )
    inviter_reward_status = Column(
        Integer, default=0, nullable=False, comment="邀请人奖励状态: 0待发放 1已发放"
    )
    invitee_reward_status = Column(
        Integer, default=0, nullable=False, comment="被邀请人奖励状态: 0待发放 1已发放"
    )

    inviter = relationship("User", foreign_keys=[inviter_id])
    invitee = relationship("User", foreign_keys=[invitee_id])


class ContentShareReward(Base, TimestampMixin):
    """内容分享奖励表"""

    __tablename__ = "content_share_rewards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False, index=True)
    share_platform = Column(String(50), nullable=False, comment="分享平台")
    share_count = Column(Integer, default=1, nullable=False, comment="分享次数")
    reward_points = Column(Integer, default=10, nullable=False, comment="奖励积分")

    user = relationship("User")
    work = relationship("Work")


class QualityContentReward(Base, TimestampMixin):
    """优质内容激励表"""

    __tablename__ = "quality_content_rewards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False, index=True)
    quality_score = Column(Integer, nullable=False, comment="质量评分")
    reward_type = Column(
        String(50), nullable=False, comment="奖励类型: points/coupon/permission"
    )
    reward_value = Column(String(200), nullable=False, comment="奖励内容")
    status = Column(Integer, default=0, nullable=False, comment="状态: 0待发放 1已发放")

    user = relationship("User")
    work = relationship("Work")


class MonthlyActivity(Base, TimestampMixin):
    """月度主题活动表"""

    __tablename__ = "monthly_activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_month = Column(
        String(7), nullable=False, index=True, comment="活动月份 YYYY-MM"
    )
    theme = Column(String(200), nullable=False, comment="活动主题")
    theme_type = Column(
        String(50), nullable=False, comment="主题类型: festival/anniversary/seasonal"
    )
    description = Column(String(1000), nullable=True, comment="活动描述")

    # 活动奖励配置
    discount_rate = Column(
        Integer, default=20, nullable=False, comment="折扣力度（百分比）"
    )
    bonus_points_rate = Column(
        Integer, default=200, nullable=False, comment="积分倍率（百分比）"
    )
    special_gifts = Column(String(500), nullable=True, comment="特殊礼品，JSON格式")

    # 活动目标
    target_participants = Column(Integer, nullable=True, comment="目标参与人数")
    target_revenue = Column(Integer, nullable=True, comment="目标收入")

    # 活动状态
    status = Column(
        Integer, default=1, nullable=False, comment="状态: 0未开始 1进行中 2已结束"
    )
    start_at = Column(DateTime, nullable=False, comment="开始时间")
    end_at = Column(DateTime, nullable=False, comment="结束时间")


class UserSegment(Base, TimestampMixin):
    """用户分层标签表"""

    __tablename__ = "user_segments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    segment_type = Column(
        String(50), nullable=False, comment="分层类型: rfm/behavior/value"
    )
    segment_value = Column(String(50), nullable=False, comment="分层值")
    score = Column(Integer, nullable=True, comment="评分")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")

    user = relationship("User")
