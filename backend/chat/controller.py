from datetime import datetime
 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
 
from backend.auth.service import AuthService
from backend.chat.schemes.post import (
    ConversationResponseSchema,
    MessageResponseSchema,
    SendMessageSchema,
)
from backend.chat.service import ChatService
from backend.database import get_db
 
router = APIRouter(prefix="/chat", tags=["Chat"])
 
 
@router.post("/messages", response_model=MessageResponseSchema)
async def send_message(
    data: SendMessageSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    if data.receiver_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="O'zingizga xabar yubora olmaysiz"
        )
 
    receiver_exists = await ChatService.user_exists(db, data.receiver_id)
    if not receiver_exists:
        raise HTTPException(
            status_code=404,
            detail=f"ID={data.receiver_id} bo'lgan foydalanuvchi topilmadi",
        )
 
    return await ChatService.send_message(
        db=db,
        sender_id=current_user.id,
        receiver_id=data.receiver_id,
        text=data.text,
    )
 
 
@router.get("/conversations", response_model=list[ConversationResponseSchema])
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    return await ChatService.get_user_conversations(db=db, user_id=current_user.id)
 
 
@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponseSchema],
)
async def get_messages(
    conversation_id: int,
    cursor: datetime | None = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    allowed = await ChatService.is_participant(db, conversation_id, current_user.id)
    if not allowed:
        raise HTTPException(
            status_code=403, detail="Bu suhbatga kirish huquqingiz yo'q"
        )
 
    return await ChatService.get_messages_paginated(
        db=db, conversation_id=conversation_id, cursor=cursor, limit=limit
    )