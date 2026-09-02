import asyncio
import json
import uuid
from contextlib import suppress

from app.core.redis import get_redis
from app.ws.manager import manager

CHANNEL_PREFIX = "shopping:list:"


def _channel(list_id: uuid.UUID) -> str:
    return f"{CHANNEL_PREFIX}{list_id}"


async def publish_list_event(list_id: uuid.UUID, event_type: str, data: dict) -> None:
    """Publish a realtime event for a list. Every API instance subscribed to this
    channel (see `listen_and_forward`) rebroadcasts it to its own local WebSocket
    connections, so this is the one call site services need for realtime fanout."""
    redis = get_redis()
    message = {"type": event_type, "list_id": str(list_id), "data": data}
    await redis.publish(_channel(list_id), json.dumps(message, default=str))


async def listen_and_forward(list_id: uuid.UUID, stop_event: asyncio.Event) -> None:
    """Subscribe this process to a list's channel and forward messages to local
    WebSocket connections until `stop_event` is set (called once per list per
    process, when the first local subscriber connects)."""
    redis = get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(_channel(list_id))
    try:
        while not stop_event.is_set():
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is None:
                continue
            with suppress(Exception):
                payload = json.loads(message["data"])
                await manager.broadcast_local(list_id, payload)
    finally:
        with suppress(Exception):
            await pubsub.unsubscribe(_channel(list_id))
            await pubsub.aclose()
