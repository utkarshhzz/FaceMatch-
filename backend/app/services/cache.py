"""
Optional Redis cache. The app MUST still work if Redis is down, so every
method swallows connection errors and degrades to "no cache".

Concept — why cache embeddings:
  At match time we read ALL embeddings from the DB every request. For a few
  hundred employees this is fine, but Redis can keep them in RAM (10-min TTL)
  to avoid repeated DB round-trips. We never rely on it for correctness —
  only for speed.
"""
import json
from typing import Optional

from app.core.config import settings
from app.core.logging import app_logger

_client = None
_unavailable = False


def _get_client():
    """Lazily connect to Redis; remember if it's unavailable so we don't
    retry on every request."""
    global _client, _unavailable
    if _unavailable:
        return None
    if _client is not None:
        return _client
    try:
        import redis  # type: ignore
        _client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        _client.ping()
        app_logger.info("Redis cache connected")
    except Exception as e:  # noqa: BLE001
        app_logger.warning("Redis unavailable, running without cache: {}", e)
        _client = None
        _unavailable = True
    return _client


def get_json(key: str) -> Optional[object]:
    c = _get_client()
    if not c:
        return None
    try:
        raw = c.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None


def set_json(key: str, value: object, ttl_seconds: int = 600) -> None:
    c = _get_client()
    if not c:
        return
    try:
        c.setex(key, ttl_seconds, json.dumps(value))
    except Exception:
        pass
