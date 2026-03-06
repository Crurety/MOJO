"""Operational automation tasks."""

from datetime import date, datetime, timedelta

from celery import shared_task

from app.core.database import SessionLocal
from app.core.logging import logger
from app.models import User, Work
from app.models.operation import InviteReward, QualityContentReward, UserSignIn
from app.services.member_service import MemberService
from app.services.notification_service import NotificationService


@shared_task
def reset_daily_tasks():
    """Placeholder daily reset task."""
    db = SessionLocal()
    try:
        logger.info("Daily tasks reset completed")
        return {"success": True}
    except Exception as exc:
        logger.error("Daily task reset failed: %s", str(exc))
        return {"success": False, "error": str(exc)}
    finally:
        db.close()


@shared_task
def send_sign_in_reminder():
    """Send reminders to users who signed in yesterday but not today."""
    db = SessionLocal()
    try:
        notification_service = NotificationService(db)
        today = date.today()
        yesterday = today - timedelta(days=1)

        yesterday_users = db.query(UserSignIn.user_id).filter(UserSignIn.sign_date == yesterday).all()
        today_users = db.query(UserSignIn.user_id).filter(UserSignIn.sign_date == today).all()

        remind_user_ids = {u.user_id for u in yesterday_users} - {u.user_id for u in today_users}

        count = 0
        for user_id in remind_user_ids:
            notification_service.create_message(
                user_id=user_id,
                title="Sign-in reminder",
                content="You have not signed in today yet.",
                message_type="system",
                link="/sign-in",
            )
            count += 1

        logger.info("Sign-in reminders sent: %s", count)
        return {"success": True, "count": count}
    except Exception as exc:
        logger.error("Sign-in reminder failed: %s", str(exc))
        return {"success": False, "error": str(exc)}
    finally:
        db.close()


@shared_task
def process_invite_rewards():
    """Grant pending invite rewards."""
    db = SessionLocal()
    try:
        member_service = MemberService(db)
        pending_rewards = (
            db.query(InviteReward)
            .filter((InviteReward.inviter_reward_status == 0) | (InviteReward.invitee_reward_status == 0))
            .all()
        )

        count = 0
        for reward in pending_rewards:
            if reward.inviter_reward_status == 0:
                member_service.add_points(
                    user_id=reward.inviter_id,
                    points=reward.inviter_reward_points,
                    reason="Invite reward",
                    related_type="invite",
                    related_id=reward.id,
                )
                reward.inviter_reward_status = 1
                count += 1

            if reward.invitee_reward_status == 0:
                member_service.add_points(
                    user_id=reward.invitee_id,
                    points=reward.invitee_reward_points,
                    reason="Invite reward",
                    related_type="invite",
                    related_id=reward.id,
                )
                reward.invitee_reward_status = 1
                count += 1

        db.commit()
        logger.info("Invite rewards processed: %s", count)
        return {"success": True, "count": count}
    except Exception as exc:
        db.rollback()
        logger.error("Invite reward processing failed: %s", str(exc))
        return {"success": False, "error": str(exc)}
    finally:
        db.close()


@shared_task
def auto_reward_quality_content():
    """Reward high-quality public works created in the last day."""
    db = SessionLocal()
    try:
        from app.services.operation_strategy_service import OperationStrategyService

        strategy_service = OperationStrategyService(db)
        yesterday = datetime.now() - timedelta(days=1)

        quality_works = (
            db.query(Work)
            .filter(Work.created_at >= yesterday, Work.quality_score >= 80, Work.is_public == 1)
            .all()
        )

        count = 0
        for work in quality_works:
            existing = db.query(QualityContentReward).filter(QualityContentReward.work_id == work.id).first()
            if existing:
                continue

            success, _, _ = strategy_service.reward_quality_content(
                user_id=work.user_id,
                work_id=work.id,
                quality_score=work.quality_score,
            )
            if success:
                count += 1

        logger.info("Quality content rewards processed: %s", count)
        return {"success": True, "count": count}
    except Exception as exc:
        logger.error("Quality reward processing failed: %s", str(exc))
        return {"success": False, "error": str(exc)}
    finally:
        db.close()


@shared_task
def update_user_segments():
    """Refresh user segmentation labels."""
    db = SessionLocal()
    try:
        from app.services.operation_strategy_service import OperationStrategyService

        strategy_service = OperationStrategyService(db)
        users = db.query(User).filter(User.status == 1).all()

        count = 0
        for user in users:
            strategy_service.update_user_segment(
                user_id=user.id,
                segment_type="rfm",
                segment_value="potential",
                score=50,
            )
            count += 1

        logger.info("User segments updated: %s", count)
        return {"success": True, "count": count}
    except Exception as exc:
        logger.error("User segment update failed: %s", str(exc))
        return {"success": False, "error": str(exc)}
    finally:
        db.close()


@shared_task
def send_monthly_activity_notification():
    """Send notification for active monthly activity."""
    db = SessionLocal()
    try:
        from app.models.operation import MonthlyActivity

        notification_service = NotificationService(db)
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
            return {"success": True, "message": "No active monthly activity"}

        active_users = (
            db.query(User)
            .filter(User.status == 1, User.last_login_at >= now - timedelta(days=7))
            .all()
        )

        count = 0
        for user in active_users:
            notification_service.create_message(
                user_id=user.id,
                title=f"Monthly Activity: {activity.theme}",
                content=(
                    f"{activity.description}\n"
                    f"Discount: {activity.discount_rate}%, "
                    f"Bonus points multiplier: {activity.bonus_points_rate}%."
                ),
                message_type="promotion",
                link="/activities/monthly",
            )
            count += 1

        logger.info("Monthly activity notifications sent: %s", count)
        return {"success": True, "count": count}
    except Exception as exc:
        logger.error("Monthly activity notification failed: %s", str(exc))
        return {"success": False, "error": str(exc)}
    finally:
        db.close()
