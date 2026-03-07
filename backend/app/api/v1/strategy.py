"""运营策略API接口"""

from datetime import date

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.core.database import get_db
from app.core.rate_limit import RATE_LIMITS, limiter
from app.models import User
from app.schemas import BaseResponse
from app.services.operation_strategy_service import OperationStrategyService

router = APIRouter()


# 签到功能
@limiter.limit(RATE_LIMITS["general"])
@router.post("/sign-in", response_model=BaseResponse)
def daily_sign_in(
    request: Request,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """每日签到"""
    strategy_service = OperationStrategyService(db)
    success, message, rewards = strategy_service.daily_sign_in(current_user.id)

    if not success:
        return BaseResponse(code=400, message=message)

    return BaseResponse(
        message=message,
        data={
            "continuous_days": rewards.get("continuous_days", 1),
            "points": rewards.get("points", 0),
            "extra_reward": rewards.get("extra_reward"),
        },
    )


@limiter.limit(RATE_LIMITS["general"])
@router.get("/sign-in/status")
def get_sign_in_status(
    request: Request,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """获取签到状态"""
    strategy_service = OperationStrategyService(db)

    # 获取今日签到记录
    from app.models.operation import UserSignIn

    today = date.today()
    sign_in = (
        db.query(UserSignIn)
        .filter(UserSignIn.user_id == current_user.id, UserSignIn.sign_date == today)
        .first()
    )

    # 获取连续签到天数
    if sign_in:
        continuous_days = sign_in.continuous_days
        signed_today = True
    else:
        # 查询最近一次签到
        last_sign = (
            db.query(UserSignIn)
            .filter(UserSignIn.user_id == current_user.id)
            .order_by(UserSignIn.sign_date.desc())
            .first()
        )

        if last_sign:
            continuous_days = last_sign.continuous_days
        else:
            continuous_days = 0
        signed_today = False

    return {
        "signed_today": signed_today,
        "continuous_days": continuous_days,
        "next_reward": strategy_service._calculate_sign_in_points(continuous_days + 1),
    }


# 新用户奖励
@limiter.limit(RATE_LIMITS["general"])
@router.post("/new-user/claim", response_model=BaseResponse)
def claim_new_user_rewards(
    request: Request,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """领取新用户奖励"""
    strategy_service = OperationStrategyService(db)
    success, message, rewards = strategy_service.claim_new_user_rewards(current_user.id)

    if not success:
        return BaseResponse(code=400, message=message)

    return BaseResponse(message=message, data=rewards)


@limiter.limit(RATE_LIMITS["general"])
@router.get("/new-user/status")
def get_new_user_reward_status(
    request: Request,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """获取新用户奖励状态"""
    from app.models.operation import NewUserReward

    reward = (
        db.query(NewUserReward).filter(NewUserReward.user_id == current_user.id).first()
    )

    if not reward:
        return {
            "available": True,
            "claimed": False,
            "rewards": {"points": 100, "first_order_discount": 30},
        }

    return {
        "available": reward.status == 0,
        "claimed": reward.status == 1,
        "claimed_at": reward.claimed_at.isoformat() if reward.claimed_at else None,
    }


# 邀请奖励
class InviteClaimRequest(BaseModel):
    invite_code: str


@limiter.limit(RATE_LIMITS["general"])
@router.post("/invite/claim", response_model=BaseResponse)
def claim_invite_reward(
    request: InviteClaimRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """使用邀请码领取奖励"""
    strategy_service = OperationStrategyService(db)
    success, message, rewards = strategy_service.process_invite_reward(
        current_user.id, request.invite_code
    )

    if not success:
        return BaseResponse(code=400, message=message)

    return BaseResponse(message=message, data=rewards)


@limiter.limit(RATE_LIMITS["general"])
@router.get("/invite/my-code")
def get_my_invite_code(request: Request, current_user: User = Depends(get_current_user)):
    """获取我的邀请码"""
    return {
        "invite_code": current_user.invite_code,
        "invite_url": f"https://platform.com/register?invite={current_user.invite_code}",
    }


@limiter.limit(RATE_LIMITS["general"])
@router.get("/invite/statistics")
def get_invite_statistics(
    request: Request,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """获取邀请统计"""
    from app.models.operation import InviteReward

    # 邀请人数
    invite_count = (
        db.query(InviteReward)
        .filter(InviteReward.inviter_id == current_user.id)
        .count()
    )

    # 获得的总积分
    from sqlalchemy import func

    total_points = (
        db.query(func.sum(InviteReward.inviter_reward_points))
        .filter(
            InviteReward.inviter_id == current_user.id,
            InviteReward.inviter_reward_status == 1,
        )
        .scalar()
        or 0
    )

    return {"invite_count": invite_count, "total_reward_points": total_points}


# 内容分享奖励
class ShareRequest(BaseModel):
    work_id: int
    platform: str


@limiter.limit(RATE_LIMITS["general"])
@router.post("/share/reward", response_model=BaseResponse)
def claim_share_reward(
    request: ShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """分享内容获得奖励"""
    strategy_service = OperationStrategyService(db)
    success, message, points = strategy_service.reward_content_share(
        current_user.id, request.work_id, request.platform
    )

    if not success:
        return BaseResponse(code=400, message=message)

    return BaseResponse(message=message, data={"points": points})


# 月度活动
@limiter.limit(RATE_LIMITS["general"])
@router.get("/monthly-activity/current")
def get_current_monthly_activity(request: Request, db: Session = Depends(get_db)):
    """获取当前月度活动"""
    from datetime import datetime

    from app.models.operation import MonthlyActivity

    now = datetime.now()
    activity = (
        db.query(MonthlyActivity)
        .filter(
            MonthlyActivity.status == 1,
            MonthlyActivity.start_at <= now,
            MonthlyActivity.end_at >= now,
        )
        .first()
    )

    if not activity:
        return {"active": False}

    return {
        "active": True,
        "theme": activity.theme,
        "theme_type": activity.theme_type,
        "description": activity.description,
        "discount_rate": activity.discount_rate,
        "bonus_points_rate": activity.bonus_points_rate,
        "end_at": activity.end_at.isoformat(),
    }


# 管理员接口
class MonthlyActivityCreate(BaseModel):
    activity_month: str
    theme: str
    theme_type: str
    description: str
    discount_rate: int = 20
    bonus_points_rate: int = 200
    target_participants: int | None = None
    target_revenue: int | None = None
    start_at: str
    end_at: str


@router.post("/admin/monthly-activity", response_model=BaseResponse)
def create_monthly_activity(
    activity_in: MonthlyActivityCreate,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """创建月度活动（管理员）"""
    from datetime import datetime

    from app.models.operation import MonthlyActivity

    activity = MonthlyActivity(
        activity_month=activity_in.activity_month,
        theme=activity_in.theme,
        theme_type=activity_in.theme_type,
        description=activity_in.description,
        discount_rate=activity_in.discount_rate,
        bonus_points_rate=activity_in.bonus_points_rate,
        target_participants=activity_in.target_participants,
        target_revenue=activity_in.target_revenue,
        start_at=datetime.fromisoformat(activity_in.start_at),
        end_at=datetime.fromisoformat(activity_in.end_at),
        status=1,
    )

    db.add(activity)
    db.commit()

    return BaseResponse(message="月度活动创建成功", data={"activity_id": activity.id})


@router.get("/admin/operation/dashboard")
def get_operation_dashboard(
    current_admin=Depends(get_current_admin), db: Session = Depends(get_db)
):
    """运营数据看板（管理员）"""
    from datetime import datetime, timedelta

    from sqlalchemy import func

    from app.models.operation import InviteReward, NewUserReward, UserSignIn

    today = date.today()

    # 今日签到人数
    today_sign_ins = (
        db.query(func.count(UserSignIn.id))
        .filter(UserSignIn.sign_date == today)
        .scalar()
    )

    # 新用户奖励领取率
    total_new_users = db.query(func.count(NewUserReward.id)).scalar()
    claimed_new_users = (
        db.query(func.count(NewUserReward.id))
        .filter(NewUserReward.status == 1)
        .scalar()
    )
    claim_rate = round(
        (claimed_new_users / total_new_users * 100) if total_new_users else 0, 2
    )

    # 邀请数据
    total_invites = db.query(func.count(InviteReward.id)).scalar()

    # 本月数据
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    month_sign_ins = (
        db.query(func.count(func.distinct(UserSignIn.user_id)))
        .filter(UserSignIn.created_at >= month_start)
        .scalar()
    )

    return {
        "today_sign_ins": today_sign_ins,
        "new_user_claim_rate": claim_rate,
        "total_invites": total_invites,
        "month_active_users": month_sign_ins,
    }
