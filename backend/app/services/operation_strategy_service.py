"""运营策略实施服务"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import User
from app.models.operation import (
    ContentShareReward,
    InviteReward,
    MonthlyActivity,
    NewUserReward,
    QualityContentReward,
    UserSegment,
    UserSignIn,
)
from app.services.coupon_service import CouponService
from app.services.member_service import MemberService


class OperationStrategyService:
    """运营策略服务"""

    def __init__(self, db: Session):
        self.db = db
        self.member_service = MemberService(db)
        try:
            self.coupon_service = CouponService(db)
        except:
            self.coupon_service = None

    # 新用户激励
    def init_new_user_rewards(self, user_id: int) -> NewUserReward:
        """初始化新用户奖励"""
        # 检查是否已初始化
        existing = (
            self.db.query(NewUserReward)
            .filter(NewUserReward.user_id == user_id)
            .first()
        )

        if existing:
            return existing

        # 创建新用户奖励记录
        reward = NewUserReward(
            user_id=user_id, register_points=100, first_order_discount=30, status=0
        )

        self.db.add(reward)
        self.db.commit()
        self.db.refresh(reward)

        return reward

    def claim_new_user_rewards(self, user_id: int) -> tuple[bool, str, Dict]:
        """领取新用户奖励"""
        reward = (
            self.db.query(NewUserReward)
            .filter(NewUserReward.user_id == user_id)
            .first()
        )

        if not reward:
            reward = self.init_new_user_rewards(user_id)

        if reward.status == 1:
            return False, "奖励已领取", {}

        rewards_detail = {}

        # 发放注册积分
        if reward.register_points > 0:
            self.member_service.add_points(
                user_id=user_id, points=reward.register_points, reason="新用户注册奖励"
            )
            rewards_detail["points"] = reward.register_points

        # 发放新人优惠券（8折）
        if self.coupon_service:
            try:
                # 创建新人专享优惠券
                coupon = self.coupon_service.create_coupon(
                    name="新人专享8折优惠券",
                    coupon_type="discount",
                    discount_value=Decimal("20"),  # 8折 = 20%折扣
                    start_at=datetime.now(),
                    expire_at=datetime.now() + timedelta(days=30),
                    total_count=1,
                    min_amount=Decimal("50"),
                )

                # 自动领取
                success, msg, user_coupon = self.coupon_service.claim_coupon(
                    user_id, coupon.code
                )
                if success:
                    reward.welcome_coupon_id = user_coupon.id
                    rewards_detail["coupon"] = coupon.code
            except:
                pass

        # 首单折扣标记
        rewards_detail["first_order_discount"] = reward.first_order_discount

        reward.status = 1
        reward.claimed_at = datetime.now()
        self.db.commit()

        return True, "奖励领取成功", rewards_detail

    # 签到系统
    def sign_in(self, user_id: int) -> tuple[bool, str, Dict]:
        """用户签到"""
        today = date.today()

        # 检查今天是否已签到
        existing = (
            self.db.query(UserSignIn)
            .filter(UserSignIn.user_id == user_id, UserSignIn.sign_date == today)
            .first()
        )

        if existing:
            return False, "今天已签到", {}

        # 获取昨天的签到记录
        yesterday = today - timedelta(days=1)
        yesterday_sign = (
            self.db.query(UserSignIn)
            .filter(UserSignIn.user_id == user_id, UserSignIn.sign_date == yesterday)
            .first()
        )

        # 计算连续签到天数
        if yesterday_sign:
            continuous_days = yesterday_sign.continuous_days + 1
        else:
            continuous_days = 1

        # 计算奖励积分（连续签到递增）
        reward_points = self._calculate_sign_in_points(continuous_days)

        # 创建签到记录
        sign_in = UserSignIn(
            user_id=user_id,
            sign_date=today,
            continuous_days=continuous_days,
            reward_points=reward_points,
        )

        self.db.add(sign_in)

        # 发放积分
        self.member_service.add_points(
            user_id=user_id,
            points=reward_points,
            reason=f"每日签到（连续{continuous_days}天）",
        )

        # 连续签到7天额外奖励
        extra_reward = {}
        if continuous_days == 7:
            # 赠送会员体验（3天银卡会员）
            extra_reward = {"type": "member_trial", "days": 3, "level": "silver"}
            # 这里可以实际发放会员体验

        self.db.commit()

        return (
            True,
            "签到成功",
            {
                "points": reward_points,
                "continuous_days": continuous_days,
                "extra_reward": extra_reward,
            },
        )

    def _calculate_sign_in_points(self, continuous_days: int) -> int:
        """计算签到积分"""
        base_points = 5

        if continuous_days <= 3:
            return base_points
        elif continuous_days <= 6:
            return base_points + 5
        elif continuous_days == 7:
            return base_points + 20  # 第7天额外奖励
        else:
            # 7天后重新开始循环
            return base_points + ((continuous_days - 1) % 7) * 2

    def get_sign_in_status(self, user_id: int) -> Dict:
        """获取签到状态"""
        today = date.today()

        # 今天是否已签到
        today_sign = (
            self.db.query(UserSignIn)
            .filter(UserSignIn.user_id == user_id, UserSignIn.sign_date == today)
            .first()
        )

        # 获取最近的签到记录
        latest_sign = (
            self.db.query(UserSignIn)
            .filter(UserSignIn.user_id == user_id)
            .order_by(UserSignIn.sign_date.desc())
            .first()
        )

        continuous_days = latest_sign.continuous_days if latest_sign else 0

        # 如果最近签到不是昨天，连续天数归零
        if latest_sign and latest_sign.sign_date < today - timedelta(days=1):
            continuous_days = 0

        return {
            "signed_today": today_sign is not None,
            "continuous_days": continuous_days,
            "next_reward_points": self._calculate_sign_in_points(continuous_days + 1),
        }

    # 邀请奖励
    def process_invite_reward(
        self, inviter_id: int, invitee_id: int
    ) -> tuple[bool, str]:
        """处理邀请奖励"""
        # 检查是否已处理
        existing = (
            self.db.query(InviteReward)
            .filter(
                InviteReward.inviter_id == inviter_id,
                InviteReward.invitee_id == invitee_id,
            )
            .first()
        )

        if existing:
            return False, "邀请奖励已发放"

        # 创建邀请奖励记录
        reward = InviteReward(
            inviter_id=inviter_id,
            invitee_id=invitee_id,
            inviter_reward_points=50,
            invitee_reward_points=50,
        )

        self.db.add(reward)

        # 发放邀请人奖励
        self.member_service.add_points(
            user_id=inviter_id,
            points=50,
            reason="邀请好友奖励",
            related_type="invite",
            related_id=invitee_id,
        )
        reward.inviter_reward_status = 1

        # 发放被邀请人奖励
        self.member_service.add_points(
            user_id=invitee_id,
            points=50,
            reason="接受邀请奖励",
            related_type="invite",
            related_id=inviter_id,
        )
        reward.invitee_reward_status = 1

        self.db.commit()

        return True, "邀请奖励发放成功"

    # 内容分享奖励
    def record_content_share(
        self, user_id: int, work_id: int, platform: str
    ) -> tuple[bool, str, int]:
        """记录内容分享"""
        # 检查今天是否已分享过该作品
        today = date.today()
        existing = (
            self.db.query(ContentShareReward)
            .filter(
                ContentShareReward.user_id == user_id,
                ContentShareReward.work_id == work_id,
                ContentShareReward.created_at
                >= datetime.combine(today, datetime.min.time()),
            )
            .first()
        )

        if existing:
            return False, "今天已分享过该作品", 0

        # 创建分享记录
        reward_points = 10
        share_reward = ContentShareReward(
            user_id=user_id,
            work_id=work_id,
            share_platform=platform,
            reward_points=reward_points,
        )

        self.db.add(share_reward)

        # 发放积分
        self.member_service.add_points(
            user_id=user_id,
            points=reward_points,
            reason=f"分享作品到{platform}",
            related_type="share",
            related_id=work_id,
        )

        self.db.commit()

        return True, "分享成功，获得积分奖励", reward_points

    # 优质内容激励
    def reward_quality_content(
        self, user_id: int, work_id: int, quality_score: int
    ) -> tuple[bool, str, Dict]:
        """优质内容激励"""
        # 检查是否已奖励
        existing = (
            self.db.query(QualityContentReward)
            .filter(QualityContentReward.work_id == work_id)
            .first()
        )

        if existing:
            return False, "该作品已获得奖励", {}

        rewards = {}

        # 根据质量评分给予不同奖励
        if quality_score >= 90:
            # 优秀作品：积分 + 优惠券
            points = 100
            rewards = {"points": points, "coupon": "优质内容创作者专享券"}
            reward_type = "points+coupon"
            reward_value = f"{points}积分+优惠券"
        elif quality_score >= 80:
            # 良好作品：积分
            points = 50
            rewards = {"points": points}
            reward_type = "points"
            reward_value = f"{points}积分"
        else:
            return False, "作品质量未达到奖励标准", {}

        # 创建奖励记录
        quality_reward = QualityContentReward(
            user_id=user_id,
            work_id=work_id,
            quality_score=quality_score,
            reward_type=reward_type,
            reward_value=reward_value,
            status=1,
        )

        self.db.add(quality_reward)

        # 发放积分
        if "points" in rewards:
            self.member_service.add_points(
                user_id=user_id,
                points=rewards["points"],
                reason="优质内容创作奖励",
                related_type="quality_work",
                related_id=work_id,
            )

        self.db.commit()

        return True, "优质内容奖励发放成功", rewards

    # 用户分层
    def update_user_segment(
        self, user_id: int, segment_type: str, segment_value: str, score: int = None
    ):
        """更新用户分层标签"""
        # 查找现有标签
        segment = (
            self.db.query(UserSegment)
            .filter(
                UserSegment.user_id == user_id, UserSegment.segment_type == segment_type
            )
            .first()
        )

        if segment:
            segment.segment_value = segment_value
            segment.score = score
            segment.updated_at = datetime.now()
        else:
            segment = UserSegment(
                user_id=user_id,
                segment_type=segment_type,
                segment_value=segment_value,
                score=score,
                updated_at=datetime.now(),
            )
            self.db.add(segment)

        self.db.commit()

    def get_user_segments(self, user_id: int) -> List[UserSegment]:
        """获取用户分层标签"""
        return self.db.query(UserSegment).filter(UserSegment.user_id == user_id).all()
