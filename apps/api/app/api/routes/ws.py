import asyncio
import uuid

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import decode_token
from app.db.session import async_session_factory
from app.models.enums import ListRole
from app.models.user import User
from app.services.authz import get_list_or_404, resolve_role
from app.ws.manager import manager
from app.ws.redis_pubsub import listen_and_forward

router = APIRouter(tags=["websocket"])

_listener_tasks: dict[uuid.UUID, tuple[asyncio.Task, asyncio.Event, int]] = {}


async def _ensure_listener(list_id: uuid.UUID) -> None:
    entry = _listener_tasks.get(list_id)
    if entry is None:
        stop_event = asyncio.Event()
        task = asyncio.create_task(listen_and_forward(list_id, stop_event))
        _listener_tasks[list_id] = (task, stop_event, 1)
    else:
        task, stop_event, count = entry
        _listener_tasks[list_id] = (task, stop_event, count + 1)


async def _release_listener(list_id: uuid.UUID) -> None:
    entry = _listener_tasks.get(list_id)
    if entry is None:
        return
    task, stop_event, count = entry
    if count <= 1:
        stop_event.set()
        _listener_tasks.pop(list_id, None)
    else:
        _listener_tasks[list_id] = (task, stop_event, count - 1)


@router.websocket("/ws/lists/{list_id}")
async def list_websocket(websocket: WebSocket, list_id: uuid.UUID, token: str = Query(...)) -> None:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise ValueError("invalid_token_type")
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, KeyError):
        await websocket.close(code=4401)
        return

    async with async_session_factory() as db:
        try:
            shopping_list = await get_list_or_404(db, list_id)
        except Exception:
            await websocket.close(code=4404)
            return
        role = await resolve_role(db, shopping_list, user_id)
        if role is None:
            await websocket.close(code=4403)
            return
        user = await db.get(User, user_id)

    await manager.connect(list_id, websocket)
    await _ensure_listener(list_id)
    manager.set_presence(list_id, user_id, user.name if user else str(user_id))
    await websocket.send_json({"type": "CONNECTED", "list_id": str(list_id), "role": role.value})

    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "PING":
                await websocket.send_json({"type": "PONG"})
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(list_id, websocket)
        manager.clear_presence(list_id, user_id)
        await _release_listener(list_id)
