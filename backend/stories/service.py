import os
import shutil
from datetime import datetime, timezone
 
from fastapi import UploadFile
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
 
from backend.stories.models import Story
 
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
 
 
class StoryService:
    @staticmethod
    async def create_story(
        db: AsyncSession,
        user_id: int,
        image: UploadFile | None = None,
        video: UploadFile | None = None,
    ) -> Story:
        image_url = None
        video_url = None
 
        if image:
            image_path = os.path.join(
                UPLOAD_DIR, f"story_img_{datetime.now().timestamp()}_{image.filename}"
            )
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_url = os.path.basename(image_path)
 
        if video:
            video_path = os.path.join(
                UPLOAD_DIR, f"story_vid_{datetime.now().timestamp()}_{video.filename}"
            )
            with open(video_path, "wb") as buffer:
                shutil.copyfileobj(video.file, buffer)
            video_url = os.path.basename(video_path)
 
        new_story = Story(user_id=user_id, image_url=image_url, video_url=video_url)
        db.add(new_story)
        await db.commit()
        await db.refresh(new_story)
        return new_story
 
    @staticmethod
    async def get_active_stories_paginated(
        db: AsyncSession,
        cursor: datetime | None = None,
        limit: int = 20,
    ) -> list[Story]:
        now = datetime.utcnow()
        query = select(Story).where(Story.expires_at > now)
 
        if cursor:
            if cursor.tzinfo is not None:
                cursor = cursor.astimezone(timezone.utc).replace(tzinfo=None)
            query = query.filter(Story.created_at < cursor)
 
        query = query.order_by(Story.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
 
    @staticmethod
    async def get_user_active_stories(db: AsyncSession, user_id: int) -> list[Story]:
        now = datetime.utcnow()
        query = (
            select(Story)
            .where(Story.user_id == user_id, Story.expires_at > now)
            .order_by(Story.created_at.desc())
        )
        result = await db.execute(query)
        return result.scalars().all()
