from __future__ import annotations

import fnmatch
import json
import threading
import time
from typing import Any, Optional

import redis

from app.core.config import settings


class RedisClient:
    def __init__(self):
        self._lock = threading.RLock()
        self._memory_mode = False
        self._kv: dict[str, Any] = {}
        self._expire_at: dict[str, float] = {}
        self._lists: dict[str, list[Any]] = {}
        self._hashes: dict[str, dict[str, Any]] = {}
        self.client = None

        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=0.2,
                socket_timeout=0.2,
                retry_on_timeout=False,
            )
            self.client.ping()
        except Exception:
            self._memory_mode = True
            self.client = None

    def _cleanup_expired(self, key: str):
        expire = self._expire_at.get(key)
        if expire is not None and expire <= time.time():
            self._kv.pop(key, None)
            self._expire_at.pop(key, None)

    @staticmethod
    def _to_storage(value: Any) -> Any:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return value

    @staticmethod
    def _from_storage(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        value = self._to_storage(value)
        if not self._memory_mode and self.client:
            try:
                return bool(self.client.set(key, value, ex=ex))
            except Exception:
                pass

        with self._lock:
            self._kv[key] = value
            if ex is not None:
                self._expire_at[key] = time.time() + ex
            else:
                self._expire_at.pop(key, None)
        return True

    def setex(self, key: str, ex: int, value: Any) -> bool:
        return self.set(key, value, ex=ex)

    def get(self, key: str) -> Optional[Any]:
        if not self._memory_mode and self.client:
            try:
                value = self.client.get(key)
                return self._from_storage(value)
            except Exception:
                pass

        with self._lock:
            self._cleanup_expired(key)
            return self._from_storage(self._kv.get(key))

    def delete(self, *keys: str) -> int:
        if not keys:
            return 0

        if not self._memory_mode and self.client:
            try:
                return int(self.client.delete(*keys))
            except Exception:
                pass

        removed = 0
        with self._lock:
            for key in keys:
                if key in self._kv:
                    removed += 1
                self._kv.pop(key, None)
                self._expire_at.pop(key, None)
                self._lists.pop(key, None)
                self._hashes.pop(key, None)
        return removed

    def exists(self, key: str) -> int:
        if not self._memory_mode and self.client:
            try:
                return int(self.client.exists(key))
            except Exception:
                pass

        with self._lock:
            self._cleanup_expired(key)
            return 1 if key in self._kv else 0

    def expire(self, key: str, seconds: int) -> bool:
        if not self._memory_mode and self.client:
            try:
                return bool(self.client.expire(key, seconds))
            except Exception:
                pass

        with self._lock:
            if key not in self._kv:
                return False
            self._expire_at[key] = time.time() + seconds
            return True

    def ttl(self, key: str) -> int:
        if not self._memory_mode and self.client:
            try:
                return int(self.client.ttl(key))
            except Exception:
                pass

        with self._lock:
            self._cleanup_expired(key)
            expire = self._expire_at.get(key)
            if key not in self._kv:
                return -2
            if expire is None:
                return -1
            return max(0, int(expire - time.time()))

    def incr(self, key: str) -> int:
        if not self._memory_mode and self.client:
            try:
                return int(self.client.incr(key))
            except Exception:
                pass

        with self._lock:
            self._cleanup_expired(key)
            current = self._kv.get(key, 0)
            try:
                number = int(current)
            except Exception:
                number = 0
            number += 1
            self._kv[key] = number
            return number

    def decr(self, key: str) -> int:
        if not self._memory_mode and self.client:
            try:
                return int(self.client.decr(key))
            except Exception:
                pass

        with self._lock:
            self._cleanup_expired(key)
            current = self._kv.get(key, 0)
            try:
                number = int(current)
            except Exception:
                number = 0
            number -= 1
            self._kv[key] = number
            return number

    def lpush(self, key: str, value: Any) -> int:
        value = self._to_storage(value)
        if not self._memory_mode and self.client:
            try:
                return int(self.client.lpush(key, value))
            except Exception:
                pass

        with self._lock:
            self._lists.setdefault(key, []).insert(0, value)
            return len(self._lists[key])

    def rpop(self, key: str) -> Optional[Any]:
        if not self._memory_mode and self.client:
            try:
                return self._from_storage(self.client.rpop(key))
            except Exception:
                pass

        with self._lock:
            queue = self._lists.get(key, [])
            if not queue:
                return None
            value = queue.pop()
            return self._from_storage(value)

    def llen(self, key: str) -> int:
        if not self._memory_mode and self.client:
            try:
                return int(self.client.llen(key))
            except Exception:
                pass

        with self._lock:
            return len(self._lists.get(key, []))

    def hset(self, name: str, key: str, value: Any) -> int:
        value = self._to_storage(value)
        if not self._memory_mode and self.client:
            try:
                return int(self.client.hset(name, key, value))
            except Exception:
                pass

        with self._lock:
            hash_obj = self._hashes.setdefault(name, {})
            is_new = 0 if key in hash_obj else 1
            hash_obj[key] = value
            return is_new

    def hget(self, name: str, key: str) -> Optional[Any]:
        if not self._memory_mode and self.client:
            try:
                return self._from_storage(self.client.hget(name, key))
            except Exception:
                pass

        with self._lock:
            return self._from_storage(self._hashes.get(name, {}).get(key))

    def hgetall(self, name: str) -> dict:
        if not self._memory_mode and self.client:
            try:
                values = self.client.hgetall(name)
                return {k: self._from_storage(v) for k, v in values.items()}
            except Exception:
                pass

        with self._lock:
            return {
                k: self._from_storage(v)
                for k, v in self._hashes.get(name, {}).items()
            }

    def hdel(self, name: str, key: str) -> int:
        if not self._memory_mode and self.client:
            try:
                return int(self.client.hdel(name, key))
            except Exception:
                pass

        with self._lock:
            hash_obj = self._hashes.get(name, {})
            if key in hash_obj:
                del hash_obj[key]
                return 1
            return 0

    def scan_iter(self, match: str = "*", count: int = 1000):
        if not self._memory_mode and self.client:
            try:
                yield from self.client.scan_iter(match=match, count=count)
                return
            except Exception:
                pass

        with self._lock:
            keys = list(self._kv.keys())
        for key in keys:
            if fnmatch.fnmatch(key, match):
                yield key


redis_client = RedisClient()
# Backward-compatible alias used by existing tests/modules.
redis = redis_client

__all__ = ["RedisClient", "redis_client", "redis"]
