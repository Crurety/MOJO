"""营销活动服务"""

import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.member import Activity, ActivityParticipation


class ActivityService:
    """营销活动服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_activity(
        self,
        activity_code: str,
        activity_name: str,
        activity_type: str,
        description: str,
        rules: dict,
        start_at: datetime,
        end_at: datetime,
        max_participants: int = None,
        user_limit: int = 1,
        banner_url: str = None,
    ) -> Activity:
        """创建营销活动"""
        activity = Activity(
            activity_code=activity_code,
            activity_name=activity_name,
            activity_type=activity_type,
            description=description,
            rules=json.dumps(rules, ensure_ascii=False),
            start_at=start_at,
            end_at=end_at,
            max_participants=max_participants,
            user_limit=user_limit,
            banner_url=banner_url,
            status=1,
        )

        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)

        return activity

    def get_active_activities(self) -> List[Activity]:
        """获取进行中的活动"""
        now = datetime.now()
        return (
            self.db.query(Activity)
            .filter(
                Activity.status == 1, Activity.start_at <= now, Activity.end_at >= now
            )
            .order_by(Activity.priority.desc())
            .all()
        )

    def get_activity_by_code(self, activity_code: str) -> Optional[Activity]:
        """根据代码获取活动"""
        return (
            self.db.query(Activity)
            .filter(Activity.activity_code == activity_code)
            .first()
        )

    def can_participate(self, user_id: int, activity_id: int) -> tuple[bool, str]:
        """检查用户是否可以参与活动"""
        activity = self.db.query(Activity).filter(Activity.id == activity_id).first()

        if not activity:
            return False, "活动不存在"

        if activity.status != 1:
            return False, "活动已结束"

        now = datetime.now()
        if now < activity.start_at:
            return False, "活动未开始"

        if now > activity.end_at:
            return False, "活动已结束"

        # 检查人数限制
        if activity.max_participants:
            if activity.current_participants >= activity.max_participants:
                return False, "活动名额已满"

        # 检查用户参与次数
        participation = (
            self.db.query(ActivityParticipation)
            .filter(
                ActivityParticipation.activity_id == activity_id,
                ActivityParticipation.user_id == user_id,
            )
            .first()
        )

        if participation and participation.participation_count >= activity.user_limit:
            return False, f"您已达到参与次数上限（{activity.user_limit}次）"

        return True, "可以参与"

    def participate(
        self, user_id: int, activity_id: int, rewards: dict = None
    ) -> tuple[bool, str, dict]:
        """参与活动"""
        can_join, message = self.can_participate(user_id, activity_id)

        if not can_join:
            return False, message, {}

        activity = self.db.query(Activity).filter(Activity.id == activity_id).first()

        # 记录参与
        participation = (
            self.db.query(ActivityParticipation)
            .filter(
                ActivityParticipation.activity_id == activity_id,
                ActivityParticipation.user_id == user_id,
            )
            .first()
        )

        if participation:
            participation.participation_count += 1
            if rewards:
                participation.rewards = json.dumps(rewards, ensure_ascii=False)
        else:
            participation = ActivityParticipation(
                activity_id=activity_id,
                user_id=user_id,
                participation_count=1,
                rewards=json.dumps(rewards, ensure_ascii=False) if rewards else None,
            )
            self.db.add(participation)
            activity.current_participants += 1

        self.db.commit()

        return True, "参与成功", rewards or {}

    def get_user_participations(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> List[ActivityParticipation]:
        """获取用户参与记录"""
        return (
            self.db.query(ActivityParticipation)
            .filter(ActivityParticipation.user_id == user_id)
            .order_by(ActivityParticipation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_activity_statistics(self, activity_id: int) -> dict:
        """获取活动统计数据"""
        activity = self.db.query(Activity).filter(Activity.id == activity_id).first()

        if not activity:
            return {}

        # 参与人数
        participants = (
            self.db.query(ActivityParticipation)
            .filter(ActivityParticipation.activity_id == activity_id)
            .count()
        )

        # 参与次数
        total_participations = (
            self.db.query(func.sum(ActivityParticipation.participation_count))
            .filter(ActivityParticipation.activity_id == activity_id)
            .scalar()
            or 0
        )

        return {
            "activity_name": activity.activity_name,
            "participants": participants,
            "total_participations": total_participations,
            "max_participants": activity.max_participants,
            "participation_rate": round(
                (participants / activity.max_participants * 100)
                if activity.max_participants
                else 0,
                2,
            ),
        }

    def end_activity(self, activity_id: int) -> bool:
        """结束活动"""
        activity = self.db.query(Activity).filter(Activity.id == activity_id).first()

        if not activity:
            return False

        activity.status = 2
        self.db.commit()

        return True


from sqlalchemy import func
