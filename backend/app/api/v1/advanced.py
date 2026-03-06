"""高级运营功能API"""

from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Body, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.core.database import get_db
from app.core.rate_limit import RATE_LIMITS, limiter
from app.models import User
from app.schemas import BaseResponse
from app.services.ab_test_service import ABTestService
from app.services.push_service import PushService
from app.services.user_tag_service import UserTagService

router = APIRouter()


# 用户标签接口
class TagCreate(BaseModel):
    tag_name: str
    tag_category: str
    description: str | None = None
    color: str | None = None


@router.post("/admin/tags", response_model=BaseResponse)
def create_tag(
    tag_in: TagCreate,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """创建标签（管理员）"""
    tag_service = UserTagService(db)
    tag = tag_service.create_tag(
        tag_name=tag_in.tag_name,
        tag_category=tag_in.tag_category,
        tag_type="manual",
        description=tag_in.description,
        color=tag_in.color,
    )

    return BaseResponse(message="标签创建成功", data={"tag_id": tag.id})


@router.get("/admin/tags")
def get_all_tags(
    category: str = Query(None),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取所有标签（管理员）"""
    tag_service = UserTagService(db)
    tags = tag_service.get_all_tags(category)

    return {
        "items": [
            {
                "id": t.id,
                "tag_name": t.tag_name,
                "tag_category": t.tag_category,
                "tag_type": t.tag_type,
                "description": t.description,
                "color": t.color,
            }
            for t in tags
        ]
    }


@router.post("/admin/users/{user_id}/tags/{tag_id}", response_model=BaseResponse)
def add_user_tag(
    user_id: int,
    tag_id: int,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """给用户打标签（管理员）"""
    tag_service = UserTagService(db)
    tag_service.add_user_tag(user_id, tag_id, tag_source="manual")

    return BaseResponse(message="标签添加成功")


@router.get("/admin/users/{user_id}/tags")
def get_user_tags(
    user_id: int,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取用户标签（管理员）"""
    tag_service = UserTagService(db)
    tags = tag_service.get_user_tags(user_id)

    return {
        "items": [
            {
                "tag_id": t.tag_id,
                "tag_name": t.tag.tag_name,
                "tag_category": t.tag.tag_category,
                "tag_source": t.tag_source,
                "confidence": t.confidence,
                "created_at": t.created_at,
            }
            for t in tags
        ]
    }


@router.post("/admin/tags/auto-tag-active-users", response_model=BaseResponse)
def auto_tag_active_users(
    current_admin=Depends(get_current_admin), db: Session = Depends(get_db)
):
    """自动标记活跃用户（管理员）"""
    tag_service = UserTagService(db)
    count = tag_service.auto_tag_active_users()

    return BaseResponse(message=f"已标记 {count} 个活跃用户")


# AB测试接口
class ABTestCreate(BaseModel):
    test_name: str
    test_type: str
    description: str
    variants: List[Dict]
    start_at: str
    end_at: str
    target_users: str = "all"


@router.post("/admin/ab-tests", response_model=BaseResponse)
def create_ab_test(
    test_in: ABTestCreate,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """创建AB测试（管理员）"""
    ab_test_service = ABTestService(db)
    test = ab_test_service.create_test(
        test_name=test_in.test_name,
        test_type=test_in.test_type,
        description=test_in.description,
        variants=test_in.variants,
        start_at=datetime.fromisoformat(test_in.start_at),
        end_at=datetime.fromisoformat(test_in.end_at),
        target_users=test_in.target_users,
    )

    return BaseResponse(message="AB测试创建成功", data={"test_id": test.id})


@router.get("/ab-tests/{test_id}/variant")
def get_user_variant(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户分配的变体"""
    ab_test_service = ABTestService(db)
    variant = ab_test_service.assign_user_to_variant(test_id, current_user.id)

    return {"variant": variant}


@router.post("/ab-tests/{test_id}/metrics", response_model=BaseResponse)
def record_ab_test_metric(
    test_id: int,
    metric_name: str = Body(...),
    metric_value: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """记录AB测试指标"""
    ab_test_service = ABTestService(db)
    ab_test_service.record_metric(test_id, current_user.id, metric_name, metric_value)

    return BaseResponse(message="指标记录成功")


@router.get("/admin/ab-tests/{test_id}/results")
def get_ab_test_results(
    test_id: int,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取AB测试结果（管理员）"""
    ab_test_service = ABTestService(db)
    return ab_test_service.get_test_results(test_id)


@router.put("/admin/ab-tests/{test_id}/end", response_model=BaseResponse)
def end_ab_test(
    test_id: int,
    winner_variant: str = Body(None),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """结束AB测试（管理员）"""
    ab_test_service = ABTestService(db)
    ab_test_service.end_test(test_id, winner_variant)

    return BaseResponse(message="AB测试已结束")


# 推送通知接口
class PushCreate(BaseModel):
    notification_type: str
    target_type: str
    title: str
    content: str
    target_value: Dict | None = None
    link: str | None = None
    image_url: str | None = None
    send_at: str | None = None


@router.post("/admin/push", response_model=BaseResponse)
def create_push_notification(
    push_in: PushCreate,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """创建推送通知（管理员）"""
    push_service = PushService(db)

    send_at = datetime.fromisoformat(push_in.send_at) if push_in.send_at else None

    push = push_service.create_push(
        notification_type=push_in.notification_type,
        target_type=push_in.target_type,
        title=push_in.title,
        content=push_in.content,
        target_value=push_in.target_value,
        link=push_in.link,
        image_url=push_in.image_url,
        send_at=send_at,
    )

    return BaseResponse(message="推送创建成功", data={"push_id": push.id})


@router.get("/admin/push/{push_id}/statistics")
def get_push_statistics(
    push_id: int,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取推送统计（管理员）"""
    push_service = PushService(db)
    return push_service.get_push_statistics(push_id)


@router.post("/push/{push_id}/click", response_model=BaseResponse)
def record_push_click(
    push_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """记录推送点击"""
    push_service = PushService(db)
    push_service.record_click(push_id, current_user.id)

    return BaseResponse(message="点击记录成功")


@router.delete("/admin/push/{push_id}", response_model=BaseResponse)
def cancel_push_notification(
    push_id: int,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """取消推送（管理员）"""
    push_service = PushService(db)
    success = push_service.cancel_push(push_id)

    if not success:
        return BaseResponse(code=400, message="无法取消该推送")

    return BaseResponse(message="推送已取消")
