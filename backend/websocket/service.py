import logging
from fastapi import WebSocket

from backend.websocket.schemes.post import SignalMessage

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        # Har bir user_id uchun WebSocket ulanishlar to'plami (set)
        # Bu foydalanuvchi bir vaqtning o'zida telefon va kompyuterdan kirganda ham to'g'ri ishlashini ta'minlaydi
        self.active_connections: dict[int, set[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket | None = None) -> None:
        if user_id in self.active_connections:
            if websocket is not None:
                self.active_connections[user_id].discard(websocket)
            else:
                self.active_connections[user_id].clear()

            # Agar bu foydalanuvchida boshqa ulanish qolmasa, tozalab tashlaymiz
            if not self.active_connections[user_id]:
                self.active_connections.pop(user_id, None)

    def is_online(self, user_id: int) -> bool:
        return bool(self.active_connections.get(user_id))

    async def send_to_user(self, user_id: int, message: dict) -> bool:
        sockets = self.active_connections.get(user_id)
        if not sockets:
            return False

        disconnected = []
        sent_any = False

        for ws in list(sockets):
            try:
                await ws.send_json(message)
                sent_any = True
            except Exception as e:
                logger.warning(f"Error sending to user {user_id}: {e}")
                disconnected.append(ws)

        for ws in disconnected:
            self.disconnect(user_id, ws)

        return sent_any


manager = ConnectionManager()


class VideoCallService:
    @staticmethod
    async def connect_user(user_id: int, websocket: WebSocket) -> None:
        await manager.connect(user_id, websocket)

    @staticmethod
    def disconnect_user(user_id: int, websocket: WebSocket | None = None) -> None:
        manager.disconnect(user_id, websocket)

    @staticmethod
    async def relay_signal(from_user_id: int, message: SignalMessage) -> bool:
        return await manager.send_to_user(
            message.to_user_id,
            {
                "type": message.type,
                "from_user_id": from_user_id,
                "payload": message.payload,
            },
        )
