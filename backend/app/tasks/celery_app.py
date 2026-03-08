from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "ai_platform",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.content_tasks", "app.tasks.notification_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

celery_app.conf.beat_schedule = {
    "check-video-status": {
        "task": "app.tasks.content_tasks.check_video_status",
        "schedule": 300.0,
    },
    "cleanup-expired-tasks": {
        "task": "app.tasks.content_tasks.cleanup_expired_tasks",
        "schedule": 3600.0,
    },
    "cleanup-old-works": {
        "task": "app.tasks.content_tasks.cleanup_old_works",
        "schedule": 86400.0,
    },
    "check-expired-permissions": {
        "task": "app.tasks.content_tasks.check_expired_permissions",
        "schedule": 3600.0,
    },
}
