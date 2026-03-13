"""Content API tests."""

import pytest


class TestContentAPI:
    """Content creation API tests."""

    def test_create_script(self, client, auth_headers, db, monkeypatch):
        from app.api.v1 import content as content_api
        from app.models import User
        from app.services.permission_service import PermissionService

        async def fake_generate_from_keywords(**kwargs):
            return {"script": "Generated storyboard for a futuristic campaign."}

        monkeypatch.setattr(content_api.script_generator, "generate_from_keywords", fake_generate_from_keywords)

        user = db.query(User).filter(User.email == "test@example.com").first()
        PermissionService(db).grant_permission(user.id, "script", "per_use", count=10)

        response = client.post(
            "/api/v1/content/scripts",
            json={
                "title": "Test Script",
                "keywords": "technology,future",
                "output_type": "video",
                "parameters": {"style": "modern", "scene_count": 3},
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["script"]["content"] == "Generated storyboard for a futuristic campaign."
        assert "script_id" in data["data"]

    def test_create_script_without_permission(self, client, auth_headers):
        response = client.post(
            "/api/v1/content/scripts",
            json={"title": "Test Script", "keywords": "technology", "output_type": "video"},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_create_script_generation_failure(self, client, auth_headers, db, monkeypatch):
        from app.api.v1 import content as content_api
        from app.models import User
        from app.services.permission_service import PermissionService

        async def fake_generate_from_keywords(**kwargs):
            raise RuntimeError("provider unavailable")

        monkeypatch.setattr(content_api.script_generator, "generate_from_keywords", fake_generate_from_keywords)

        user = db.query(User).filter(User.email == "test@example.com").first()
        PermissionService(db).grant_permission(user.id, "script", "per_use", count=10)

        response = client.post(
            "/api/v1/content/scripts",
            json={
                "title": "Test Script",
                "keywords": "technology",
                "output_type": "video",
                "parameters": {"style": "modern"},
            },
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert response.json()["message"] == "Script generation failed. Check AI configuration and try again."

    def test_get_my_scripts(self, client, auth_headers):
        response = client.get("/api/v1/content/scripts", headers=auth_headers)
        assert response.status_code == 200

    def test_create_image_task(self, client, auth_headers, db, monkeypatch):
        from app.api.v1 import content as content_api
        from app.models import User
        from app.services.permission_service import PermissionService

        monkeypatch.setattr(content_api.process_content_task, "delay", lambda task_id: None)

        user = db.query(User).filter(User.email == "test@example.com").first()
        PermissionService(db).grant_permission(user.id, "image", "per_use", count=10)

        response = client.post(
            "/api/v1/content/tasks/image",
            json={"prompt": "a cute cat", "clarity": "1080p", "count": 1},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "task_id" in data["data"]

    def test_create_image_task_dispatch_failure_rolls_back(self, client, auth_headers, db, monkeypatch):
        from app.api.v1 import content as content_api
        from app.models import Task, User
        from app.services.permission_service import PermissionService

        def fail_dispatch(task_id):
            raise RuntimeError("broker unavailable")

        monkeypatch.setattr(content_api.process_content_task, "delay", fail_dispatch)

        user = db.query(User).filter(User.email == "test@example.com").first()
        permission_service = PermissionService(db)
        permission = permission_service.grant_permission(user.id, "image", "per_use", count=10)

        response = client.post(
            "/api/v1/content/tasks/image",
            json={"prompt": "a cute cat", "clarity": "1080p", "count": 1},
            headers=auth_headers,
        )

        db.refresh(permission)
        remaining_tasks = db.query(Task).filter(Task.user_id == user.id, Task.task_type == "image").all()

        assert response.status_code == 400
        assert response.json()["message"] == "Task submission failed. Please try again later."
        assert permission.used_count == 0
        assert remaining_tasks == []

    def test_create_image_task_rejects_when_cost_exceeds_remaining_quota(self, client, auth_headers, db, monkeypatch):
        from app.api.v1 import content as content_api
        from app.models import User
        from app.services.permission_service import PermissionService

        monkeypatch.setattr(content_api.process_content_task, "delay", lambda task_id: None)

        user = db.query(User).filter(User.email == "test@example.com").first()
        PermissionService(db).grant_permission(user.id, "image", "per_use", count=4)

        response = client.post(
            "/api/v1/content/tasks/image",
            json={"prompt": "a cute cat", "clarity": "1080p", "count": 1},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "Insufficient usage count" in response.json()["message"]

    def test_create_ad_task(self, client, auth_headers, db, monkeypatch):
        from app.api.v1 import content as content_api
        from app.models import User
        from app.services.permission_service import PermissionService

        monkeypatch.setattr(content_api.process_content_task, "delay", lambda task_id: None)

        user = db.query(User).filter(User.email == "test@example.com").first()
        PermissionService(db).grant_permission(user.id, "ad", "per_use", count=10)

        response = client.post(
            "/api/v1/content/tasks",
            json={
                "task_type": "ad",
                "parameters": {
                    "ad_type": "image",
                    "product_info": "Sparkling water",
                    "target_audience": "Young professionals",
                    "clarity": "1080p",
                },
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["code"] == 0

    def test_create_ad_task_dispatch_failure_rolls_back(self, client, auth_headers, db, monkeypatch):
        from app.api.v1 import content as content_api
        from app.models import Task, User
        from app.services.permission_service import PermissionService

        def fail_dispatch(task_id):
            raise RuntimeError("broker unavailable")

        monkeypatch.setattr(content_api.process_content_task, "delay", fail_dispatch)

        user = db.query(User).filter(User.email == "test@example.com").first()
        permission = PermissionService(db).grant_permission(user.id, "ad", "per_use", count=10)

        response = client.post(
            "/api/v1/content/tasks",
            json={
                "task_type": "ad",
                "parameters": {
                    "ad_type": "image",
                    "product_info": "Sparkling water",
                    "target_audience": "Young professionals",
                    "clarity": "1080p",
                },
            },
            headers=auth_headers,
        )

        db.refresh(permission)
        remaining_tasks = db.query(Task).filter(Task.user_id == user.id, Task.task_type == "ad").all()

        assert response.status_code == 400
        assert response.json()["message"] == "Task submission failed. Please try again later."
        assert permission.used_count == 0
        assert remaining_tasks == []

    def test_create_video_task(self, client, auth_headers, db, monkeypatch):
        from app.api.v1 import content as content_api
        from app.models import User
        from app.services.permission_service import PermissionService

        monkeypatch.setattr(content_api.process_content_task, "delay", lambda task_id: None)

        user = db.query(User).filter(User.email == "test@example.com").first()
        PermissionService(db).grant_permission(user.id, "video", "per_use", count=10)

        response = client.post(
            "/api/v1/content/tasks/video",
            json={"prompt": "city night timelapse", "duration": 5, "clarity": "1080p"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_create_video_task_dispatch_failure_rolls_back(self, client, auth_headers, db, monkeypatch):
        from app.api.v1 import content as content_api
        from app.models import Task, User
        from app.services.permission_service import PermissionService

        def fail_dispatch(task_id):
            raise RuntimeError("broker unavailable")

        monkeypatch.setattr(content_api.process_content_task, "delay", fail_dispatch)

        user = db.query(User).filter(User.email == "test@example.com").first()
        permission = PermissionService(db).grant_permission(user.id, "video", "per_use", count=10)

        response = client.post(
            "/api/v1/content/tasks/video",
            json={"prompt": "city night timelapse", "duration": 5, "clarity": "1080p"},
            headers=auth_headers,
        )

        db.refresh(permission)
        remaining_tasks = db.query(Task).filter(Task.user_id == user.id, Task.task_type == "video").all()

        assert response.status_code == 400
        assert response.json()["message"] == "Task submission failed. Please try again later."
        assert permission.used_count == 0
        assert remaining_tasks == []

    @pytest.mark.asyncio
    async def test_process_image_task_fails_when_provider_returns_no_images(self, monkeypatch):
        from app.tasks.content_tasks import process_image_task
        from app.models import Task

        async def fake_generate_single(**kwargs):
            return {"images": []}

        monkeypatch.setattr("app.tasks.content_tasks.image_generator.generate_single", fake_generate_single)

        task = Task(task_type="image", parameters={"prompt": "a cat", "clarity": "1080p", "count": 1})

        with pytest.raises(ValueError, match="Image generation returned no images"):
            await process_image_task(task)

    def test_get_my_tasks(self, client, auth_headers):
        response = client.get("/api/v1/content/tasks", headers=auth_headers)
        assert response.status_code == 200

    def test_get_task_detail(self, client, auth_headers, db):
        from app.models import Task, User

        user = db.query(User).filter(User.email == "test@example.com").first()
        task = Task(user_id=user.id, task_no="TEST123", task_type="image", status=0, progress=0)
        db.add(task)
        db.commit()

        response = client.get(f"/api/v1/content/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == 200

    def test_get_my_works(self, client, auth_headers):
        response = client.get("/api/v1/content/works", headers=auth_headers)
        assert response.status_code == 200

    def test_delete_work(self, client, auth_headers, db):
        from app.models import User, Work

        user = db.query(User).filter(User.email == "test@example.com").first()
        work = Work(user_id=user.id, work_type="image", file_url="http://example.com/test.jpg")
        db.add(work)
        db.commit()

        response = client.delete(f"/api/v1/content/works/{work.id}", headers=auth_headers)
        assert response.status_code == 200

    def test_get_gallery(self, client):
        response = client.get("/api/v1/content/gallery")
        assert response.status_code == 200


    def test_get_task_detail_by_task_no(self, client, auth_headers, db):
        from app.models import Task, User

        user = db.query(User).filter(User.email == "test@example.com").first()
        task = Task(user_id=user.id, task_no="TASKNO001", task_type="image", status=0, progress=0)
        db.add(task)
        db.commit()

        response = client.get(f"/api/v1/content/tasks/{task.task_no}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["task_no"] == "TASKNO001"

    def test_get_task_detail_not_found(self, client, auth_headers):
        response = client.get("/api/v1/content/tasks/999999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_work_detail(self, client, auth_headers, test_work):
        response = client.get(f"/api/v1/content/works/{test_work.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == test_work.id

    def test_get_work_detail_not_found(self, client, auth_headers):
        response = client.get("/api/v1/content/works/999999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_gallery_with_work_type_filter(self, client, db, test_work):
        test_work.is_public = 1
        db.commit()

        response = client.get("/api/v1/content/gallery", params={"work_type": "image"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_task_dispatch_failure_rolls_back_generic_task(self, client, auth_headers, db, monkeypatch):
        from app.api.v1 import content as content_api
        from app.models import Task, User
        from app.services.permission_service import PermissionService

        def fail_dispatch(task_id):
            raise RuntimeError("broker unavailable")

        monkeypatch.setattr(content_api.process_content_task, "delay", fail_dispatch)

        user = db.query(User).filter(User.email == "test@example.com").first()
        permission = PermissionService(db).grant_permission(user.id, "image", "per_use", count=10)

        response = client.post(
            "/api/v1/content/tasks",
            json={"task_type": "image", "parameters": {"prompt": "a cat", "clarity": "1080p", "count": 1}},
            headers=auth_headers,
        )

        db.refresh(permission)
        remaining_tasks = db.query(Task).filter(Task.user_id == user.id, Task.task_type == "image").all()

        assert response.status_code == 400
        assert response.json()["message"] == "Task submission failed. Please try again later."
        assert permission.used_count == 0
        assert remaining_tasks == []
