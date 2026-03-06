"""Repository基类和实现"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from app.models.base import Base
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repository基类"""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """根据ID获取"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """获取所有"""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """创建"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: int, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """更新"""
        db_obj = self.get_by_id(id)
        if db_obj:
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        """删除"""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False

    def count(self, filters: Dict[str, Any] = None) -> int:
        """计数"""
        query = self.db.query(self.model)
        if filters:
            query = self._apply_filters(query, filters)
        return query.count()

    def find_by(
        self, filters: Dict[str, Any], skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """条件查询"""
        query = self.db.query(self.model)
        query = self._apply_filters(query, filters)
        return query.offset(skip).limit(limit).all()

    def find_one_by(self, filters: Dict[str, Any]) -> Optional[ModelType]:
        """条件查询单个"""
        query = self.db.query(self.model)
        query = self._apply_filters(query, filters)
        return query.first()

    def exists(self, filters: Dict[str, Any]) -> bool:
        """检查是否存在"""
        return self.find_one_by(filters) is not None

    def _apply_filters(self, query, filters: Dict[str, Any]):
        """应用过滤条件"""
        for field, value in filters.items():
            if hasattr(self.model, field):
                if isinstance(value, (list, tuple)):
                    query = query.filter(getattr(self.model, field).in_(value))
                else:
                    query = query.filter(getattr(self.model, field) == value)
        return query


# 具体Repository实现示例
from app.models import Order, Task, User, Work


class UserRepository(BaseRepository[User]):
    """用户Repository"""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.find_one_by({"email": email})

    def get_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        return self.find_one_by({"phone": phone})

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取活跃用户"""
        return self.find_by({"status": 1}, skip, limit)


class OrderRepository(BaseRepository[Order]):
    """订单Repository"""

    def __init__(self, db: Session):
        super().__init__(Order, db)

    def get_by_order_no(self, order_no: str) -> Optional[Order]:
        """根据订单号获取"""
        return self.find_one_by({"order_no": order_no})

    def get_user_orders(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """获取用户订单"""
        return self.find_by({"user_id": user_id}, skip, limit)

    def get_paid_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """获取已支付订单"""
        return self.find_by({"status": 1}, skip, limit)


class TaskRepository(BaseRepository[Task]):
    """任务Repository"""

    def __init__(self, db: Session):
        super().__init__(Task, db)

    def get_by_task_no(self, task_no: str) -> Optional[Task]:
        """根据任务号获取"""
        return self.find_one_by({"task_no": task_no})

    def get_user_tasks(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        """获取用户任务"""
        return self.find_by({"user_id": user_id}, skip, limit)

    def get_pending_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """获取待处理任务"""
        return self.find_by({"status": 0}, skip, limit)


class WorkRepository(BaseRepository[Work]):
    """作品Repository"""

    def __init__(self, db: Session):
        super().__init__(Work, db)

    def get_user_works(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Work]:
        """获取用户作品"""
        return self.find_by({"user_id": user_id}, skip, limit)

    def get_public_works(self, skip: int = 0, limit: int = 100) -> List[Work]:
        """获取公开作品"""
        return self.find_by({"is_public": 1}, skip, limit)
