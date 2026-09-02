import json
import uuid
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """Local (per-process) registry of open WebSocket connections, keyed by list id.

    Real fanout across multiple API instances happens over Redis pub/sub
    (see app.ws.redis_pubsub) — this class only tracks sockets local to this process.
    """

    def __init__(self) -> None:
        self._connections: dict[uuid.UUID, set[WebSocket]] = defaultdict(set)
        self._presence: dict[uuid.UUID, dict[uuid.UUID, str]] = defaultdict(dict)

    async def connect(self, list_id: uuid.UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[list_id].add(websocket)

    def disconnect(self, list_id: uuid.UUID, websocket: WebSocket) -> None:
        self._connections[list_id].discard(websocket)
        if not self._connections[list_id]:
            self._connections.pop(list_id, None)

    def set_presence(self, list_id: uuid.UUID, user_id: uuid.UUID, name: str) -> None:
        self._presence[list_id][user_id] = name

    def clear_presence(self, list_id: uuid.UUID, user_id: uuid.UUID) -> None:
        self._presence[list_id].pop(user_id, None)

    def presence(self, list_id: uuid.UUID) -> dict[str, str]:
        return {str(k): v for k, v in self._presence[list_id].items()}

    async def broadcast_local(self, list_id: uuid.UUID, message: dict) -> None:
        dead: list[WebSocket] = []
        payload = json.dumps(message, default=str)
        for connection in self._connections.get(list_id, set()):
            try:
                await connection.send_text(payload)
            except Exception:
                dead.append(connection)
        for connection in dead:
            self.disconnect(list_id, connection)


manager = ConnectionManager()
