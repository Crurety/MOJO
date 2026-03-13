from __future__ import annotations

import asyncio
import base64
from datetime import datetime, timedelta
from typing import Any, Dict

from app.ai import ad_design_service, image_generator, script_generator, video_generator
from app.core.database import SessionLocal
from app.models import Task, UserPermission, Work
from app.services import MessageService, ScriptService, TaskService, WorkService
from app.tasks.celery_app import celery_app
from app.utils.storage import storage_service


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _save_base64_images(images: list[dict], sub_dir: str) -> list[str]:
    image_urls: list[str] = []
    for image in images:
        base64_data = image.get("base64")
        if not base64_data:
            continue
        image_data = base64.b64decode(base64_data)
        file_path = await storage_service.save_file(
            file_content=image_data,
            file_extension=".png",
            sub_dir=sub_dir,
        )
        image_urls.append(storage_service.get_file_url(file_path))
    return image_urls


async def process_script_task(task: Task) -> Dict[str, Any]:
    params = task.parameters or {}
    keywords = params.get("keywords", "")
    output_type = params.get("output_type", "image_set")
    style = params.get("style")
    scene_count = params.get("scene_count", 1)

    result = await script_generator.generate_from_keywords(
        keywords=keywords,
        output_type=output_type,
        style=style,
        scene_count=scene_count,
    )
    return {
        "script": result.get("script", ""),
        "keywords": keywords,
        "output_type": output_type,
    }


async def process_image_task(task: Task) -> Dict[str, Any]:
    params = task.parameters or {}
    script_id = params.get("script_id")
    prompt = params.get("prompt", "")
    clarity = params.get("clarity", "1080p")
    style = params.get("style")
    count = params.get("count", 1)
    reference_image = params.get("reference_image")

    if script_id:
        db = SessionLocal()
        try:
            script_service = ScriptService(db)
            script = script_service.get_by_id(int(script_id))
            if script:
                prompt = script.content
        finally:
            db.close()

    if reference_image:
        result = await image_generator.generate_with_reference(
            reference_image=reference_image,
            prompt=prompt,
            clarity=clarity,
            style=style,
        )
        images = result.get("images", [])
    else:
        result = await image_generator.generate_single(
            prompt=prompt,
            clarity=clarity,
            style=style,
            count=max(1, int(count)),
        )
        images = result.get("images", [])

    image_urls = await _save_base64_images(images, sub_dir="images")
    if not image_urls:
        raise ValueError("Image generation returned no images")
    return {"images": image_urls, "count": len(image_urls)}


async def process_video_task(task: Task) -> Dict[str, Any]:
    params = task.parameters or {}
    script_id = params.get("script_id")
    prompt = params.get("prompt", "")
    duration = params.get("duration", 4)
    clarity = params.get("clarity", "1080p")
    style = params.get("style")

    if script_id:
        db = SessionLocal()
        try:
            script_service = ScriptService(db)
            script = script_service.get_by_id(int(script_id))
            if script:
                prompt = script.content
        finally:
            db.close()

    result = await video_generator.generate(
        prompt=prompt,
        duration=max(1, int(duration)),
        clarity=clarity,
        style=style,
    )
    return {
        "external_task_id": result.get("task_id"),
        "status": result.get("status", "pending"),
        "estimated_time": result.get("estimated_time"),
        "result_url": result.get("result_url"),
    }


async def process_ad_task(task: Task) -> Dict[str, Any]:
    params = task.parameters or {}
    ad_type = params.get("ad_type", "image")
    product_info = params.get("product_info", "")
    target_audience = params.get("target_audience", "")
    brand_style = params.get("brand_style")
    clarity = params.get("clarity", "1080p")
    duration = params.get("duration", 15)
    creative_plan = params.get("creative_plan")

    if not creative_plan:
        creative_plan = await ad_design_service.analyze_requirements(
            product_info=product_info,
            target_audience=target_audience,
            ad_type=ad_type,
            brand_style=brand_style,
        )

    if ad_type == "image":
        result = await ad_design_service.generate_image_ad(
            creative_plan=creative_plan,
            clarity=clarity,
            style=brand_style,
        )
        image_urls = await _save_base64_images(result.get("images", []), sub_dir="ads")
        return {"ad_type": ad_type, "creative_plan": creative_plan, "images": image_urls}

    result = await ad_design_service.generate_video_ad(
        creative_plan=creative_plan,
        duration=max(1, int(duration)),
        clarity=clarity,
        style=brand_style,
    )
    return {
        "ad_type": ad_type,
        "creative_plan": creative_plan,
        "external_task_id": result.get("task_id"),
        "status": result.get("status", "pending"),
        "result_url": result.get("result_url"),
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
        result: Dict[str, Any] = {}
        result_url: str | None = None

        if task.task_type == "script":
            result = run_async(process_script_task(task))
            task_service.update_status(task_id, status=2, progress=100)
            message_service.send_task_complete_notification(
                user_id=task.user_id,
                task_no=task.task_no,
                task_type=task.task_type,
                result_url="",
            )
            return {"status": "success", "result": result}

        if task.task_type == "image":
            result = run_async(process_image_task(task))
            images = result.get("images", [])
            result_url = images[0] if images else None
            if result_url:
                work_service.create(
                    user_id=task.user_id,
                    work_type=task.task_type,
                    file_url=result_url,
                    task_id=task.id,
                    title=f"Generated {task.task_type}",
                    parameters=task.parameters,
                )
            task_service.update_status(task_id, status=2, progress=100, result_url=result_url)
            message_service.send_task_complete_notification(
                user_id=task.user_id,
                task_no=task.task_no,
                task_type=task.task_type,
                result_url=result_url or "",
            )
            return {"status": "success", "result": result}

        if task.task_type == "video":
            result = run_async(process_video_task(task))
            result_url = result.get("result_url")
            external_task_id = result.get("external_task_id")
            if external_task_id and not result_url:
                task.parameters = {**(task.parameters or {}), "external_task_id": external_task_id}
                db.commit()
                task_service.update_status(task_id, status=1, progress=60)
                return {"status": "processing", "result": result}

            if not result_url:
                error_message = "Generation returned neither an external task ID nor a result URL."
                task_service.update_status(task_id, status=3, error_message=error_message)
                message_service.send_task_failed_notification(
                    user_id=task.user_id,
                    task_no=task.task_no,
                    task_type=task.task_type,
                    error_message=error_message,
                )
                return {"status": "error", "message": error_message}

            work_service.create(
                user_id=task.user_id,
                work_type=task.task_type,
                file_url=result_url,
                task_id=task.id,
                title=f"Generated {task.task_type}",
                parameters=task.parameters,
            )
            task_service.update_status(task_id, status=2, progress=100, result_url=result_url)
            message_service.send_task_complete_notification(
                user_id=task.user_id,
                task_no=task.task_no,
                task_type=task.task_type,
                result_url=result_url,
            )
            return {"status": "success", "result": result}

        if task.task_type == "ad":
            result = run_async(process_ad_task(task))
            ad_type = result.get("ad_type", "image")
            if ad_type == "image":
                images = result.get("images", [])
                result_url = images[0] if images else None
                if not result_url:
                    error_message = "Ad image generation returned no images."
                    task_service.update_status(task_id, status=3, error_message=error_message)
                    message_service.send_task_failed_notification(
                        user_id=task.user_id,
                        task_no=task.task_no,
                        task_type=task.task_type,
                        error_message=error_message,
                    )
                    return {"status": "error", "message": error_message}

                work_service.create(
                    user_id=task.user_id,
                    work_type=task.task_type,
                    file_url=result_url,
                    task_id=task.id,
                    title="Generated ad image",
                    parameters=task.parameters,
                )
                task_service.update_status(task_id, status=2, progress=100, result_url=result_url)
                message_service.send_task_complete_notification(
                    user_id=task.user_id,
                    task_no=task.task_no,
                    task_type=task.task_type,
                    result_url=result_url,
                )
                return {"status": "success", "result": result}

            result_url = result.get("result_url")
            external_task_id = result.get("external_task_id")
            if external_task_id and not result_url:
                task.parameters = {
                    **(task.parameters or {}),
                    "external_task_id": external_task_id,
                    "creative_plan": result.get("creative_plan"),
                    "ad_type": "video",
                }
                db.commit()
                task_service.update_status(task_id, status=1, progress=60)
                return {"status": "processing", "result": result}

            if not result_url:
                error_message = "Generation returned neither an external task ID nor a result URL."
                task_service.update_status(task_id, status=3, error_message=error_message)
                message_service.send_task_failed_notification(
                    user_id=task.user_id,
                    task_no=task.task_no,
                    task_type=task.task_type,
                    error_message=error_message,
                )
                return {"status": "error", "message": error_message}

            work_service.create(
                user_id=task.user_id,
                work_type=task.task_type,
                file_url=result_url,
                task_id=task.id,
                title="Generated ad video",
                parameters=task.parameters,
            )
            task_service.update_status(task_id, status=2, progress=100, result_url=result_url)
            message_service.send_task_complete_notification(
                user_id=task.user_id,
                task_no=task.task_no,
                task_type=task.task_type,
                result_url=result_url,
            )
            return {"status": "success", "result": result}

        task_service.update_status(task_id, status=3, error_message="Unknown task type")
        return {"status": "error", "message": "Unknown task type"}
    except Exception as exc:
        task_service = TaskService(db)
        message_service = MessageService(db)
        task = task_service.get_by_id(task_id)
        task_service.update_status(task_id, status=3, error_message=str(exc))
        if task:
            message_service.send_task_failed_notification(
                user_id=task.user_id,
                task_no=task.task_no,
                task_type=task.task_type,
                error_message=str(exc),
            )
        return {"status": "error", "message": str(exc)}
    finally:
        db.close()


@celery_app.task
def check_video_status():
    db = SessionLocal()
    try:
        task_service = TaskService(db)
        work_service = WorkService(db)
        message_service = MessageService(db)

        processing_tasks = (
            db.query(Task)
            .filter(Task.status == 1, Task.task_type.in_(["video", "ad"]))
            .all()
        )

        checked = 0
        for task in processing_tasks:
            params = task.parameters or {}
            external_task_id = params.get("external_task_id")
            if not external_task_id:
                continue

            checked += 1
            try:
                status_result = run_async(video_generator.get_status(external_task_id))
            except Exception as exc:
                # 保持处理中，等待下一轮。
                task.error_message = str(exc)
                db.commit()
                continue

            status = (status_result.get("status") or "").lower()
            if status in {"completed", "succeeded", "success"}:
                result_url = status_result.get("result_url")
                if not result_url:
                    error_message = "Generation completed without a result URL."
                    task_service.update_status(task.id, status=3, error_message=error_message)
                    message_service.send_task_failed_notification(
                        user_id=task.user_id,
                        task_no=task.task_no,
                        task_type=task.task_type,
                        error_message=error_message,
                    )
                    continue

                task_service.update_status(task.id, status=2, progress=100, result_url=result_url)
                work_service.create(
                    user_id=task.user_id,
                    work_type=task.task_type,
                    file_url=result_url,
                    task_id=task.id,
                    title=f"Generated {task.task_type}",
                    parameters=task.parameters,
                )
                message_service.send_task_complete_notification(
                    user_id=task.user_id,
                    task_no=task.task_no,
                    task_type=task.task_type,
                    result_url=result_url,
                )
            elif status in {"failed", "error", "cancelled"}:
                task_service.update_status(
                    task.id,
                    status=3,
                    error_message=status_result.get("error", "Video generation failed"),
                )
                message_service.send_task_failed_notification(
                    user_id=task.user_id,
                    task_no=task.task_no,
                    task_type=task.task_type,
                    error_message=status_result.get("error", "Video generation failed"),
                )
            else:
                progress = status_result.get("progress")
                if isinstance(progress, int) and 0 <= progress <= 99:
                    task_service.update_status(task.id, status=1, progress=progress)

        return {"checked_count": checked}
    finally:
        db.close()


@celery_app.task
def cleanup_expired_tasks():
    db = SessionLocal()
    try:
        expired_date = datetime.now() - timedelta(days=30)
        expired_tasks = db.query(Task).filter(Task.created_at < expired_date, Task.status.in_([2, 3])).all()
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
        old_works = db.query(Work).filter(Work.created_at < expired_date, Work.is_public == 0).all()
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
        expired_permissions = (
            db.query(UserPermission)
            .filter(
                UserPermission.expire_at < now,
                UserPermission.status == 1,
                UserPermission.payment_mode.in_(["monthly", "yearly"]),
            )
            .all()
        )
        for permission in expired_permissions:
            permission.status = 0
        db.commit()
        return {"expired_count": len(expired_permissions)}
    finally:
        db.close()

