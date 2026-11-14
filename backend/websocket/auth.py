import jwt
from fastapi import WebSocket, WebSocketException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.models import User
from backend.config import settings


async def get_current_user_ws(websocket: WebSocket, db: AsyncSession) -> User:
    # Tokenni query parametr yoki headers orqali olish
    token = websocket.query_params.get("token")
    if not token:
        # Ba'zi mijozlar Authorization header orqali yuborishi mumkin
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Autentifikatsiya tokeni topilmadi",
        )

    try:
        payload = jwt.decode(
            token, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("email")
        if email is None:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Yaroqsiz token ma'lumotlari",
            )
    except jwt.PyJWTError:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Yaroqsiz yoki muddati o'tgan token",
        )

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Foydalanuvchi topilmadi",
        )

    return user
