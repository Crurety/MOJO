"""异步文件删除任务"""
from celery import shared_task
from app.utils.storage import storage_service
from app.core.logging import logger
from typing import List


@shared_task
def async_delete_file(file_url: str):
    """异步删除单个文件

    Args:
        file_url: 文件URL
    """
    try:
        storage_service.delete_file(file_url)
        logger.info(f"文件删除成功: {file_url}")
        return {"success": True, "file_url": file_url}
    except Exception as e:
        logger.error(f"文件删除失败: {file_url}, 错误: {str(e)}")
        return {"success": False, "file_url": file_url, "error": str(e)}


@shared_task
def async_delete_files(file_urls: List[str]):
    """异步批量删除文件

    Args:
        file_urls: 文件URL列表
    """
    success_count = 0
    failed_count = 0

    for file_url in file_urls:
        try:
            storage_service.delete_file(file_url)
            success_count += 1
            logger.debug(f"文件删除成功: {file_url}")
        except Exception as e:
            failed_count += 1
            logger.error(f"文件删除失败: {file_url}, 错误: {str(e)}")

    logger.info(f"批量删除完成: 成功 {success_count}, 失败 {failed_count}")

    return {
        "success": True,
        "total": len(file_urls),
        "success_count": success_count,
        "failed_count": failed_count
    }


@shared_task
def cleanup_orphan_files():
    """清理孤立文件（数据库中不存在的文件）"""
    from app.core.database import SessionLocal
    from app.models import Work

    db = SessionLocal()
    try:
        # 获取所有存储的文件
        all_files = storage_service.list_files()

        # 获取数据库中的所有文件URL
        db_file_urls = set()
        works = db.query(Work).all()
        for work in works:
            if work.file_url:
                db_file_urls.add(work.file_url)
            if work.thumbnail_url:
                db_file_urls.add(work.thumbnail_url)

        # 找出孤立文件
        orphan_files = [f for f in all_files if f not in db_file_urls]

        if orphan_files:
            # 批量删除
            async_delete_files.delay(orphan_files)
            logger.info(f"发现 {len(orphan_files)} 个孤立文件，已提交删除任务")

        return {
            "success": True,
            "total_files": len(all_files),
            "db_files": len(db_file_urls),
            "orphan_files": len(orphan_files)
        }

    except Exception as e:
        logger.error(f"清理孤立文件失败: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()
