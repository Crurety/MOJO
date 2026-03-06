from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.schemas import BaseResponse
from app.services import OrderService, TaskService, UserService, WorkService

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    user_service = UserService(db)
    order_service = OrderService(db)
    task_service = TaskService(db)

    total_users = user_service.get_total()
    new_users_today = user_service.get_total_by_date(datetime.now().date())

    today_revenue = order_service.get_total_revenue(
        start_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    )
    month_revenue = order_service.get_total_revenue(
        start_date=datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    )

    pending_tasks = len(task_service.get_pending_tasks())
    processing_tasks = len(task_service.get_processing_tasks())

    return {
        "users": {"total": total_users, "new_today": new_users_today},
        "revenue": {"today": float(today_revenue), "month": float(month_revenue)},
        "tasks": {"pending": pending_tasks, "processing": processing_tasks},
    }


@router.get("/users")
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: int | None = Query(None),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    users = user_service.get_list(skip, limit, status)

    if keyword:
        users = [
            u
            for u in users
            if keyword in (u.email or "")
            or keyword in (u.phone or "")
            or keyword in (u.nickname or "")
        ]

    total = user_service.get_total(status)
    return {
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "phone": u.phone,
                "nickname": u.nickname,
                "status": u.status,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ],
        "total": total,
    }


@router.put("/users/{user_id}/status", response_model=BaseResponse)
def update_user_status(
    user_id: int,
    status: int,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    if status == 0:
        user_service.disable(user_id)
    else:
        user_service.enable(user_id)
    return BaseResponse(message="User status updated")


@router.get("/orders")
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: int | None = Query(None),
    order_type: str | None = Query(None),
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)
    orders = order_service.get_all_orders(skip, limit, status, order_type)

    return {
        "items": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "user_id": o.user_id,
                "product_name": o.product_name,
                "amount": float(o.amount),
                "status": o.status,
                "payment_method": o.payment_method,
                "created_at": o.created_at.isoformat(),
                "paid_at": o.paid_at.isoformat() if o.paid_at else None,
            }
            for o in orders
        ]
    }


@router.get("/revenue/stats")
def get_revenue_stats(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)

    start = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
    end = datetime.fromisoformat(end_date) if end_date else datetime.now()
    total_revenue = order_service.get_total_revenue(start, end)

    return {
        "total_revenue": float(total_revenue),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
    }


@router.get("/permissions/prices")
def get_permission_prices():
    return {
        "script": {"per_use": 1, "monthly": 29, "yearly": 199},
        "image": {"per_use": 3, "monthly": 99, "yearly": 699},
        "video": {"per_use": 5, "monthly": 199, "yearly": 1399},
        "ad": {"per_use": 8, "monthly": 299, "yearly": 1999},
    }


@router.put("/permissions/prices", response_model=BaseResponse)
def update_permission_prices(prices: dict[str, Any], db: Session = Depends(get_db)):
    # TODO: persist custom pricing in config storage.
    return BaseResponse(message="Prices updated")


@router.get("/works/quality")
def get_works_for_quality_check(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    work_service = WorkService(db)
    works = work_service.get_public_works(skip, limit)

    return {
        "items": [
            {
                "id": w.id,
                "user_id": w.user_id,
                "work_type": w.work_type,
                "file_url": w.file_url,
                "quality_score": w.quality_score,
                "created_at": w.created_at.isoformat(),
            }
            for w in works
        ]
    }


@router.put("/works/{work_id}/quality", response_model=BaseResponse)
def update_work_quality(
    work_id: int,
    quality_score: int,
    is_public: int | None = None,
    db: Session = Depends(get_db),
):
    work_service = WorkService(db)

    update_data = {"quality_score": quality_score}
    if is_public is not None:
        update_data["is_public"] = is_public

    work_service.update(work_id, **update_data)
    return BaseResponse(message="Work quality updated")
