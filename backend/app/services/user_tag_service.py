"""用户标签服务"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import Order, Task, User
from app.models.advanced_operation import UserTag, UserTagRelation


class UserTagService:
    """用户标签服务"""

    def __init__(self, db: Session):
        self.db = db

    # 标签管理
    def create_tag(
        self,
        tag_name: str,
        tag_category: str,
        tag_type: str = "manual",
        description: str = None,
        color: str = None,
    ) -> UserTag:
        """创建标签"""
        tag = UserTag(
            tag_name=tag_name,
            tag_category=tag_category,
            tag_type=tag_type,
            description=description,
            color=color,
            status=1,
        )

        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)

        return tag

    def get_all_tags(self, category: str = None) -> List[UserTag]:
        """获取所有标签"""
        query = self.db.query(UserTag).filter(UserTag.status == 1)

        if category:
            query = query.filter(UserTag.tag_category == category)

        return query.all()

    # 用户打标签
    def add_user_tag(
        self,
        user_id: int,
        tag_id: int,
        tag_source: str = "manual",
        confidence: int = 100,
        expire_at: datetime = None,
    ) -> UserTagRelation:
        """给用户添加标签"""
        # 检查是否已存在
        existing = (
            self.db.query(UserTagRelation)
            .filter(
                UserTagRelation.user_id == user_id, UserTagRelation.tag_id == tag_id
            )
            .first()
        )

        if existing:
            existing.confidence = confidence
            existing.expire_at = expire_at
            self.db.commit()
            return existing

        relation = UserTagRelation(
            user_id=user_id,
            tag_id=tag_id,
            tag_source=tag_source,
            confidence=confidence,
            expire_at=expire_at,
        )

        self.db.add(relation)
        self.db.commit()
        self.db.refresh(relation)

        return relation

    def remove_user_tag(self, user_id: int, tag_id: int) -> bool:
        """移除用户标签"""
        relation = (
            self.db.query(UserTagRelation)
            .filter(
                UserTagRelation.user_id == user_id, UserTagRelation.tag_id == tag_id
            )
            .first()
        )

        if relation:
            self.db.delete(relation)
            self.db.commit()
            return True

        return False

    def get_user_tags(self, user_id: int) -> List[UserTag]:
        """获取用户的所有标签"""
        relations = (
            self.db.query(UserTagRelation)
            .filter(UserTagRelation.user_id == user_id)
            .all()
        )

        tag_ids = [r.tag_id for r in relations]

        return (
            self.db.query(UserTag)
            .filter(UserTag.id.in_(tag_ids), UserTag.status == 1)
            .all()
        )

    def get_users_by_tag(self, tag_id: int) -> List[int]:
        """根据标签获取用户ID列表"""
        relations = (
            self.db.query(UserTagRelation)
            .filter(UserTagRelation.tag_id == tag_id)
            .all()
        )

        return [r.user_id for r in relations]

    def get_users_by_tags(
        self, tag_ids: List[int], match_all: bool = False
    ) -> List[int]:
        """根据多个标签获取用户（支持AND/OR逻辑）"""
        if match_all:
            # AND逻辑：用户必须拥有所有标签
            user_ids = None
            for tag_id in tag_ids:
                tag_users = set(self.get_users_by_tag(tag_id))
                if user_ids is None:
                    user_ids = tag_users
                else:
                    user_ids = user_ids.intersection(tag_users)
            return list(user_ids) if user_ids else []
        else:
            # OR逻辑：用户拥有任一标签即可
            user_ids = set()
            for tag_id in tag_ids:
                user_ids.update(self.get_users_by_tag(tag_id))
            return list(user_ids)

    # 自动打标签
    def auto_tag_high_value_users(self):
        """自动标记高价值用户"""
        # 查找高价值用户（消费金额>1000或订单数>10）
        from sqlalchemy import func

        high_value_users = (
            self.db.query(
                Order.user_id,
                func.sum(Order.amount).label("total_amount"),
                func.count(Order.id).label("order_count"),
            )
            .filter(Order.status == 1)
            .group_by(Order.user_id)
            .having((func.sum(Order.amount) > 1000) | (func.count(Order.id) > 10))
            .all()
        )

        # 获取或创建"高价值用户"标签
        tag = self.db.query(UserTag).filter(UserTag.tag_name == "高价值用户").first()

        if not tag:
            tag = self.create_tag(
                tag_name="高价值用户",
                tag_category="value",
                tag_type="auto",
                description="消费金额>1000或订单数>10",
                color="#FFD700",
            )

        # 给用户打标签
        count = 0
        for user in high_value_users:
            self.add_user_tag(
                user_id=user.user_id, tag_id=tag.id, tag_source="auto", confidence=100
            )
            count += 1

        return count

    def auto_tag_active_users(self):
        """自动标记活跃用户"""
        # 最近7天有登录的用户
        active_date = datetime.now() - timedelta(days=7)
        active_users = (
            self.db.query(User.id).filter(User.last_login_at >= active_date).all()
        )

        # 获取或创建"活跃用户"标签
        tag = self.db.query(UserTag).filter(UserTag.tag_name == "活跃用户").first()

        if not tag:
            tag = self.create_tag(
                tag_name="活跃用户",
                tag_category="behavior",
                tag_type="auto",
                description="最近7天有登录",
                color="#00FF00",
            )

        # 给用户打标签
        count = 0
        for user in active_users:
            self.add_user_tag(
                user_id=user.id,
                tag_id=tag.id,
                tag_source="auto",
                confidence=100,
                expire_at=datetime.now() + timedelta(days=7),
            )
            count += 1

        return count

    def auto_tag_content_creators(self):
        """自动标记内容创作者"""
        # 创作任务数>5的用户
        from sqlalchemy import func

        creators = (
            self.db.query(Task.user_id, func.count(Task.id).label("task_count"))
            .filter(
                Task.status == 2  # 已完成
            )
            .group_by(Task.user_id)
            .having(func.count(Task.id) > 5)
            .all()
        )

        # 获取或创建"内容创作者"标签
        tag = self.db.query(UserTag).filter(UserTag.tag_name == "内容创作者").first()

        if not tag:
            tag = self.create_tag(
                tag_name="内容创作者",
                tag_category="behavior",
                tag_type="auto",
                description="创作任务数>5",
                color="#FF69B4",
            )

        # 给用户打标签
        count = 0
        for creator in creators:
            self.add_user_tag(
                user_id=creator.user_id,
                tag_id=tag.id,
                tag_source="auto",
                confidence=100,
            )
            count += 1

        return count

    def clean_expired_tags(self):
        """清理过期标签"""
        now = datetime.now()

        expired_relations = (
            self.db.query(UserTagRelation).filter(UserTagRelation.expire_at < now).all()
        )

        count = 0
        for relation in expired_relations:
            self.db.delete(relation)
            count += 1

        self.db.commit()

        return count
