import os
import shutil
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.posts.models import Post
from datetime import datetime, timezone

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class PostService:
    @staticmethod
    async def create_post(
        db: AsyncSession, 
        user_id: int, 
        text: str | None = None, 
        image: UploadFile | None = None, 
        video: UploadFile | None = None
    ) -> Post:
        image_url = None
        video_url = None

        if image:
            image_path = os.path.join(UPLOAD_DIR, f"img_{datetime.now().timestamp()}_{image.filename}")
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_url = f"/{image_path}"

        if video:
            video_path = os.path.join(UPLOAD_DIR, f"vid_{datetime.now().timestamp()}_{video.filename}")
            with open(video_path, "wb") as buffer:
                shutil.copyfileobj(video.file, buffer)
            video_url = f"/{video_path}"

        new_post = Post(
            text=text,
            image_url=image_url,
            video_url=video_url,
            user_id=user_id
        )
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)
        return new_post


    @staticmethod
    async def get_posts_paginated(
        db: AsyncSession, 
        cursor: datetime | None = None, 
        limit: int = 10
    ) -> list[Post]:
        query = select(Post)
        
        if cursor:
            if cursor.tzinfo is not None:
                cursor = cursor.astimezone(timezone.utc).replace(tzinfo=None)
                
            query = query.filter(Post.created_at < cursor)

        query = query.order_by(Post.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()