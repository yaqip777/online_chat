from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.service import AuthService
from backend.database import get_db
from backend.stories.schemes.post import StoryResponseSchema
from backend.stories.service import StoryService

router = APIRouter(prefix="/stories", tags=["Stories"])

IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]
VIDEO_EXTENSIONS = [".mp4", ".mov", ".mkv"]

MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 50 * 1024 * 1024


@router.post("/", response_model=StoryResponseSchema)
async def create_story(
    image: UploadFile | None = File(None),
    video: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    if not image and not video:
        raise HTTPException(
            status_code=400,
            detail="Story uchun rasm yoki video kerak",
        )

    if image and image.filename:
        file_ext = image.filename[image.filename.rfind(".") :].lower()
        if file_ext not in IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Faqat rasm formatidagi fayllar yuklanishi mumkin!",
            )

        image_content = await image.read()
        if len(image_content) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="Rasm hajmi 10 MB dan oshmasligi kerak!",
            )
        await image.seek(0)

    if video and video.filename:
        file_ext = video.filename[video.filename.rfind(".") :].lower()
        if file_ext not in VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Faqat video formatidagi fayllar yuklanishi mumkin!",
            )

        video_content = await video.read()
        if len(video_content) > MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=400,
                detail="Video hajmi 50 MB dan oshmasligi kerak!",
            )
        await video.seek(0)

    return await StoryService.create_story(
        db=db, user_id=current_user.id, image=image, video=video
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
