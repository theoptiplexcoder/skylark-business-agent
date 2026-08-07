"""In-memory cache with TTL for Monday API responses."""

import time
import threading
from typing import Any, Optional
from functools import wraps

_DEFAULT_TTL = 300  # 5 minutes


class TTLCache:
    """Thread-safe in-memory cache with time-to-live expiration."""

    def __init__(self, default_ttl: int = _DEFAULT_TTL):
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._store:
                expires_at, value = self._store[key]
                if time.time() < expires_at:
                    return value
                del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl: int = None) -> None:
        expires_at = time.time() + (ttl or self._default_ttl)
        with self._lock:
            self._store[key] = (expires_at, value)

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def cleanup(self) -> int:
        """Remove expired entries. Returns count removed."""
        now = time.time()
        removed = 0
        with self._lock:
            expired = [k for k, (exp, _) in self._store.items() if now >= exp]
            for k in expired:
                del self._store[k]
                removed += 1
        return removed

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._store)


cache = TTLCache()


def cached(ttl: int = _DEFAULT_TTL, prefix: str = ""):
    """Decorator for caching async function results."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key_parts = [prefix or func.__name__]
            for arg in args:
                if hasattr(arg, "__dict__"):
                    continue
                key_parts.append(str(arg))
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
            cache_key = ":".join(key_parts)

            result = cache.get(cache_key)
            if result is not None:
                return result

            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result

        wrapper.invalidate = lambda *a, **kw: cache.clear()
        return wrapper

    return decorator
