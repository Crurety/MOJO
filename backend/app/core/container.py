"""依赖注入容器"""

from functools import lru_cache
from typing import Any, Callable, Dict, Type

from sqlalchemy.orm import Session


class Container:
    """简单的依赖注入容器"""

    def __init__(self):
        self._services: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}

    def register(self, name: str, factory: Callable, singleton: bool = False):
        """注册服务

        Args:
            name: 服务名称
            factory: 工厂函数
            singleton: 是否单例
        """
        self._services[name] = factory
        if singleton:
            self._singletons[name] = None

    def resolve(self, name: str, **kwargs) -> Any:
        """解析服务

        Args:
            name: 服务名称
            **kwargs: 额外参数

        Returns:
            服务实例
        """
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")

        # 单例模式
        if name in self._singletons:
            if self._singletons[name] is None:
                self._singletons[name] = self._services[name](**kwargs)
            return self._singletons[name]

        # 每次创建新实例
        return self._services[name](**kwargs)

    def register_class(self, service_class: Type, singleton: bool = False):
        """注册类

        Args:
            service_class: 服务类
            singleton: 是否单例
        """
        name = service_class.__name__
        self.register(name, service_class, singleton)


# 全局容器实例
container = Container()


# 注册核心服务
def setup_container():
    """设置依赖注入容器"""
    from app.services.analytics_service import AnalyticsService
    from app.services.cache_service import CacheService
    from app.services.coupon_service import CouponService
    from app.services.help_service import HelpService
    from app.services.invoice_service import InvoiceService
    from app.services.member_service import MemberService
    from app.services.notification_service import NotificationService
    from app.services.order_service import OrderService
    from app.services.permission_service import PermissionService
    from app.services.script_service import ScriptService
    from app.services.task_service import TaskService
    from app.services.ticket_service import TicketService
    from app.services.user_service import UserService
    from app.services.work_service import WorkService

    # 注册服务（非单例，每次请求创建新实例）
    container.register_class(UserService)
    container.register_class(PermissionService)
    container.register_class(OrderService)
    container.register_class(TaskService)
    container.register_class(WorkService)
    container.register_class(ScriptService)
    container.register_class(NotificationService)
    container.register_class(MemberService)
    container.register_class(AnalyticsService)
    container.register_class(CouponService)
    container.register_class(InvoiceService)
    container.register_class(TicketService)
    container.register_class(HelpService)

    # 注册单例服务
    container.register_class(CacheService, singleton=True)


def get_service(service_name: str, db: Session):
    """获取服务实例

    Args:
        service_name: 服务名称
        db: 数据库会话

    Returns:
        服务实例
    """
    return container.resolve(service_name, db=db)
