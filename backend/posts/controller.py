from datetime import datetime
import os
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.service import AuthService
from backend.config import settings
from backend.database import get_db
from backend.posts.schemes.post import PostResponseSchema
from backend.posts.service import PostService

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=PostResponseSchema)
async def create_post(
    text: str | None = Form(None),
    image: UploadFile | None = File(None),
    video: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    has_text = text is not None and text.strip() != ""
    has_image = bool(image and image.filename)
    has_video = bool(video and video.filename)

    if not has_text and not has_image and not has_video:
        raise HTTPException(
            status_code=400,
            detail="Post uchun matn, rasm yoki video kamida bittasi kerak!",
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

    return await PostService.create_post(
        db=db,
        user_id=current_user.id,
        text=text,
        image=image if has_image else None,
        video=video if has_video else None,
    )


@router.get("/", response_model=list[PostResponseSchema])
async def get_posts(
    cursor: datetime | None = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user_optional),
):
    current_user_id = current_user.id if current_user else None
    return await PostService.get_posts_paginated(
        db=db, cursor=cursor, limit=limit, current_user_id=current_user_id
    )


@router.get("/{post_id}", response_model=PostResponseSchema)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user_optional),
):
    current_user_id = current_user.id if current_user else None
    return await PostService.get_post_by_id(
        db=db, post_id=post_id, current_user_id=current_user_id
    )


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    await PostService.delete_post(db=db, post_id=post_id, user_id=current_user.id)
    return {"message": "Post muvaffaqiyatli o'chirildi"}


@router.post("/{post_id}/like")
async def like_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    await PostService.like_post(db=db, user_id=current_user.id, post_id=post_id)
    return {"message": "Layk qo'yildi"}


@router.delete("/{post_id}/like")
async def unlike_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    await PostService.unlike_post(db=db, user_id=current_user.id, post_id=post_id)
    return {"message": "Layk olib tashlandi"}
