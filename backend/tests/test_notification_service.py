"""通知服务单元测试"""
import pytest
from app.services.notification_service import NotificationService
from app.models import Message


class TestNotificationService:

    def test_create_message(self, db, test_user):
        svc = NotificationService(db)
        msg = svc.create_message(
            user_id=test_user.id,
            title="测试标题",
            content="测试内容",
            message_type="system",
        )
        assert msg.id is not None
        assert msg.is_read == 0

    def test_get_user_messages(self, db, test_user, multiple_messages):
        svc = NotificationService(db)
        msgs = svc.get_user_messages(test_user.id)
        assert len(msgs) == 5

    def test_get_user_messages_unread(self, db, test_user, multiple_messages):
        svc = NotificationService(db)
        msgs = svc.get_user_messages(test_user.id, is_read=0)
        assert len(msgs) == 3

    def test_get_user_messages_by_type(self, db, test_user, multiple_messages):
        svc = NotificationService(db)
        system_msgs = svc.get_user_messages(test_user.id, message_type="system")
        assert all(m.message_type == "system" for m in system_msgs)

    def test_get_unread_count(self, db, test_user, multiple_messages):
        svc = NotificationService(db)
        count = svc.get_unread_count(test_user.id)
        assert count == 3

    def test_mark_as_read(self, db, test_user, test_message):
        svc = NotificationService(db)
        result = svc.mark_as_read(test_message.id, test_user.id)
        assert result is True

        db.refresh(test_message)
        assert test_message.is_read == 1

    def test_mark_as_read_wrong_user(self, db, test_user, test_user2, test_message):
        svc = NotificationService(db)
        result = svc.mark_as_read(test_message.id, test_user2.id)
        assert result is False

    def test_mark_all_as_read(self, db, test_user, multiple_messages):
        svc = NotificationService(db)
        count = svc.mark_all_as_read(test_user.id)
        assert count == 3

        # 再查未读应该为0
        unread = svc.get_unread_count(test_user.id)
        assert unread == 0

    def test_delete_message(self, db, test_user, test_message):
        svc = NotificationService(db)
        result = svc.delete_message(test_message.id, test_user.id)
        assert result is True

        # 确认已删除
        found = db.query(Message).filter(Message.id == test_message.id).first()
        assert found is None

    def test_notify_task_completed(self, db, test_user):
        svc = NotificationService(db)
        msg = svc.notify_task_completed(
            user_id=test_user.id,
            task_no="T001",
            task_type="image",
            result_url="https://example.com/result.png",
        )
        assert "图片生成" in msg.title
        assert msg.message_type == "task"

    def test_notify_task_failed(self, db, test_user):
        svc = NotificationService(db)
        msg = svc.notify_task_failed(
            user_id=test_user.id,
            task_no="T002",
            task_type="video",
            error_message="GPU内存不足",
        )
        assert "失败" in msg.title
        assert "GPU" in msg.content

    def test_pagination(self, db, test_user):
        svc = NotificationService(db)
        for i in range(25):
            svc.create_message(test_user.id, f"消息{i}", f"内容{i}", "system")

        page1 = svc.get_user_messages(test_user.id, skip=0, limit=10)
        page2 = svc.get_user_messages(test_user.id, skip=10, limit=10)
        page3 = svc.get_user_messages(test_user.id, skip=20, limit=10)

        assert len(page1) == 10
        assert len(page2) == 10
        assert len(page3) == 5
