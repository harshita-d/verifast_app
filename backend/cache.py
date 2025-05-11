from __future__ import annotations

import asyncio
import json
import os
from typing import List, Dict

import redis.asyncio as redis
from redis.exceptions import ConnectionError, RedisError

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_KEY = "session:{sid}"          # key template  e.g. session:demo

_conn: redis.Redis | None = None


async def _init_real() -> redis.Redis | None:
    conn = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        await conn.ping()
        print(f"[cache] Connected to Redis @ {REDIS_URL}")
        return conn
    except (ConnectionError, RedisError):
        return None


async def _init_fake() -> redis.Redis:
    import fakeredis.aioredis as faker
    print("[cache] Using fakeredis in-memory store (no external Redis running)")
    return faker.FakeRedis(decode_responses=True)


async def _get_conn() -> redis.Redis:
    global _conn
    if _conn is None:
        _conn = await _init_real() or await _init_fake()
    return _conn


async def push(session_id: str, role: str, content: str) -> None:
    r = await _get_conn()
    key = _KEY.format(sid=session_id)
    await r.rpush(key, json.dumps({"role": role, "content": content}))
    await r.expire(key, 86_400)          # 24 h TTL


async def history(session_id: str) -> List[Dict]:
    r = await _get_conn()
    raw = await r.lrange(_KEY.format(sid=session_id), 0, -1)
    return [json.loads(x) for x in raw]


async def clear(session_id: str) -> None:
    r = await _get_conn()
    await r.delete(_KEY.format(sid=session_id))


if __name__ == "__main__":

    async def _demo():
        await push("demo", "user", "Hi!")
        await push("demo", "assistant", "Hello")
        print("History:", await history("demo"))
        await clear("demo")
        print("After clear:", await history("demo"))

    asyncio.run(_demo())
