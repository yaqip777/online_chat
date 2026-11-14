from datetime import datetime
import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.service import AuthService
from backend.config import settings
from backend.database import get_db
from backend.stories.schemes.post import StoryResponseSchema
from backend.stories.service import StoryService

router = APIRouter(prefix="/stories", tags=["Stories"])


@router.post("/", response_model=StoryResponseSchema)
async def create_story(
    image: UploadFile | None = File(None),
    video: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    has_image = bool(image and image.filename)
    has_video = bool(video and video.filename)

    if not has_image and not has_video:
        raise HTTPException(
            status_code=400,
            detail="Story uchun rasm yoki video fayl yuklanishi shart!",
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

    return await StoryService.create_story(
        db=db,
        user_id=current_user.id,
        image=image if has_image else None,
        video=video if has_video else None,
    )


@router.get("/", response_model=list[StoryResponseSchema])
async def get_active_stories(
    cursor: datetime | None = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await StoryService.get_active_stories_paginated(
        db=db, cursor=cursor, limit=limit
    )


@router.get("/user/{user_id}", response_model=list[StoryResponseSchema])
async def get_user_stories(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await StoryService.get_user_active_stories(db=db, user_id=user_id)


@router.delete("/{story_id}")
async def delete_story(
    story_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    await StoryService.delete_story(db=db, story_id=story_id, user_id=current_user.id)
    return {"message": "Story muvaffaqiyatli o'chirildi"}
