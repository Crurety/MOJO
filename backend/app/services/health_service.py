"""健康检查服务"""

from typing import Dict

import httpx
from sqlalchemy.orm import Session

from app.core.database import engine
from app.core.mongodb_logger import mongo_logger
from app.utils.redis import redis_client


class HealthCheckService:
    """健康检查服务"""

    @staticmethod
    def check_database() -> Dict:
        """检查数据库连接"""
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return {"status": "healthy", "message": "Database connection OK"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Database error: {str(e)}"}

    @staticmethod
    def check_redis() -> Dict:
        """检查Redis连接"""
        try:
            redis_client.ping()
            return {"status": "healthy", "message": "Redis connection OK"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Redis error: {str(e)}"}

    @staticmethod
    def check_mongodb() -> Dict:
        """检查MongoDB连接"""
        try:
            mongo_logger.client.server_info()
            return {"status": "healthy", "message": "MongoDB connection OK"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"MongoDB error: {str(e)}"}

    @staticmethod
    async def check_external_services() -> Dict:
        """检查外部服务"""
        services = {}

        # 检查OpenAI
        try:
            from app.core.config import settings

            if settings.OPENAI_API_KEY:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(
                        f"{settings.OPENAI_API_BASE or 'https://api.openai.com'}/v1/models",
                        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                    )
                    services["openai"] = {
                        "status": "healthy"
                        if response.status_code == 200
                        else "unhealthy",
                        "message": "OpenAI API accessible",
                    }
            else:
                services["openai"] = {
                    "status": "not_configured",
                    "message": "API key not set",
                }
        except Exception as e:
            services["openai"] = {"status": "unhealthy", "message": str(e)}

        return services

    @staticmethod
    def get_system_info() -> Dict:
        """获取系统信息"""
        import platform

        import psutil

        return {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
        }

    @classmethod
    async def full_health_check(cls) -> Dict:
        """完整健康检查"""
        return {
            "status": "healthy",
            "timestamp": str(datetime.now()),
            "checks": {
                "database": cls.check_database(),
                "redis": cls.check_redis(),
                "mongodb": cls.check_mongodb(),
                "external_services": await cls.check_external_services(),
            },
            "system": cls.get_system_info(),
        }


from datetime import datetime
