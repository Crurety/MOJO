"""Member points and level services."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.member import MemberLevel, PointsLog, UserGrowth, UserPoints


class MemberService:
    def __init__(self, db: Session):
        self.db = db

    # Level management
    def get_all_levels(self) -> List[MemberLevel]:
        return (
            self.db.query(MemberLevel)
            .filter(MemberLevel.status == 1)
            .order_by(MemberLevel.sort_order)
            .all()
        )

    def get_level_by_points(self, points: int) -> Optional[MemberLevel]:
        return (
            self.db.query(MemberLevel)
            .filter(
                MemberLevel.status == 1,
                MemberLevel.min_points <= points,
                or_(MemberLevel.max_points.is_(None), MemberLevel.max_points >= points),
            )
            .first()
        )

    # Points management
    def get_user_points(self, user_id: int) -> Optional[UserPoints]:
        user_points = (
            self.db.query(UserPoints).filter(UserPoints.user_id == user_id).first()
        )
        if not user_points:
            user_points = self.init_user_points(user_id)
        return user_points

    def init_user_points(self, user_id: int) -> UserPoints:
        user_points = UserPoints(
            user_id=user_id,
            total_points=0,
            available_points=0,
            used_points=0,
        )
        self.db.add(user_points)
        self.db.commit()
        self.db.refresh(user_points)
        return user_points

    def add_points(
        self,
        user_id: int,
        points: int,
        reason: str | None = None,
        related_type: str | None = None,
        related_id: int | None = None,
        source: str | None = None,
        description: str | None = None,
    ) -> tuple[bool, str]:
        reason_text = reason or source or description or "points_add"
        user_points = self.get_user_points(user_id)
        if not user_points:
            return False, "用户积分初始化失败"

        user_points.total_points += points
        user_points.available_points += points

        new_level = self.get_level_by_points(user_points.total_points)
        if new_level:
            user_points.level_id = new_level.id

        log = PointsLog(
            user_id=user_id,
            points=points,
            reason=reason_text,
            related_type=related_type,
            related_id=related_id,
            balance_after=user_points.available_points,
        )

        self.db.add(log)
        self.db.commit()
        return True, "增加成功"

    def deduct_points(
        self,
        user_id: int,
        points: int,
        reason: str,
        related_type: str | None = None,
        related_id: int | None = None,
    ) -> tuple[bool, str]:
        user_points = self.get_user_points(user_id)
        if not user_points:
            return False, "用户积分记录不存在"

        if user_points.available_points < points:
            return False, "积分不足"

        user_points.available_points -= points
        user_points.used_points += points

        log = PointsLog(
            user_id=user_id,
            points=-points,
            reason=reason,
            related_type=related_type,
            related_id=related_id,
            balance_after=user_points.available_points,
        )

        self.db.add(log)
        self.db.commit()
        return True, "扣除成功"

    # Backward-compatible alias used by tests.
    def consume_points(
        self,
        user_id: int,
        points: int,
        reason: str,
        description: str | None = None,
    ) -> tuple[bool, str]:
        actual_reason = description or reason
        return self.deduct_points(user_id=user_id, points=points, reason=actual_reason)

    def get_points_logs(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> List[PointsLog]:
        return (
            self.db.query(PointsLog)
            .filter(PointsLog.user_id == user_id)
            .order_by(PointsLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # Growth tasks
    def get_user_growth_tasks(
        self, user_id: int, task_type: str | None = None
    ) -> List[UserGrowth]:
        query = self.db.query(UserGrowth).filter(UserGrowth.user_id == user_id)
        if task_type:
            query = query.filter(UserGrowth.task_type == task_type)
        return query.order_by(UserGrowth.status, UserGrowth.created_at.desc()).all()

    def update_task_progress(self, user_id: int, task_code: str, progress: int) -> bool:
        task = (
            self.db.query(UserGrowth)
            .filter(
                UserGrowth.user_id == user_id,
                UserGrowth.task_code == task_code,
                UserGrowth.status == 0,
            )
            .first()
        )
        if not task:
            return False

        task.progress = progress
        if progress >= task.target:
            task.status = 1
            task.completed_at = datetime.now()

        self.db.commit()
        return True

    def claim_task_reward(self, user_id: int, task_id: int) -> tuple[bool, str]:
        task = (
            self.db.query(UserGrowth)
            .filter(UserGrowth.id == task_id, UserGrowth.user_id == user_id)
            .first()
        )
        if not task:
            return False, "任务不存在"
        if task.status != 1:
            return False, "任务未完成"

        if task.reward_points > 0:
            self.add_points(
                user_id=user_id,
                points=task.reward_points,
                reason=f"完成任务：{task.task_name}",
                related_type="growth_task",
                related_id=task.id,
            )

        task.status = 2
        self.db.commit()
        return True, "奖励领取成功"

    # Member benefits
    def get_member_benefits(self, user_id: int) -> dict:
        user_points = self.get_user_points(user_id)
        if not user_points or not user_points.level_id:
            return {
                "level_name": "普通会员",
                "discount_rate": 100,
                "free_tasks_monthly": 0,
                "priority_support": False,
            }

        level = (
            self.db.query(MemberLevel).filter(MemberLevel.id == user_points.level_id).first()
        )
        if not level:
            return {
                "level_name": "普通会员",
                "discount_rate": 100,
                "free_tasks_monthly": 0,
                "priority_support": False,
            }

        return {
            "level_name": level.level_name,
            "discount_rate": float(level.discount_rate),
            "free_tasks_monthly": level.free_tasks_monthly,
            "priority_support": level.priority_support == 1,
            "icon": level.icon,
            "color": level.color,
        }
