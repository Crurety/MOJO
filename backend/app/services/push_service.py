"""推送通知服务"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import User
from app.models.advanced_operation import PushNotification, PushNotificationLog
from app.services.notification_service import NotificationService


class PushService:
    """推送通知服务"""

    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)

    def create_push(
        self,
        notification_type: str,
        target_type: str,
        title: str,
        content: str,
        target_value: Dict = None,
        link: str = None,
        image_url: str = None,
        send_at: datetime = None,
    ) -> PushNotification:
        """创建推送通知

        Args:
            notification_type: 通知类型 (site/email/sms/app)
            target_type: 目标类型 (all/segment/user)
            title: 通知标题
            content: 通知内容
            target_value: 目标值 (用户ID列表或分层条件)
            link: 跳转链接
            image_url: 图片URL
            send_at: 定时发送时间
        """
        push = PushNotification(
            notification_type=notification_type,
            target_type=target_type,
            target_value=json.dumps(target_value) if target_value else None,
            title=title,
            content=content,
            link=link,
            image_url=image_url,
            send_at=send_at,
            status=0 if send_at else 1,
        )

        self.db.add(push)
        self.db.commit()
        self.db.refresh(push)

        # 如果不是定时发送，立即发送
        if not send_at:
            self.send_push(push.id)

        return push

    def get_target_users(self, push: PushNotification) -> List[int]:
        """获取目标用户列表"""
        if push.target_type == "all":
            # 所有活跃用户
            users = self.db.query(User.id).filter(User.status == 1).all()
            return [u.id for u in users]

        elif push.target_type == "user":
            # 指定用户
            target_value = json.loads(push.target_value) if push.target_value else {}
            return target_value.get("user_ids", [])

        elif push.target_type == "segment":
            # 用户分层
            target_value = json.loads(push.target_value) if push.target_value else {}
            segment_type = target_value.get("segment_type")
            segment_value = target_value.get("segment_value")

            if segment_type and segment_value:
                from app.models.operation import UserSegment

                segments = (
                    self.db.query(UserSegment)
                    .filter(
                        UserSegment.segment_type == segment_type,
                        UserSegment.segment_value == segment_value,
                    )
                    .all()
                )
                return [s.user_id for s in segments]

        return []

    def send_push(self, push_id: int):
        """发送推送通知"""
        push = (
            self.db.query(PushNotification)
            .filter(PushNotification.id == push_id)
            .first()
        )

        if not push or push.status == 2:
            return

        # 更新状态为发送中
        push.status = 1
        self.db.commit()

        # 获取目标用户
        user_ids = self.get_target_users(push)
        push.total_count = len(user_ids)

        success_count = 0
        failed_count = 0

        # 发送通知
        for user_id in user_ids:
            try:
                if push.notification_type == "site":
                    # 站内信
                    self.notification_service.create_message(
                        user_id=user_id,
                        title=push.title,
                        content=push.content,
                        message_type="system",
                        link=push.link,
                    )
                    status = 1
                    error_message = None

                elif push.notification_type == "email":
                    # 邮件推送（需要实现邮件发送）
                    status = 1
                    error_message = None

                elif push.notification_type == "sms":
                    # 短信推送（需要实现短信发送）
                    status = 1
                    error_message = None

                elif push.notification_type == "app":
                    # APP推送（需要实现APP推送）
                    status = 1
                    error_message = None

                else:
                    status = 0
                    error_message = "不支持的通知类型"

                # 记录日志
                log = PushNotificationLog(
                    notification_id=push.id,
                    user_id=user_id,
                    status=status,
                    error_message=error_message,
                )
                self.db.add(log)

                if status == 1:
                    success_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                # 记录失败日志
                log = PushNotificationLog(
                    notification_id=push.id,
                    user_id=user_id,
                    status=0,
                    error_message=str(e),
                )
                self.db.add(log)
                failed_count += 1

        # 更新统计
        push.success_count = success_count
        push.failed_count = failed_count
        push.status = 2

        self.db.commit()

    def record_click(self, push_id: int, user_id: int):
        """记录点击"""
        log = (
            self.db.query(PushNotificationLog)
            .filter(
                PushNotificationLog.notification_id == push_id,
                PushNotificationLog.user_id == user_id,
            )
            .first()
        )

        if log and log.clicked == 0:
            log.clicked = 1
            log.clicked_at = datetime.now()

            # 更新推送的点击统计
            push = (
                self.db.query(PushNotification)
                .filter(PushNotification.id == push_id)
                .first()
            )

            if push:
                push.click_count += 1

            self.db.commit()

    def get_push_statistics(self, push_id: int) -> Dict:
        """获取推送统计"""
        push = (
            self.db.query(PushNotification)
            .filter(PushNotification.id == push_id)
            .first()
        )

        if not push:
            return {}

        return {
            "title": push.title,
            "notification_type": push.notification_type,
            "target_type": push.target_type,
            "total_count": push.total_count,
            "success_count": push.success_count,
            "failed_count": push.failed_count,
            "click_count": push.click_count,
            "success_rate": round(
                (push.success_count / push.total_count * 100)
                if push.total_count
                else 0,
                2,
            ),
            "click_rate": round(
                (push.click_count / push.success_count * 100)
                if push.success_count
                else 0,
                2,
            ),
            "status": push.status,
            "created_at": push.created_at,
        }

    def get_pending_pushes(self) -> List[PushNotification]:
        """获取待发送的定时推送"""
        now = datetime.now()
        return (
            self.db.query(PushNotification)
            .filter(PushNotification.status == 0, PushNotification.send_at <= now)
            .all()
        )

    def cancel_push(self, push_id: int) -> bool:
        """取消推送"""
        push = (
            self.db.query(PushNotification)
            .filter(PushNotification.id == push_id)
            .first()
        )

        if push and push.status == 0:
            push.status = 3
            self.db.commit()
            return True

        return False
