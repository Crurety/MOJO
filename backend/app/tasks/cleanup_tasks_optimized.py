"""定时任务 - 数据清理（批量优化版）"""
from celery import shared_task
from app.core.database import SessionLocal
from app.models import Work, Task
from datetime import datetime, timedelta
from app.core.logging import logger
from app.tasks.file_tasks import async_delete_files


@shared_task
def cleanup_expired_works():
    """批量清理过期作品（15天）"""
    db = SessionLocal()
    try:
        expire_date = datetime.now() - timedelta(days=15)

        # 批量查询过期作品
        expired_works = db.query(Work).filter(
            Work.created_at < expire_date
        ).all()

        if not expired_works:
            logger.info("没有需要清理的过期作品")
            return {"success": True, "count": 0}

        # 收集需要删除的文件URL
        file_urls = []
        work_ids = []

        for work in expired_works:
            if work.file_url:
                file_urls.append(work.file_url)
            if work.thumbnail_url:
                file_urls.append(work.thumbnail_url)
            work_ids.append(work.id)

        # 批量删除数据库记录
        db.query(Work).filter(Work.id.in_(work_ids)).delete(synchronize_session=False)
        db.commit()

        # 异步批量删除文件
        if file_urls:
            async_delete_files.delay(file_urls)

        logger.info(f"清理过期作品完成，共清理 {len(expired_works)} 个作品，{len(file_urls)} 个文件")

        return {
            "success": True,
            "count": len(expired_works),
            "files": len(file_urls)
        }

    except Exception as e:
        db.rollback()
        logger.error(f"清理过期作品失败: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@shared_task
def cleanup_expired_tasks():
    """批量清理过期任务（30天）"""
    db = SessionLocal()
    try:
        expire_date = datetime.now() - timedelta(days=30)

        # 批量查询过期任务
        expired_task_ids = db.query(Task.id).filter(
            Task.created_at < expire_date,
            Task.status.in_([2, 3])
        ).all()

        if not expired_task_ids:
            logger.info("没有需要清理的过期任务")
            return {"success": True, "count": 0}

        task_ids = [tid[0] for tid in expired_task_ids]

        # 批量删除
        count = db.query(Task).filter(Task.id.in_(task_ids)).delete(synchronize_session=False)
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
    """批量清理过期权限"""
    db = SessionLocal()
    try:
        from app.models import UserPermission

        now = datetime.now()

        # 批量更新过期权限状态
        count = db.query(UserPermission).filter(
            UserPermission.expire_at < now,
            UserPermission.status == 1
        ).update({"status": 0}, synchronize_session=False)

        db.commit()

        logger.info(f"清理过期权限完成，共清理 {count} 个权限")

        return {"success": True, "count": count}

    except Exception as e:
        db.rollback()
        logger.error(f"清理过期权限失败: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@shared_task
def cleanup_expired_coupons():
    """批量标记过期优惠券"""
    db = SessionLocal()
    try:
        from app.models.coupon import UserCoupon, Coupon

        now = datetime.now()

        # 批量更新过期的用户优惠券
        count = db.query(UserCoupon).join(Coupon).filter(
            UserCoupon.status == 0,
            Coupon.expire_at < now
        ).update({"status": 2}, synchronize_session=False)

        db.commit()

        logger.info(f"标记过期优惠券完成，共标记 {count} 个")

        return {"success": True, "count": count}

    except Exception as e:
        db.rollback()
        logger.error(f"标记过期优惠券失败: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@shared_task
def cleanup_old_logs():
    """清理旧日志（保留30天）"""
    try:
        from app.core.mongodb_logger import mongo_logger

        expire_date = datetime.now() - timedelta(days=30)

        # 删除30天前的日志
        result = mongo_logger.collection.delete_many({
            "timestamp": {"$lt": expire_date}
        })

        logger.info(f"清理旧日志完成，共删除 {result.deleted_count} 条")

        return {"success": True, "count": result.deleted_count}

    except Exception as e:
        logger.error(f"清理旧日志失败: {str(e)}")
        return {"success": False, "error": str(e)}
