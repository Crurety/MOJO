"""内容创作API测试"""

import pytest
from decimal import Decimal


class TestContentAPI:
    """内容创作API测试"""

    def test_create_script(self, client, auth_headers, db):
        """测试创建脚本"""
        # 先授予权限
        from app.services.permission_service import PermissionService
        from app.models import User

        user = db.query(User).filter(User.email == "test@example.com").first()
        permission_service = PermissionService(db)
        permission_service.grant_permission(user.id, "script", "per_use", count=10)

        response = client.post(
            "/api/v1/content/scripts",
            json={
                "title": "测试脚本",
                "keywords": "科技,未来",
                "output_type": "video",
                "style": "现代",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "script_id" in data["data"]

    def test_create_script_without_permission(self, client, auth_headers):
        """测试无权限创建脚本"""
        response = client.post(
            "/api/v1/content/scripts",
            json={"title": "测试脚本", "keywords": "科技", "output_type": "video"},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_get_my_scripts(self, client, auth_headers):
        """测试获取我的脚本"""
        response = client.get("/api/v1/content/scripts", headers=auth_headers)

        assert response.status_code == 200

    def test_create_image_task(self, client, auth_headers, db):
        """测试创建图片生成任务"""
        from app.services.permission_service import PermissionService
        from app.models import User

        user = db.query(User).filter(User.email == "test@example.com").first()
        permission_service = PermissionService(db)
        permission_service.grant_permission(user.id, "image", "per_use", count=10)

        response = client.post(
            "/api/v1/content/tasks/image",
            json={"prompt": "一只可爱的猫", "clarity": "1080p", "count": 1},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "task_id" in data["data"]

    def test_create_video_task(self, client, auth_headers, db):
        """测试创建视频生成任务"""
        from app.services.permission_service import PermissionService
        from app.models import User

        user = db.query(User).filter(User.email == "test@example.com").first()
        permission_service = PermissionService(db)
        permission_service.grant_permission(user.id, "video", "per_use", count=10)

        response = client.post(
            "/api/v1/content/tasks/video",
            json={"prompt": "城市夜景延时摄影", "duration": 5, "clarity": "1080p"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_get_my_tasks(self, client, auth_headers):
        """测试获取我的任务"""
        response = client.get("/api/v1/content/tasks", headers=auth_headers)

        assert response.status_code == 200

    def test_get_task_detail(self, client, auth_headers, db):
        """测试获取任务详情"""
        from app.models import Task, User

        user = db.query(User).filter(User.email == "test@example.com").first()

        # 创建测试任务
        task = Task(
            user_id=user.id, task_no="TEST123", task_type="image", status=0, progress=0
        )
        db.add(task)
        db.commit()

        response = client.get(f"/api/v1/content/tasks/{task.id}", headers=auth_headers)

        assert response.status_code == 200

    def test_get_my_works(self, client, auth_headers):
        """测试获取我的作品"""
        response = client.get("/api/v1/content/works", headers=auth_headers)

        assert response.status_code == 200

    def test_delete_work(self, client, auth_headers, db):
        """测试删除作品"""
        from app.models import Work, User

        user = db.query(User).filter(User.email == "test@example.com").first()

        # 创建测试作品
        work = Work(
            user_id=user.id, work_type="image", file_url="http://example.com/test.jpg"
        )
        db.add(work)
        db.commit()

        response = client.delete(
            f"/api/v1/content/works/{work.id}",
            headers=auth_headers
        )

        assert response.status_code == 200

    def test_get_gallery(self, client):
        """测试获取公共作品画廊"""
        response = client.get("/api/v1/content/gallery")

        assert response.status_code == 200
