import os
import shutil
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.stories.models import Story


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _save_file(upload: UploadFile, prefix: str) -> str:
    file_ext = os.path.splitext(upload.filename)[1].lower() if upload.filename else ""
    safe_name = f"{prefix}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}{file_ext}"
    path = settings.UPLOAD_DIR / safe_name
    with open(path, "wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return safe_name


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

        if image and image.filename:
            image_url = _save_file(image, "story_img")

        if video and video.filename:
            video_url = _save_file(video, "story_vid")

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
        now = _utcnow()
        query = select(Story).where(Story.expires_at > now)

        if cursor:
            if cursor.tzinfo is not None:
                cursor = cursor.astimezone(timezone.utc).replace(tzinfo=None)
            query = query.filter(Story.created_at < cursor)

        query = query.order_by(Story.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_user_active_stories(db: AsyncSession, user_id: int) -> list[Story]:
        now = _utcnow()
        query = (
            select(Story)
            .where(Story.user_id == user_id, Story.expires_at > now)
            .order_by(Story.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def delete_story(db: AsyncSession, story_id: int, user_id: int) -> None:
        result = await db.execute(select(Story).where(Story.id == story_id))
        story = result.scalar_one_or_none()
        if story is None:
            raise HTTPException(status_code=404, detail="Story topilmadi")

        if story.user_id != user_id:
            raise HTTPException(status_code=403, detail="Faqat o'zingizning storyingizni o'chira olasiz")

        if story.image_url:
            img_path = settings.UPLOAD_DIR / story.image_url
            if img_path.exists() and img_path.is_file():
                try:
                    img_path.unlink()
                except OSError:
                    pass

        if story.video_url:
            vid_path = settings.UPLOAD_DIR / story.video_url
            if vid_path.exists() and vid_path.is_file():
                try:
                    vid_path.unlink()
                except OSError:
                    pass

        await db.delete(story)
        await db.commit()
