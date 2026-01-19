"""
Redis используется как ОПЦИОНАЛЬНЫЙ кэш.
Мы кэшируем список активных правил, чтобы не ходить в БД каждый раз.
При изменении rules — инвалидируем ключ.
"""

import json
import redis
from app.core.config import REDIS_HOST, REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

ACTIVE_RULES_KEY = "active_rules_v1"

def cache_get_active_rules():
    raw = r.get(ACTIVE_RULES_KEY)
    return json.loads(raw) if raw else None

def cache_set_active_rules(rules: list[dict], ttl_seconds: int = 30):
    r.setex(ACTIVE_RULES_KEY, ttl_seconds, json.dumps(rules))

def cache_invalidate_active_rules():
    r.delete(ACTIVE_RULES_KEY)
