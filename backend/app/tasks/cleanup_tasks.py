"""定时任务 - 数据清理"""
from celery import shared_task
from app.core.database import SessionLocal
from app.models import Work, Task
from datetime import datetime, timedelta
from app.core.logging import logger
from app.utils.storage import storage_service


@shared_task
def cleanup_expired_works():
    """清理过期作品（15天）"""
    db = SessionLocal()
    try:
        # 计算15天前的时间
        expire_date = datetime.now() - timedelta(days=15)

        # 查询过期作品
        expired_works = db.query(Work).filter(
            Work.created_at < expire_date
        ).all()

        count = 0
        for work in expired_works:
            try:
                # 删除存储的文件
                if work.file_url:
                    storage_service.delete_file(work.file_url)
                if work.thumbnail_url:
                    storage_service.delete_file(work.thumbnail_url)

                # 删除数据库记录
                db.delete(work)
                count += 1
            except Exception as e:
                logger.error(f"删除作品失败 work_id={work.id}: {str(e)}")

        db.commit()
        logger.info(f"清理过期作品完成，共清理 {count} 个作品")

        return {"success": True, "count": count}
    except Exception as e:
        db.rollback()
        logger.error(f"清理过期作品失败: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@shared_task
def cleanup_expired_tasks():
    """清理过期任务（30天）"""
    db = SessionLocal()
    try:
        # 计算30天前的时间
        expire_date = datetime.now() - timedelta(days=30)

        # 查询过期任务（已完成或失败的）
        expired_tasks = db.query(Task).filter(
            Task.created_at < expire_date,
            Task.status.in_([2, 3])  # 2=完成, 3=失败
        ).all()

        count = 0
        for task in expired_tasks:
            try:
                # 删除任务记录
                db.delete(task)
                count += 1
            except Exception as e:
                logger.error(f"删除任务失败 task_id={task.id}: {str(e)}")

        db.commit()
        logger.info(f"清理过期任务完成，共清理 {count} 个任务")

        return {"success": True, "count": count}
    except Exception as e:
        db.rollback()
        logger.error(f"清理过期任务失败: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@shared_task
def cleanup_expired_permissions():
    """清理过期权限"""
    db = SessionLocal()
    try:
        from app.models import UserPermission

        # 查询已过期的权限
        now = datetime.now()
        expired_permissions = db.query(UserPermission).filter(
            UserPermission.expire_at < now,
            UserPermission.status == 1
        ).all()

        count = 0
        for permission in expired_permissions:
            try:
                # 标记为无效
                permission.status = 0
                count += 1
            except Exception as e:
                logger.error(f"更新权限状态失败 permission_id={permission.id}: {str(e)}")

        db.commit()
        logger.info(f"清理过期权限完成，共清理 {count} 个权限")

        return {"success": True, "count": count}
    except Exception as e:
        db.rollback()
        logger.error(f"清理过期权限失败: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()
