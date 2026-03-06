"""消息通知服务"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import Message, User
from datetime import datetime


class NotificationService:
    """消息通知服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_message(
        self,
        user_id: int,
        title: str,
        content: str,
        message_type: str = "system",
        link: Optional[str] = None
    ) -> Message:
        """创建消息

        Args:
            user_id: 用户ID
            title: 消息标题
            content: 消息内容
            message_type: 消息类型 (system/task/promotion)
            link: 相关链接

        Returns:
            Message: 创建的消息对象
        """
        message = Message(
            user_id=user_id,
            title=title,
            content=content,
            message_type=message_type,
            link=link,
            is_read=0
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def get_user_messages(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        is_read: Optional[int] = None,
        message_type: Optional[str] = None
    ) -> List[Message]:
        """获取用户消息列表

        Args:
            user_id: 用户ID
            skip: 跳过数量
            limit: 返回数量
            is_read: 是否已读 (0未读/1已读)
            message_type: 消息类型

        Returns:
            List[Message]: 消息列表
        """
        query = self.db.query(Message).filter(Message.user_id == user_id)

        if is_read is not None:
            query = query.filter(Message.is_read == is_read)

        if message_type:
            query = query.filter(Message.message_type == message_type)

        return query.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()

    def get_unread_count(self, user_id: int) -> int:
        """获取未读消息数量

        Args:
            user_id: 用户ID

        Returns:
            int: 未读消息数量
        """
        return self.db.query(Message).filter(
            Message.user_id == user_id,
            Message.is_read == 0
        ).count()

    def mark_as_read(self, message_id: int, user_id: int) -> bool:
        """标记消息为已读

        Args:
            message_id: 消息ID
            user_id: 用户ID

        Returns:
            bool: 是否成功
        """
        message = self.db.query(Message).filter(
            Message.id == message_id,
            Message.user_id == user_id
        ).first()

        if not message:
            return False

        message.is_read = 1
        self.db.commit()

        return True

    def mark_all_as_read(self, user_id: int) -> int:
        """标记所有消息为已读

        Args:
            user_id: 用户ID

        Returns:
            int: 标记数量
        """
        count = self.db.query(Message).filter(
            Message.user_id == user_id,
            Message.is_read == 0
        ).update({"is_read": 1})

        self.db.commit()

        return count

    def delete_message(self, message_id: int, user_id: int) -> bool:
        """删除消息

        Args:
            message_id: 消息ID
            user_id: 用户ID

        Returns:
            bool: 是否成功
        """
        message = self.db.query(Message).filter(
            Message.id == message_id,
            Message.user_id == user_id
        ).first()

        if not message:
            return False

        self.db.delete(message)
        self.db.commit()

        return True

    # 便捷方法：发送任务完成通知
    def notify_task_completed(
        self,
        user_id: int,
        task_no: str,
        task_type: str,
        result_url: Optional[str] = None
    ) -> Message:
        """发送任务完成通知

        Args:
            user_id: 用户ID
            task_no: 任务编号
            task_type: 任务类型
            result_url: 结果URL

        Returns:
            Message: 创建的消息对象
        """
        task_type_names = {
            "script": "脚本生成",
            "image": "图片生成",
            "video": "视频生成",
            "ad": "广告设计"
        }

        type_name = task_type_names.get(task_type, "任务")

        return self.create_message(
            user_id=user_id,
            title=f"{type_name}任务已完成",
            content=f"您的{type_name}任务（{task_no}）已完成，请查看结果。",
            message_type="task",
            link=f"/tasks/{task_no}"
        )

    # 便捷方法：发送任务失败通知
    def notify_task_failed(
        self,
        user_id: int,
        task_no: str,
        task_type: str,
        error_message: str
    ) -> Message:
        """发送任务失败通知

        Args:
            user_id: 用户ID
            task_no: 任务编号
            task_type: 任务类型
            error_message: 错误信息

        Returns:
            Message: 创建的消息对象
        """
        task_type_names = {
            "script": "脚本生成",
            "image": "图片生成",
            "video": "视频生成",
            "ad": "广告设计"
        }

        type_name = task_type_names.get(task_type, "任务")

        return self.create_message(
            user_id=user_id,
            title=f"{type_name}任务失败",
            content=f"您的{type_name}任务（{task_no}）处理失败：{error_message}",
            message_type="task",
            link=f"/tasks/{task_no}"
        )

    # 便捷方法：发送系统公告
    def broadcast_system_announcement(
        self,
        title: str,
        content: str,
        link: Optional[str] = None
    ) -> int:
        """广播系统公告给所有用户

        Args:
            title: 公告标题
            content: 公告内容
            link: 相关链接

        Returns:
            int: 发送数量
        """
        users = self.db.query(User).filter(User.status == 1).all()

        count = 0
        for user in users:
            self.create_message(
                user_id=user.id,
                title=title,
                content=content,
                message_type="system",
                link=link
            )
            count += 1

        return count

    # 便捷方法：发送促销通知
    def notify_promotion(
        self,
        user_id: int,
        title: str,
        content: str,
        link: Optional[str] = None
    ) -> Message:
        """发送促销通知

        Args:
            user_id: 用户ID
            title: 通知标题
            content: 通知内容
            link: 相关链接

        Returns:
            Message: 创建的消息对象
        """
        return self.create_message(
            user_id=user_id,
            title=title,
            content=content,
            message_type="promotion",
            link=link
        )
