from datetime import datetime
import os
from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.service import AuthService
from backend.chat.schemes.post import (
    ConversationResponseSchema,
    MessageResponseSchema,
)
from backend.chat.service import ChatService
from backend.config import settings
from backend.database import get_db

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/messages", response_model=MessageResponseSchema)
async def send_message(
    user_id: int = Form(...),
    text: str | None = Form(None),
    image: UploadFile | None = File(None),
    video: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="O'zingizga xabar yubora olmaysiz"
        )

    receiver_exists = await ChatService.user_exists(db, user_id)
    if not receiver_exists:
        raise HTTPException(
            status_code=404,
            detail=f"ID={user_id} bo'lgan foydalanuvchi topilmadi",
        )

    has_text = text is not None and text.strip() != ""
    has_image = bool(image and image.filename)
    has_video = bool(video and video.filename)

    if not has_text and not has_image and not has_video:
        raise HTTPException(
            status_code=400,
            detail="Xabar uchun matn, rasm yoki video kamida bittasi kerak!",
        )

    if has_image:
        file_ext = os.path.splitext(image.filename)[1].lower()
        if file_ext not in settings.IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Faqat quyidagi rasm formatlari qabul qilinadi: {', '.join(settings.IMAGE_EXTENSIONS)}",
            )
        image_content = await image.read()
        if len(image_content) > settings.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Rasm hajmi {settings.MAX_IMAGE_SIZE // (1024 * 1024)} MB dan oshmasligi kerak!",
            )
        await image.seek(0)

    if has_video:
        file_ext = os.path.splitext(video.filename)[1].lower()
        if file_ext not in settings.VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Faqat quyidagi video formatlari qabul qilinadi: {', '.join(settings.VIDEO_EXTENSIONS)}",
            )
        video_content = await video.read()
        if len(video_content) > settings.MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Video hajmi {settings.MAX_VIDEO_SIZE // (1024 * 1024)} MB dan oshmasligi kerak!",
            )
        await video.seek(0)

    return await ChatService.send_message(
        db=db,
        sender_id=current_user.id,
        receiver_id=user_id,
        text=text,
        image=image if has_image else None,
        video=video if has_video else None,
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
    conversation_id: int = Path(...),
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
