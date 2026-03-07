"""用户标签系统模型"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, BigInteger, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class UserTag(Base, TimestampMixin):
    """用户标签表"""

    __tablename__ = "user_tags"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    tag_name = Column(String(50), unique=True, nullable=False, comment="标签名称")
    tag_category = Column(
        String(50), nullable=False, comment="标签分类: behavior/preference/value/custom"
    )
    tag_type = Column(String(20), nullable=False, comment="标签类型: auto/manual")
    description = Column(Text, nullable=True, comment="标签描述")
    color = Column(String(20), nullable=True, comment="标签颜色")
    status = Column(Integer, default=1, nullable=False, comment="状态: 0禁用 1启用")


class UserTagRelation(Base, TimestampMixin):
    """用户标签关系表"""

    __tablename__ = "user_tag_relations"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    tag_id = Column(BigInteger, ForeignKey("user_tags.id"), nullable=False, index=True)
    tag_source = Column(String(20), nullable=False, comment="标签来源: auto/manual")
    confidence = Column(Integer, default=100, nullable=False, comment="置信度 0-100")
    expire_at = Column(DateTime, nullable=True, comment="过期时间")

    user = relationship("User")
    tag = relationship("UserTag")


class ABTest(Base, TimestampMixin):
    """AB测试表"""

    __tablename__ = "ab_tests"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    test_name = Column(String(100), nullable=False, comment="测试名称")
    test_key = Column(
        String(50), unique=True, nullable=False, index=True, comment="测试标识"
    )
    description = Column(Text, nullable=True, comment="测试描述")

    # 测试配置
    variants = Column(Text, nullable=False, comment="变体配置，JSON格式")
    traffic_allocation = Column(Text, nullable=False, comment="流量分配，JSON格式")

    # 测试目标
    primary_metric = Column(String(50), nullable=False, comment="主要指标")
    secondary_metrics = Column(Text, nullable=True, comment="次要指标，JSON格式")

    # 测试状态
    status = Column(
        Integer,
        default=0,
        nullable=False,
        comment="状态: 0草稿 1运行中 2已暂停 3已结束",
    )
    start_at = Column(DateTime, nullable=True, comment="开始时间")
    end_at = Column(DateTime, nullable=True, comment="结束时间")

    # 测试结果
    winner_variant = Column(String(50), nullable=True, comment="获胜变体")
    result_summary = Column(Text, nullable=True, comment="结果摘要，JSON格式")


class ABTestAssignment(Base, TimestampMixin):
    """AB测试分配表"""

    __tablename__ = "ab_test_assignments"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    test_id = Column(BigInteger, ForeignKey("ab_tests.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    variant = Column(String(50), nullable=False, comment="分配的变体")

    test = relationship("ABTest")
    user = relationship("User")


class ABTestMetric(Base, TimestampMixin):
    """AB测试指标记录表"""

    __tablename__ = "ab_test_metrics"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    test_id = Column(BigInteger, ForeignKey("ab_tests.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    variant = Column(String(50), nullable=False, comment="变体")
    metric_name = Column(String(50), nullable=False, comment="指标名称")
    metric_value = Column(String(100), nullable=False, comment="指标值")

    test = relationship("ABTest")
    user = relationship("User")


class PushNotification(Base, TimestampMixin):
    """推送通知表"""

    __tablename__ = "push_notifications"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    notification_type = Column(
        String(20), nullable=False, comment="通知类型: site/email/sms/app"
    )
    target_type = Column(
        String(20), nullable=False, comment="目标类型: all/segment/user"
    )
    target_value = Column(Text, nullable=True, comment="目标值，JSON格式")

    # 通知内容
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, nullable=False, comment="通知内容")
    link = Column(String(500), nullable=True, comment="跳转链接")
    image_url = Column(String(500), nullable=True, comment="图片URL")

    # 发送配置
    send_at = Column(DateTime, nullable=True, comment="定时发送时间")
    status = Column(
        Integer,
        default=0,
        nullable=False,
        comment="状态: 0待发送 1发送中 2已发送 3已取消",
    )

    # 发送统计
    total_count = Column(Integer, default=0, nullable=False, comment="总发送数")
    success_count = Column(Integer, default=0, nullable=False, comment="成功数")
    failed_count = Column(Integer, default=0, nullable=False, comment="失败数")
    click_count = Column(Integer, default=0, nullable=False, comment="点击数")


class PushNotificationLog(Base, TimestampMixin):
    """推送通知日志表"""

    __tablename__ = "push_notification_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    notification_id = Column(
        BigInteger, ForeignKey("push_notifications.id"), nullable=False, index=True
    )
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(Integer, nullable=False, comment="状态: 0失败 1成功")
    error_message = Column(Text, nullable=True, comment="错误信息")
    clicked = Column(Integer, default=0, nullable=False, comment="是否点击: 0否 1是")
    clicked_at = Column(DateTime, nullable=True, comment="点击时间")

    notification = relationship("PushNotification")
    user = relationship("User")
