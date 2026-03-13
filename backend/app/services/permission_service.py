from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException
from app.models import UserPermission
from app.services.system_config_service import SystemConfigService

PermissionPriceTable = Dict[str, Dict[str, Decimal]]


class PermissionService:
    PERMISSION_TYPES = ("script", "image", "video", "ad")
    PAYMENT_MODES = ("per_use", "monthly", "yearly")

    DEFAULT_PERMISSION_PRICES: PermissionPriceTable = {
        "script": {"per_use": Decimal("1"), "monthly": Decimal("29"), "yearly": Decimal("199")},
        "image": {"per_use": Decimal("3"), "monthly": Decimal("99"), "yearly": Decimal("699")},
        "video": {"per_use": Decimal("5"), "monthly": Decimal("199"), "yearly": Decimal("1399")},
        "ad": {"per_use": Decimal("8"), "monthly": Decimal("299"), "yearly": Decimal("1999")},
    }

    PRICE_DESCRIPTIONS = {
        "script_price_per_use": "Script generation pay-per-use price",
        "script_price_monthly": "Script generation monthly price",
        "script_price_yearly": "Script generation yearly price",
        "image_price_per_use": "Image generation pay-per-use price",
        "image_price_monthly": "Image generation monthly price",
        "image_price_yearly": "Image generation yearly price",
        "video_price_per_use": "Video generation pay-per-use price",
        "video_price_monthly": "Video generation monthly price",
        "video_price_yearly": "Video generation yearly price",
        "ad_price_per_use": "Ad design pay-per-use price",
        "ad_price_monthly": "Ad design monthly price",
        "ad_price_yearly": "Ad design yearly price",
    }

    def __init__(self, db: Session):
        self.db = db
        self.system_config_service = SystemConfigService(db)

    def get_user_permissions(self, user_id: int) -> List[UserPermission]:
        return (
            self.db.query(UserPermission)
            .filter(UserPermission.user_id == user_id, UserPermission.status == 1)
            .all()
        )

    def get_permission(self, user_id: int, permission_type: str) -> Optional[UserPermission]:
        permissions = self._get_permissions_for_type(user_id, permission_type)
        return permissions[0] if permissions else None

    def _get_permissions_for_type(self, user_id: int, permission_type: str) -> List[UserPermission]:
        return (
            self.db.query(UserPermission)
            .filter(
                UserPermission.user_id == user_id,
                UserPermission.permission_type == permission_type,
                UserPermission.status == 1,
            )
            .order_by(UserPermission.created_at.asc(), UserPermission.id.asc())
            .all()
        )

    @staticmethod
    def _is_permission_active(permission: UserPermission) -> bool:
        if permission.status != 1:
            return False
        if permission.expire_at and permission.expire_at < datetime.now():
            return False
        return True

    def reserve_permission(self, user_id: int, permission_type: str, count: int = 1) -> Optional[list[tuple[int, int]]]:
        permissions = [
            permission
            for permission in self._get_permissions_for_type(user_id, permission_type)
            if self._is_permission_active(permission)
        ]
        if not permissions:
            return None

        subscription = next((permission for permission in permissions if permission.payment_mode != "per_use"), None)
        if subscription:
            return []

        remaining = sum(max(0, permission.total_count - permission.used_count) for permission in permissions)
        if remaining < count:
            return None

        allocations: list[tuple[int, int]] = []
        remaining_to_consume = count
        for permission in permissions:
            row_remaining = max(0, permission.total_count - permission.used_count)
            if row_remaining <= 0:
                continue
            consume = min(remaining_to_consume, row_remaining)
            permission.used_count += consume
            allocations.append((permission.id, consume))
            remaining_to_consume -= consume
            if remaining_to_consume <= 0:
                break

        self.db.commit()
        return allocations

    def release_permission_allocations(self, allocations: list[tuple[int, int]]) -> bool:
        if not allocations:
            return True

        permission_ids = [permission_id for permission_id, _ in allocations]
        permission_map = {
            permission.id: permission
            for permission in self.db.query(UserPermission).filter(UserPermission.id.in_(permission_ids)).all()
        }
        for permission_id, count in allocations:
            permission = permission_map.get(permission_id)
            if not permission:
                continue
            permission.used_count = max(0, permission.used_count - count)

        self.db.commit()
        return True

    def check_permission(
        self,
        user_id: int,
        permission_type: str,
        required_count: int = 1,
        with_message: bool = False,
    ):
        permissions = [
            permission
            for permission in self._get_permissions_for_type(user_id, permission_type)
            if self._is_permission_active(permission)
        ]
        if not permissions:
            result = (False, f"Permission {permission_type} is not enabled")
            return result if with_message else result[0]

        if any(permission.payment_mode != "per_use" for permission in permissions):
            result = (True, "Permission is valid")
            return result if with_message else result[0]

        remaining = sum(max(0, permission.total_count - permission.used_count) for permission in permissions)
        if remaining < required_count:
            result = (False, f"Insufficient usage count, remaining {remaining}")
            return result if with_message else result[0]

        result = (True, "Permission is valid")
        return result if with_message else result[0]

    def use_permission(self, user_id: int, permission_type: str, count: int = 1) -> bool:
        allocations = self.reserve_permission(user_id, permission_type, count)
        return allocations is not None

    def release_permission(self, user_id: int, permission_type: str, count: int = 1) -> bool:
        permissions = list(reversed(self._get_permissions_for_type(user_id, permission_type)))
        if not permissions:
            return False

        if any(permission.payment_mode != "per_use" and self._is_permission_active(permission) for permission in permissions):
            return True

        remaining_to_release = count
        for permission in permissions:
            if permission.payment_mode != "per_use":
                continue
            releasable = min(permission.used_count, remaining_to_release)
            if releasable <= 0:
                continue
            permission.used_count = max(0, permission.used_count - releasable)
            remaining_to_release -= releasable
            if remaining_to_release <= 0:
                break

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

    @staticmethod
    def _build_price_config_key(permission_type: str, payment_mode: str) -> str:
        return f"{permission_type}_price_{payment_mode}"

    @staticmethod
    def _decimal_to_config_value(value: Decimal) -> str:
        text = format(value.quantize(Decimal("0.01")), "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text or "0"

    def get_permission_prices(self) -> PermissionPriceTable:
        keys = [
            self._build_price_config_key(permission_type, payment_mode)
            for permission_type in self.PERMISSION_TYPES
            for payment_mode in self.PAYMENT_MODES
        ]
        config_values = self.system_config_service.get_values(keys)

        result: PermissionPriceTable = {}
        for permission_type in self.PERMISSION_TYPES:
            result[permission_type] = {}
            for payment_mode in self.PAYMENT_MODES:
                key = self._build_price_config_key(permission_type, payment_mode)
                default_value = self.DEFAULT_PERMISSION_PRICES[permission_type][payment_mode]
                raw = config_values.get(key)

                if raw is None:
                    result[permission_type][payment_mode] = default_value
                    continue

                try:
                    value = Decimal(str(raw))
                    if value < 0:
                        raise InvalidOperation
                    result[permission_type][payment_mode] = value
                except (InvalidOperation, ValueError, TypeError):
                    result[permission_type][payment_mode] = default_value

        return result

    def normalize_permission_prices(self, prices: dict) -> PermissionPriceTable:
        if not isinstance(prices, dict):
            raise BadRequestException(detail="Invalid price payload")

        normalized: PermissionPriceTable = {}

        for permission_type in self.PERMISSION_TYPES:
            mode_values = prices.get(permission_type)
            if not isinstance(mode_values, dict):
                raise BadRequestException(detail=f"Missing pricing section: {permission_type}")

            normalized[permission_type] = {}
            for payment_mode in self.PAYMENT_MODES:
                raw_value = mode_values.get(payment_mode)
                if raw_value is None:
                    raise BadRequestException(
                        detail=f"Missing pricing value: {permission_type}.{payment_mode}"
                    )

                try:
                    value = Decimal(str(raw_value))
                except (InvalidOperation, ValueError, TypeError):
                    raise BadRequestException(
                        detail=f"Invalid pricing value: {permission_type}.{payment_mode}"
                    )

                if value < 0:
                    raise BadRequestException(
                        detail=f"Pricing value must be non-negative: {permission_type}.{payment_mode}"
                    )

                normalized[permission_type][payment_mode] = value.quantize(Decimal("0.01"))

        return normalized

    def save_permission_prices(self, prices: PermissionPriceTable) -> None:
        values: Dict[str, str] = {}
        descriptions: Dict[str, str] = {}

        for permission_type, mode_values in prices.items():
            for payment_mode, value in mode_values.items():
                key = self._build_price_config_key(permission_type, payment_mode)
                values[key] = self._decimal_to_config_value(value)
                descriptions[key] = self.PRICE_DESCRIPTIONS.get(key, "Permission pricing config")

        self.system_config_service.set_values(values, descriptions)

    def get_permission_price(self, permission_type: str, payment_mode: str) -> Decimal:
        prices = self.get_permission_prices()
        return prices.get(permission_type, {}).get(payment_mode, Decimal("0"))
