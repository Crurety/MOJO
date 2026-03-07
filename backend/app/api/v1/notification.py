"""消息通知API路由"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas import BaseResponse
from app.services.notification_service import NotificationService
from app.core.rate_limit import limiter, RATE_LIMITS
from typing import List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


router = APIRouter()


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    content: str
    message_type: str
    is_read: int
    link: str | None
    created_at: datetime


@limiter.limit(RATE_LIMITS["general"])
@router.get("/messages", response_model=List[MessageResponse])
def get_messages(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_read: int = Query(None),
    message_type: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户消息列表

    Args:
        skip: 跳过数量
        limit: 返回数量
        is_read: 是否已读 (0未读/1已读)
        message_type: 消息类型 (system/task/promotion)
        current_user: 当前用户
        db: 数据库会话

    Returns:
        List[MessageResponse]: 消息列表
    """
    notification_service = NotificationService(db)
    messages = notification_service.get_user_messages(
        current_user.id, skip, limit, is_read, message_type
    )
    return [MessageResponse.model_validate(m) for m in messages]


@limiter.limit(RATE_LIMITS["general"])
@router.get("/messages/unread-count")
def get_unread_count(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取未读消息数量

    Args:
        current_user: 当前用户
        db: 数据库会话

    Returns:
        dict: 未读消息数量
    """
    notification_service = NotificationService(db)
    count = notification_service.get_unread_count(current_user.id)
    return {"unread_count": count}


@limiter.limit(RATE_LIMITS["general"])
@router.put("/messages/{message_id}/read", response_model=BaseResponse)
def mark_message_as_read(
    request: Request,
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记消息为已读

    Args:
        message_id: 消息ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        BaseResponse: 操作结果
    """
    notification_service = NotificationService(db)
    success = notification_service.mark_as_read(message_id, current_user.id)

    if not success:
        return BaseResponse(code=404, message="消息不存在")

    return BaseResponse(message="标记成功")


@limiter.limit(RATE_LIMITS["general"])
@router.put("/messages/read-all", response_model=BaseResponse)
def mark_all_as_read(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记所有消息为已读

    Args:
        current_user: 当前用户
        db: 数据库会话

    Returns:
        BaseResponse: 操作结果
    """
    notification_service = NotificationService(db)
    count = notification_service.mark_all_as_read(current_user.id)

    return BaseResponse(message=f"已标记{count}条消息为已读")


@limiter.limit(RATE_LIMITS["general"])
@router.delete("/messages/{message_id}", response_model=BaseResponse)
def delete_message(
    request: Request,
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除消息

    Args:
        message_id: 消息ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        BaseResponse: 操作结果
    """
    notification_service = NotificationService(db)
    success = notification_service.delete_message(message_id, current_user.id)

    if not success:
        return BaseResponse(code=404, message="消息不存在")

    return BaseResponse(message="删除成功")
