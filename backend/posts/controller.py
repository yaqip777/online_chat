from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.auth.service import AuthService
from backend.posts.service import PostService
from backend.posts.schemes.post import PostResponseSchema

router = APIRouter(prefix="/posts", tags=["Posts"])

IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv"]

MAX_IMAGE_SIZE = 10 * 1024 * 1024  
MAX_VIDEO_SIZE = 50 * 1024 * 1024  

@router.post("/", response_model=PostResponseSchema)
async def create_post(
    text: str | None = Form(None),
    image: UploadFile | None = File(None),
    video: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(AuthService.get_current_user)
):
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
                detail="Rasm hajmi 5 MB dan oshmasligi kerak!",
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

    return await PostService.create_post(
        db=db, 
        user_id=current_user.id, 
        text=text, 
        image=image, 
        video=video
    )

@router.get("/", response_model=list[PostResponseSchema])
async def get_posts(
    cursor: datetime | None = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    return await PostService.get_posts_paginated(db=db, cursor=cursor, limit=limit)