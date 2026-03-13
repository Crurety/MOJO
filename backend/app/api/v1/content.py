"""Content API routes."""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.rate_limit import RATE_LIMITS, limiter
from app.models import User
from app.schemas import (
    BaseResponse,
    ScriptCreate,
    ScriptResponse,
    ScriptUpdate,
    TaskCreate,
    TaskResponse,
    WorkResponse,
)
from app.services import PermissionService, ScriptService, TaskService, WorkService
from app.tasks import process_content_task
from app.ai import script_generator
from app.utils import calculate_cost

router = APIRouter()
logger = logging.getLogger(__name__)


@limiter.limit(RATE_LIMITS["content"])
@router.post("/scripts", response_model=BaseResponse)
async def create_script(
    request: Request,
    script_in: ScriptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    script_service = ScriptService(db)
    permission_service = PermissionService(db)

    # Manual script content does not consume script quota; AI generation by keywords does.
    needs_permission = not (script_in.content and script_in.content.strip())
    if needs_permission:
        has_permission, message = permission_service.check_permission(
            current_user.id,
            "script",
            with_message=True,
        )
        if not has_permission:
            raise BadRequestException(detail=message)

    generated_content = None
    if not (script_in.content and script_in.content.strip()):
        try:
            generated = await script_generator.generate_from_keywords(
                keywords=script_in.keywords or "",
                output_type=script_in.output_type,
                style=(script_in.parameters or {}).get("style"),
                scene_count=(script_in.parameters or {}).get("scene_count", 1),
            )
            generated_content = (generated.get("script") or "").strip()
        except Exception as exc:
            logger.warning("Script generation failed: %s", exc)
            raise BadRequestException(detail="Script generation failed. Check AI configuration and try again.") from exc

        if not generated_content:
            raise BadRequestException(detail="Script generation failed: empty content returned.")

    script = script_service.create(
        current_user.id,
        script_in,
        generated_content=generated_content,
    )

    if needs_permission and not permission_service.use_permission(current_user.id, "script", 1):
        raise BadRequestException(detail="使用次数不足")

    return BaseResponse(
        message="Script created",
        data={
            "script_id": script.id,
            "script": ScriptResponse.model_validate(script).model_dump(mode="json"),
        },
    )


@limiter.limit(RATE_LIMITS["general"])
@router.get("/scripts", response_model=List[ScriptResponse])
def get_user_scripts(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    script_service = ScriptService(db)
    scripts = script_service.get_user_scripts(current_user.id, skip, limit)
    return [ScriptResponse.model_validate(s) for s in scripts]


@limiter.limit(RATE_LIMITS["general"])
@router.get("/scripts/{script_id}", response_model=ScriptResponse)
def get_script(
    request: Request,
    script_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    script_service = ScriptService(db)
    script = script_service.get_by_id(script_id)
    if not script or script.user_id != current_user.id:
        raise NotFoundException(detail="Script not found")
    return ScriptResponse.model_validate(script)


@limiter.limit(RATE_LIMITS["content"])
@router.put("/scripts/{script_id}", response_model=BaseResponse)
def update_script(
    request: Request,
    script_id: int,
    script_in: ScriptUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    script_service = ScriptService(db)
    script = script_service.get_by_id(script_id)
    if not script or script.user_id != current_user.id:
        raise NotFoundException(detail="Script not found")
    script_service.update(script_id, script_in)
    return BaseResponse(message="Script updated")


@limiter.limit(RATE_LIMITS["content"])
@router.delete("/scripts/{script_id}", response_model=BaseResponse)
def delete_script(
    request: Request,
    script_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    script_service = ScriptService(db)
    deleted = script_service.delete(script_id, current_user.id)
    if not deleted:
        raise NotFoundException(detail="Script not found")
    return BaseResponse(message="Script deleted")


@limiter.limit(RATE_LIMITS["content"])
@router.post("/tasks", response_model=BaseResponse)
def create_task(
    request: Request,
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    permission_service = PermissionService(db)
    task_service = TaskService(db)

    clarity = (
        task_in.parameters.get("clarity", "1080p") if task_in.parameters else "1080p"
    )
    duration = task_in.parameters.get("duration", 0) if task_in.parameters else 0
    count = task_in.parameters.get("count", 1) if task_in.parameters else 1

    cost_amount = calculate_cost(
        task_type=task_in.task_type,
        clarity=clarity,
        duration=duration,
        count=count,
    )

    has_permission, message = permission_service.check_permission(
        current_user.id,
        task_in.task_type,
        required_count=cost_amount,
        with_message=True,
    )
    if not has_permission:
        raise BadRequestException(detail=message)

    task = task_service.create(
        user_id=current_user.id,
        task_type=task_in.task_type,
        parameters=task_in.parameters,
        cost_amount=cost_amount,
    )

    permission_consumed = False
    permission_allocations: list[tuple[int, int]] = []
    try:
        reserved = permission_service.reserve_permission(current_user.id, task_in.task_type, cost_amount)
        if reserved is None:
            raise BadRequestException(detail="Insufficient usage count.")
        permission_allocations = reserved
        permission_consumed = True

        process_content_task.delay(task.id)
    except Exception as exc:
        if permission_consumed:
            permission_service.release_permission_allocations(permission_allocations)
        db.delete(task)
        db.commit()

        if isinstance(exc, BadRequestException):
            raise

        logger.warning("Task dispatch failed: %s", exc)
        raise BadRequestException(detail="Task submission failed. Please try again later.") from exc

    return BaseResponse(
        message="Task created",
        data={
            "task_id": task.id,
            "task_no": task.task_no,
            "task": TaskResponse.model_validate(task).model_dump(mode="json"),
        },
    )


@limiter.limit(RATE_LIMITS["content"])
@router.post("/tasks/image", response_model=BaseResponse)
def create_image_task(
    request: Request,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task_in = TaskCreate(task_type="image", parameters=payload)
    return create_task(request=request, task_in=task_in, current_user=current_user, db=db)


@limiter.limit(RATE_LIMITS["content"])
@router.post("/tasks/video", response_model=BaseResponse)
def create_video_task(
    request: Request,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task_in = TaskCreate(task_type="video", parameters=payload)
    return create_task(request=request, task_in=task_in, current_user=current_user, db=db)


@limiter.limit(RATE_LIMITS["general"])
@router.get("/tasks", response_model=List[TaskResponse])
def get_user_tasks(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[int] = Query(None),
    task_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task_service = TaskService(db)
    tasks = task_service.get_user_tasks(current_user.id, skip, limit, status, task_type)
    return [TaskResponse.model_validate(t) for t in tasks]


@limiter.limit(RATE_LIMITS["general"])
@router.get("/tasks/{task_ref}", response_model=TaskResponse)
def get_task(
    request: Request,
    task_ref: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task_service = TaskService(db)

    task = None
    if task_ref.isdigit():
        task = task_service.get_by_id(int(task_ref))
    if not task:
        task = task_service.get_by_task_no(task_ref)

    if not task or task.user_id != current_user.id:
        raise NotFoundException(detail="Task not found")
    return TaskResponse.model_validate(task)


@limiter.limit(RATE_LIMITS["general"])
@router.get("/works", response_model=List[WorkResponse])
def get_user_works(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    work_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    work_service = WorkService(db)
    works = work_service.get_user_works(current_user.id, skip, limit, work_type)
    return [WorkResponse.model_validate(w) for w in works]


@limiter.limit(RATE_LIMITS["general"])
@router.get("/works/{work_id}", response_model=WorkResponse)
def get_work(
    request: Request,
    work_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    work_service = WorkService(db)
    work = work_service.get_by_id(work_id)
    if not work or work.user_id != current_user.id:
        raise NotFoundException(detail="Work not found")
    return WorkResponse.model_validate(work)


@limiter.limit(RATE_LIMITS["content"])
@router.delete("/works/{work_id}", response_model=BaseResponse)
def delete_work(
    request: Request,
    work_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    work_service = WorkService(db)
    deleted = work_service.delete(work_id, current_user.id)
    if not deleted:
        raise NotFoundException(detail="Work not found")
    return BaseResponse(message="Work deleted")


@limiter.limit(RATE_LIMITS["general"])
@router.get("/gallery", response_model=List[WorkResponse])
def get_gallery(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    work_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    work_service = WorkService(db)
    works = work_service.get_public_works(skip, limit, work_type)
    return [WorkResponse.model_validate(w) for w in works]
