import asyncio
import time
from datetime import datetime, timedelta
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models import Task, Work, UserPermission, Script
from app.services import TaskService, WorkService, ScriptService
from app.services.notification_service import NotificationService
from app.utils import calculate_cost
from app.utils.storage import storage_service
from app.ai import (
    script_generator,
    image_generator,
    video_generator,
    ad_design_service
)
import base64
import os


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


async def process_script_task(task: Task, task_service: TaskService) -> dict:
    params = task.parameters or {}
    keywords = params.get("keywords", "")
    output_type = params.get("output_type", "image")
    style = params.get("style")
    scene_count = params.get("scene_count", 1)

    result = await script_generator.generate_from_keywords(
        keywords=keywords,
        output_type=output_type,
        style=style,
        scene_count=scene_count
    )

    return {
        "script": result.get("script", ""),
        "keywords": keywords,
        "output_type": output_type
    }


async def process_image_task(task: Task, task_service: TaskService) -> dict:
    params = task.parameters or {}
    script_id = params.get("script_id")
    prompt = params.get("prompt", "")
    clarity = params.get("clarity", "1080p")
    style = params.get("style")
    count = params.get("count", 1)
    reference_image = params.get("reference_image")

    if script_id:
        db = SessionLocal()
        script_service = ScriptService(db)
        script = script_service.get_by_id(script_id)
        db.close()

        if script:
            prompt = script.content

    if reference_image:
        result = await image_generator.generate_with_reference(
            reference_image=reference_image,
            prompt=prompt,
            clarity=clarity,
            style=style
        )
    else:
        result = await image_generator.generate_single(
            prompt=prompt,
            clarity=clarity,
            style=style
        )

    image_urls = []
    for img in result.get("images", []):
        if img.get("base64"):
            image_data = base64.b64decode(img["base64"])
            file_path = await storage_service.save_file(
                file_content=image_data,
                file_extension=".png",
                sub_dir="images"
            )
            image_urls.append(storage_service.get_file_url(file_path))

    return {
        "images": image_urls,
        "count": len(image_urls)
    }


async def process_video_task(task: Task, task_service: TaskService) -> dict:
    params = task.parameters or {}
    script_id = params.get("script_id")
    prompt = params.get("prompt", "")
    duration = params.get("duration", 4)
    clarity = params.get("clarity", "1080p")
    style = params.get("style")

    if script_id:
        db = SessionLocal()
        script_service = ScriptService(db)
        script = script_service.get_by_id(script_id)
        db.close()

        if script:
            prompt = script.content

    result = await video_generator.generate(
        prompt=prompt,
        duration=duration,
        clarity=clarity,
        style=style
    )

    return {
        "task_id": result.get("task_id"),
        "status": result.get("status"),
        "estimated_time": result.get("estimated_time")
    }


async def process_ad_task(task: Task, task_service: TaskService) -> dict:
    params = task.parameters or {}
    product_info = params.get("product_info", "")
    target_audience = params.get("target_audience", "")
    ad_type = params.get("ad_type", "image")
    brand_style = params.get("brand_style")
    clarity = params.get("clarity", "1080p")
    duration = params.get("duration", 15)

    creative_plan = await ad_design_service.analyze_requirements(
        product_info=product_info,
        target_audience=target_audience,
        ad_type=ad_type,
        brand_style=brand_style
    )

    if ad_type == "image":
        result = await ad_design_service.generate_image_ad(
            creative_plan=creative_plan,
            clarity=clarity,
            style=brand_style
        )

        image_urls = []
        for img in result.get("images", []):
            if img.get("base64"):
                image_data = base64.b64decode(img["base64"])
                file_path = await storage_service.save_file(
                    file_content=image_data,
                    file_extension=".png",
                    sub_dir="ads"
                )
                image_urls.append(storage_service.get_file_url(file_path))

        return {
            "images": image_urls,
            "creative_plan": creative_plan
        }
    else:
        result = await ad_design_service.generate_video_ad(
            creative_plan=creative_plan,
            duration=duration,
            clarity=clarity,
            style=brand_style
        )

        return {
            "task_id": result.get("task_id"),
            "status": result.get("status"),
            "creative_plan": creative_plan
        }


@celery_app.task(bind=True)
def process_content_task(self, task_id: int):
    db = SessionLocal()
    try:
        task_service = TaskService(db)
        work_service = WorkService(db)
        message_service = MessageService(db)

        task = task_service.get_by_id(task_id)
        if not task:
            return {"status": "error", "message": "Task not found"}

        task_service.update_status(task_id, status=1, progress=10)

        try:
            if task.task_type == "script":
                result = run_async(process_script_task(task, task_service))
                result_url = None
            elif task.task_type == "image":
                result = run_async(process_image_task(task, task_service))
                result_url = result.get("images", [""])[0] if result.get("images") else None
            elif task.task_type == "video":
                result = run_async(process_video_task(task, task_service))
                result_url = None
            elif task.task_type == "ad":
                result = run_async(process_ad_task(task, task_service))
                result_url = result.get("images", [""])[0] if result.get("images") else None
            else:
                result = {"error": "Unknown task type"}
                result_url = None

            task_service.update_status(task_id, status=2, progress=100, result_url=result_url)

            if result_url:
                work = work_service.create(
                    user_id=task.user_id,
                    work_type=task.task_type,
                    file_url=result_url,
                    task_id=task.id,
                    title=f"Generated {task.task_type}",
                    parameters=task.parameters
                )

            message_service.send_task_complete_notification(
                user_id=task.user_id,
                task_no=task.task_no,
                task_type=task.task_type,
                result_url=result_url or ""
            )

            return {"status": "success", "result": result}

        except Exception as e:
            task_service.update_status(
                task_id,
                status=3,
                error_message=str(e)
            )

            message_service.send_task_failed_notification(
                user_id=task.user_id,
                task_no=task.task_no,
                task_type=task.task_type,
                error_message=str(e)
            )

            return {"status": "error", "message": str(e)}

    finally:
        db.close()


@celery_app.task
def check_video_status():
    db = SessionLocal()
    try:
        task_service = TaskService(db)

        processing_tasks = db.query(Task).filter(
            Task.task_type == "video",
            Task.status == 1
        ).all()

        for task in processing_tasks:
            external_task_id = task.parameters.get("external_task_id")
            if external_task_id:
                status_result = run_async(video_generator.get_status(external_task_id))

                if status_result.get("status") == "completed":
                    result_url = status_result.get("result_url")
                    task_service.update_status(task.id, status=2, progress=100, result_url=result_url)
                elif status_result.get("status") == "failed":
                    task_service.update_status(
                        task.id,
                        status=3,
                        error_message=status_result.get("error", "Video generation failed")
                    )

        return {"checked_count": len(processing_tasks)}

    finally:
        db.close()


@celery_app.task
def cleanup_expired_tasks():
    db = SessionLocal()
    try:
        expired_date = datetime.now() - timedelta(days=30)

        expired_tasks = db.query(Task).filter(
            Task.created_at < expired_date,
            Task.status.in_([2, 3])
        ).all()

        for task in expired_tasks:
            db.delete(task)

        db.commit()

        return {"deleted_count": len(expired_tasks)}

    finally:
        db.close()


@celery_app.task
def cleanup_old_works():
    db = SessionLocal()
    try:
        expired_date = datetime.now() - timedelta(days=15)

        old_works = db.query(Work).filter(
            Work.created_at < expired_date,
            Work.is_public == 0
        ).all()

        for work in old_works:
            db.delete(work)

        db.commit()

        return {"deleted_count": len(old_works)}

    finally:
        db.close()


@celery_app.task
def check_expired_permissions():
    db = SessionLocal()
    try:
        now = datetime.now()

        expired_permissions = db.query(UserPermission).filter(
            UserPermission.expire_at < now,
            UserPermission.status == 1,
            UserPermission.payment_mode.in_(["monthly", "yearly"])
        ).all()

        for permission in expired_permissions:
            permission.status = 0

        db.commit()

        return {"expired_count": len(expired_permissions)}

    finally:
        db.close()
