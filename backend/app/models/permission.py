from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
import enum


class PermissionType(str, enum.Enum):
    SCRIPT = "script"
    IMAGE = "image"
    VIDEO = "video"
    AD = "ad"


class PaymentMode(str, enum.Enum):
    PER_USE = "per_use"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class UserPermission(Base, TimestampMixin):
    __tablename__ = "user_permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    permission_type = Column(String(20), nullable=False, comment="权限类型: script/image/video/ad")
    payment_mode = Column(String(20), nullable=False, comment="付费模式: per_use/monthly/yearly")
    total_count = Column(Integer, default=0, nullable=False, comment="总次数(按次付费)")
    used_count = Column(Integer, default=0, nullable=False, comment="已使用次数")
    expire_at = Column(DateTime, nullable=True, comment="到期时间(包月/包年)")
    status = Column(Integer, default=1, nullable=False, comment="状态: 0无效 1有效")

    user = relationship("User", back_populates="permissions")
