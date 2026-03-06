"""Redis cache service."""

from __future__ import annotations

import json
from typing import Any, Optional

from app.utils.redis import redis_client


class CacheService:
    def __init__(self):
        self.redis = redis_client
        self.default_ttl = 3600

    @staticmethod
    def _serialize(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, default=str)

    @staticmethod
    def _deserialize(value: str) -> Any:
        return json.loads(value)

    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            return self._deserialize(value)
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        try:
            ttl = ttl or self.default_ttl
            self.redis.setex(key, ttl, self._serialize(value))
            return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        try:
            self.redis.delete(key)
            return True
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        try:
            return self.redis.exists(key) > 0
        except Exception:
            return False

    def clear_pattern(self, pattern: str) -> int:
        try:
            keys = list(self.redis.scan_iter(match=pattern, count=1000))
            if not keys:
                return 0
            return int(self.redis.delete(*keys))
        except Exception:
            return 0

    def get_coupon(self, coupon_code: str) -> Optional[dict]:
        return self.get(f"coupon:{coupon_code}")

    def set_coupon(self, coupon_code: str, coupon_data: dict, ttl: int = 1800) -> bool:
        return self.set(f"coupon:{coupon_code}", coupon_data, ttl)

    def delete_coupon(self, coupon_code: str) -> bool:
        return self.delete(f"coupon:{coupon_code}")

    def get_user_permissions(self, user_id: int) -> Optional[list]:
        return self.get(f"user_permissions:{user_id}")

    def set_user_permissions(self, user_id: int, permissions: list, ttl: int = 600) -> bool:
        return self.set(f"user_permissions:{user_id}", permissions, ttl)

    def delete_user_permissions(self, user_id: int) -> bool:
        return self.delete(f"user_permissions:{user_id}")

    def get_gallery(self, page: int, work_type: str | None = None) -> Optional[list]:
        key = f"gallery:{work_type or 'all'}:{page}"
        return self.get(key)

    def set_gallery(self, page: int, works: list, work_type: str | None = None, ttl: int = 300) -> bool:
        key = f"gallery:{work_type or 'all'}:{page}"
        return self.set(key, works, ttl)

    def clear_gallery_cache(self) -> int:
        return self.clear_pattern("gallery:*")

    def get_stats(self, stats_type: str) -> Optional[dict]:
        return self.get(f"stats:{stats_type}")

    def set_stats(self, stats_type: str, stats_data: dict, ttl: int = 300) -> bool:
        return self.set(f"stats:{stats_type}", stats_data, ttl)

    def increment_rate_limit(self, key: str, ttl: int = 60) -> int:
        try:
            count = self.redis.incr(key)
            if count == 1:
                self.redis.expire(key, ttl)
            return int(count)
        except Exception:
            return 0

    def get_rate_limit(self, key: str) -> int:
        try:
            count = self.redis.get(key)
            return int(count) if count else 0
        except Exception:
            return 0


cache_service = CacheService()
