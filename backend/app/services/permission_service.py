from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import UserPermission


class PermissionService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_permissions(self, user_id: int) -> List[UserPermission]:
        return (
            self.db.query(UserPermission)
            .filter(UserPermission.user_id == user_id, UserPermission.status == 1)
            .all()
        )

    def get_permission(self, user_id: int, permission_type: str) -> Optional[UserPermission]:
        return (
            self.db.query(UserPermission)
            .filter(
                UserPermission.user_id == user_id,
                UserPermission.permission_type == permission_type,
                UserPermission.status == 1,
            )
            .first()
        )

    def check_permission(
        self,
        user_id: int,
        permission_type: str,
        required_count: int = 1,
        with_message: bool = False,
    ):
        permission = self.get_permission(user_id, permission_type)
        if not permission:
            result = (False, f"未开通{permission_type}权限")
            return result if with_message else result[0]

        if permission.payment_mode == "per_use":
            remaining = permission.total_count - permission.used_count
            if remaining < required_count:
                result = (False, f"使用次数不足，剩余{remaining}次")
                return result if with_message else result[0]
        else:
            if permission.expire_at and permission.expire_at < datetime.now():
                result = (False, "权限已过期")
                return result if with_message else result[0]

        result = (True, "权限有效")
        return result if with_message else result[0]

    def use_permission(self, user_id: int, permission_type: str, count: int = 1) -> bool:
        permission = self.get_permission(user_id, permission_type)
        if not permission:
            return False

        if permission.payment_mode == "per_use":
            has_permission = self.check_permission(
                user_id=user_id,
                permission_type=permission_type,
                required_count=count,
            )
            if not has_permission:
                return False
            permission.used_count += count

        self.db.commit()
        return True

    # Backward-compatible alias used by tests.
    def consume_permission(self, user_id: int, permission_type: str, count: int = 1) -> bool:
        return self.use_permission(user_id, permission_type, count)

    def grant_permission(
        self,
        user_id: int,
        permission_type: str,
        payment_mode: str,
        count: int = 0,
        days: int = 0,
    ) -> UserPermission:
        existing = (
            self.db.query(UserPermission)
            .filter(
                UserPermission.user_id == user_id,
                UserPermission.permission_type == permission_type,
            )
            .first()
        )

        if existing:
            if payment_mode == "per_use":
                existing.total_count += count
                existing.status = 1
            else:
                if existing.expire_at and existing.expire_at > datetime.now():
                    existing.expire_at += timedelta(days=days)
                else:
                    existing.expire_at = datetime.now() + timedelta(days=days)
                existing.status = 1

            self.db.commit()
            return existing

        permission = UserPermission(
            user_id=user_id,
            permission_type=permission_type,
            payment_mode=payment_mode,
            total_count=count if payment_mode == "per_use" else 0,
            expire_at=datetime.now() + timedelta(days=days) if payment_mode != "per_use" else None,
            status=1,
        )

        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def get_permission_price(self, permission_type: str, payment_mode: str) -> Decimal:
        prices = {
            "script": {"per_use": 1, "monthly": 29, "yearly": 199},
            "image": {"per_use": 3, "monthly": 99, "yearly": 699},
            "video": {"per_use": 5, "monthly": 199, "yearly": 1399},
            "ad": {"per_use": 8, "monthly": 299, "yearly": 1999},
        }
        return Decimal(prices.get(permission_type, {}).get(payment_mode, 0))
