"""运营数据分析和营销活动API"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.core.database import get_db
from app.core.rate_limit import RATE_LIMITS, limiter
from app.models import User
from app.schemas import BaseResponse
from app.services.activity_service import ActivityService
from app.services.analytics_service import AnalyticsService
from app.services.member_service import MemberService

router = APIRouter()


# 会员积分接口
@limiter.limit(RATE_LIMITS["general"])
@router.get("/member/points")
def get_my_points(
    request: Request,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """获取我的积分"""
    member_service = MemberService(db)
    user_points = member_service.get_user_points(current_user.id)

    if not user_points:
        user_points = member_service.init_user_points(current_user.id)

    return {
        "total_points": user_points.total_points,
        "available_points": user_points.available_points,
        "used_points": user_points.used_points,
    }


@limiter.limit(RATE_LIMITS["general"])
@router.get("/member/level")
def get_my_level(
    request: Request,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """获取我的会员等级"""
    member_service = MemberService(db)
    benefits = member_service.get_member_benefits(current_user.id)
    return benefits


@limiter.limit(RATE_LIMITS["general"])
@router.get("/member/levels")
def get_all_levels(request: Request, db: Session = Depends(get_db)):
    """获取所有会员等级"""
    member_service = MemberService(db)
    levels = member_service.get_all_levels()

    return {
        "items": [
            {
                "level_name": l.level_name,
                "min_points": l.min_points,
                "max_points": l.max_points,
                "discount_rate": float(l.discount_rate),
                "free_tasks_monthly": l.free_tasks_monthly,
                "priority_support": l.priority_support == 1,
                "icon": l.icon,
                "color": l.color,
            }
            for l in levels
        ]
    }


@limiter.limit(RATE_LIMITS["general"])
@router.get("/member/points/logs")
def get_points_logs(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取积分变动记录"""
    member_service = MemberService(db)
    logs = member_service.get_points_logs(current_user.id, skip, limit)

    return {
        "items": [
            {
                "points": log.points,
                "reason": log.reason,
                "balance_after": log.balance_after,
                "created_at": log.created_at,
            }
            for log in logs
        ]
    }


@limiter.limit(RATE_LIMITS["general"])
@router.get("/member/growth/tasks")
def get_growth_tasks(
    request: Request,
    task_type: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取成长任务"""
    member_service = MemberService(db)
    tasks = member_service.get_user_growth_tasks(current_user.id, task_type)

    return {
        "items": [
            {
                "id": t.id,
                "task_name": t.task_name,
                "task_type": t.task_type,
                "progress": t.progress,
                "target": t.target,
                "reward_points": t.reward_points,
                "status": t.status,
                "completed_at": t.completed_at,
            }
            for t in tasks
        ]
    }


@limiter.limit(RATE_LIMITS["general"])
@router.post("/member/growth/tasks/{task_id}/claim", response_model=BaseResponse)
def claim_task_reward(
    request: Request,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """领取任务奖励"""
    member_service = MemberService(db)
    success, message = member_service.claim_task_reward(current_user.id, task_id)

    if not success:
        return BaseResponse(code=400, message=message)

    return BaseResponse(message=message)


# 营销活动接口
@limiter.limit(RATE_LIMITS["general"])
@router.get("/activities")
def get_active_activities(request: Request, db: Session = Depends(get_db)):
    """获取进行中的活动"""
    activity_service = ActivityService(db)
    activities = activity_service.get_active_activities()

    return {
        "items": [
            {
                "id": a.id,
                "activity_code": a.activity_code,
                "activity_name": a.activity_name,
                "activity_type": a.activity_type,
                "description": a.description,
                "start_at": a.start_at,
                "end_at": a.end_at,
                "banner_url": a.banner_url,
                "current_participants": a.current_participants,
                "max_participants": a.max_participants,
            }
            for a in activities
        ]
    }


@limiter.limit(RATE_LIMITS["general"])
@router.post("/activities/{activity_id}/participate", response_model=BaseResponse)
def participate_activity(
    request: Request,
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """参与活动"""
    activity_service = ActivityService(db)
    success, message, rewards = activity_service.participate(
        current_user.id, activity_id
    )

    if not success:
        return BaseResponse(code=400, message=message)

    return BaseResponse(message=message, data={"rewards": rewards})


@limiter.limit(RATE_LIMITS["general"])
@router.get("/activities/my")
def get_my_participations(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取我的活动参与记录"""
    activity_service = ActivityService(db)
    participations = activity_service.get_user_participations(
        current_user.id, skip, limit
    )

    return {
        "items": [
            {
                "activity_id": p.activity_id,
                "participation_count": p.participation_count,
                "rewards": p.rewards,
                "created_at": p.created_at,
            }
            for p in participations
        ]
    }


# 数据分析接口（管理员）
@router.get("/admin/analytics/users")
def get_user_analytics(
    start_date: str = Query(None),
    end_date: str = Query(None),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取用户数据分析"""
    analytics_service = AnalyticsService(db)

    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    return analytics_service.get_user_statistics(start, end)


@router.get("/admin/analytics/revenue")
def get_revenue_analytics(
    start_date: str = Query(None),
    end_date: str = Query(None),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取收入数据分析"""
    analytics_service = AnalyticsService(db)

    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    return analytics_service.get_revenue_statistics(start, end)


@router.get("/admin/analytics/content")
def get_content_analytics(
    start_date: str = Query(None),
    end_date: str = Query(None),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取内容使用分析"""
    analytics_service = AnalyticsService(db)

    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    return analytics_service.get_content_statistics(start, end)


@router.get("/admin/analytics/funnel")
def get_funnel_analytics(
    start_date: str = Query(None),
    end_date: str = Query(None),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取用户行为漏斗"""
    analytics_service = AnalyticsService(db)

    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    return analytics_service.get_funnel_analysis(start, end)


@router.get("/admin/analytics/trend")
def get_trend_analytics(
    metric: str = Query(..., regex="^(users|revenue|tasks)$"),
    days: int = Query(30, ge=1, le=365),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取趋势数据"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_trend_data(metric, days)


@router.get("/admin/analytics/rfm")
def get_rfm_analytics(
    current_admin=Depends(get_current_admin), db: Session = Depends(get_db)
):
    """获取RFM用户价值分析"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_rfm_analysis()


# 活动管理接口（管理员）
class ActivityCreate(BaseModel):
    activity_code: str
    activity_name: str
    activity_type: str
    description: str
    rules: dict
    start_at: datetime
    end_at: datetime
    max_participants: int | None = None
    user_limit: int = 1
    banner_url: str | None = None


@router.post("/admin/activities", response_model=BaseResponse)
def create_activity(
    activity_in: ActivityCreate,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """创建营销活动"""
    activity_service = ActivityService(db)
    activity = activity_service.create_activity(
        activity_code=activity_in.activity_code,
        activity_name=activity_in.activity_name,
        activity_type=activity_in.activity_type,
        description=activity_in.description,
        rules=activity_in.rules,
        start_at=activity_in.start_at,
        end_at=activity_in.end_at,
        max_participants=activity_in.max_participants,
        user_limit=activity_in.user_limit,
        banner_url=activity_in.banner_url,
    )

    return BaseResponse(message="活动创建成功", data={"activity_id": activity.id})


@router.get("/admin/activities/{activity_id}/statistics")
def get_activity_statistics(
    activity_id: int,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取活动统计数据"""
    activity_service = ActivityService(db)
    return activity_service.get_activity_statistics(activity_id)
