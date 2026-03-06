"""数据库连接池配置"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 数据库引擎配置（优化版）
engine = create_engine(
    settings.DATABASE_URL,
    # 连接池配置
    poolclass=QueuePool,
    pool_size=20,  # 连接池大小
    max_overflow=40,  # 最大溢出连接数
    pool_timeout=30,  # 获取连接超时时间
    pool_recycle=3600,  # 连接回收时间（1小时）
    pool_pre_ping=True,  # 连接前检查
    # 性能优化
    echo=False,  # 生产环境关闭SQL日志
    echo_pool=False,  # 关闭连接池日志
    # 编码设置
    connect_args={
        "charset": "utf8mb4",
        "connect_timeout": 10
    } if "mysql" in settings.DATABASE_URL else {}
)

# 会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # 提交后不过期对象
)


# 连接池事件监听
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """连接建立时的回调"""
    logger.debug("Database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """从连接池获取连接时的回调"""
    pass


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """连接归还到连接池时的回调"""
    pass


def get_db() -> Session:
    """获取数据库会话（依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_context():
    """获取数据库会话（上下文管理器）"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


# 连接池状态监控
def get_pool_status() -> dict:
    """获取连接池状态"""
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total": pool.size() + pool.overflow()
    }
