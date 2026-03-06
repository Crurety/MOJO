"""Celery定时任务配置"""
from celery.schedules import crontab


# Celery Beat定时任务配置
beat_schedule = {
    # 每天凌晨2点清理过期作品
    'cleanup-expired-works': {
        'task': 'app.tasks.cleanup_tasks_optimized.cleanup_expired_works',
        'schedule': crontab(hour=2, minute=0),
        'options': {'queue': 'cleanup'}
    },

    # 每天凌晨3点清理过期任务
    'cleanup-expired-tasks': {
        'task': 'app.tasks.cleanup_tasks_optimized.cleanup_expired_tasks',
        'schedule': crontab(hour=3, minute=0),
        'options': {'queue': 'cleanup'}
    },

    # 每天凌晨4点清理过期权限
    'cleanup-expired-permissions': {
        'task': 'app.tasks.cleanup_tasks_optimized.cleanup_expired_permissions',
        'schedule': crontab(hour=4, minute=0),
        'options': {'queue': 'cleanup'}
    },

    # 每天凌晨5点标记过期优惠券
    'cleanup-expired-coupons': {
        'task': 'app.tasks.cleanup_tasks_optimized.cleanup_expired_coupons',
        'schedule': crontab(hour=5, minute=0),
        'options': {'queue': 'cleanup'}
    },

    # 每周日凌晨1点清理旧日志
    'cleanup-old-logs': {
        'task': 'app.tasks.cleanup_tasks_optimized.cleanup_old_logs',
        'schedule': crontab(hour=1, minute=0, day_of_week=0),
        'options': {'queue': 'cleanup'}
    },

    # 每周日凌晨6点清理孤立文件
    'cleanup-orphan-files': {
        'task': 'app.tasks.file_tasks.cleanup_orphan_files',
        'schedule': crontab(hour=6, minute=0, day_of_week=0),
        'options': {'queue': 'cleanup'}
    },

    # 每小时检查视频生成状态
    'check-video-status': {
        'task': 'app.tasks.content_tasks.check_video_status',
        'schedule': crontab(minute='*/30'),  # 每30分钟
        'options': {'queue': 'default'}
    },
}


# Celery配置
celery_config = {
    'broker_url': 'redis://localhost:6379/0',
    'result_backend': 'redis://localhost:6379/0',
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'timezone': 'Asia/Shanghai',
    'enable_utc': True,
    'task_track_started': True,
    'task_time_limit': 3600,  # 任务最大执行时间1小时
    'task_soft_time_limit': 3000,  # 软超时50分钟
    'worker_prefetch_multiplier': 4,
    'worker_max_tasks_per_child': 1000,
    'beat_schedule': beat_schedule,
    'task_routes': {
        'app.tasks.cleanup_tasks_optimized.*': {'queue': 'cleanup'},
        'app.tasks.file_tasks.*': {'queue': 'cleanup'},
        'app.tasks.content_tasks.*': {'queue': 'default'},
        'app.tasks.notification_tasks.*': {'queue': 'notification'},
    },
    'task_default_queue': 'default',
    'task_default_exchange': 'default',
    'task_default_routing_key': 'default',
}
