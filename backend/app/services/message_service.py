from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.models import Message


class MessageService:
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        user_id: int,
        title: str,
        content: str,
        message_type: str = "system",
        link: str = None
    ) -> Message:
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
    
    def mark_as_read(self, message_id: int):
        message = self.db.query(Message).filter(Message.id == message_id).first()
        if message:
            message.is_read = 1
            self.db.commit()
    
    def mark_all_as_read(self, user_id: int):
        self.db.query(Message).filter(
            Message.user_id == user_id,
            Message.is_read == 0
        ).update({"is_read": 1})
        self.db.commit()
    
    def get_user_messages(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        is_read: int = None,
        message_type: str = None
    ) -> List[Message]:
        query = self.db.query(Message).filter(Message.user_id == user_id)
        
        if is_read is not None:
            query = query.filter(Message.is_read == is_read)
        if message_type:
            query = query.filter(Message.message_type == message_type)
        
        return query.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_unread_count(self, user_id: int) -> int:
        return self.db.query(Message).filter(
            Message.user_id == user_id,
            Message.is_read == 0
        ).count()
    
    def delete(self, message_id: int, user_id: int) -> bool:
        message = self.db.query(Message).filter(
            Message.id == message_id,
            Message.user_id == user_id
        ).first()
        
        if message:
            self.db.delete(message)
            self.db.commit()
            return True
        return False
    
    def send_task_complete_notification(
        self,
        user_id: int,
        task_no: str,
        task_type: str,
        result_url: str
    ):
        type_names = {
            "script": "脚本生成",
            "image": "图片生成",
            "video": "视频生成",
            "ad": "广告设计"
        }
        
        self.create(
            user_id=user_id,
            title=f"{type_names.get(task_type, '任务')}完成",
            content=f"您的任务 {task_no} 已完成，点击查看结果。",
            message_type="task",
            link=f"/tasks/{task_no}"
        )
    
    def send_task_failed_notification(
        self,
        user_id: int,
        task_no: str,
        task_type: str,
        error_message: str
    ):
        type_names = {
            "script": "脚本生成",
            "image": "图片生成",
            "video": "视频生成",
            "ad": "广告设计"
        }
        
        self.create(
            user_id=user_id,
            title=f"{type_names.get(task_type, '任务')}失败",
            content=f"您的任务 {task_no} 处理失败：{error_message}",
            message_type="task"
        )
