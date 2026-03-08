from sqlalchemy import BigInteger, Column, DateTime, Integer, String

from app.models.base import Base, TimestampMixin


class AdminUser(Base, TimestampMixin):
    __tablename__ = "admin_users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    password = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=True)
    role = Column(String(20), nullable=False, default="admin")
    status = Column(Integer, default=1, nullable=False, comment="0 disabled, 1 active")
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(50), nullable=True)
