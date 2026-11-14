import os
import shutil
import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.config import settings
from backend.posts.models import Like, Post


def _save_file(upload: UploadFile, prefix: str) -> str:
    file_ext = os.path.splitext(upload.filename)[1].lower() if upload.filename else ""
    safe_name = f"{prefix}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}{file_ext}"
    path = settings.UPLOAD_DIR / safe_name
    with open(path, "wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return safe_name


class PostService:
    @staticmethod
    async def create_post(
        db: AsyncSession,
        user_id: int,
        text: str | None = None,
        image: UploadFile | None = None,
        video: UploadFile | None = None,
    ) -> Post:
        image_url = None
        video_url = None

        if image and image.filename:
            image_url = _save_file(image, "img")

        if video and video.filename:
            video_url = _save_file(video, "vid")

        new_post = Post(
            text=text,
            image_url=image_url,
            video_url=video_url,
            user_id=user_id,
        )
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)
        return new_post

    @staticmethod
    async def get_posts_paginated(
        db: AsyncSession,
        cursor: datetime | None = None,
        limit: int = 10,
        current_user_id: int | None = None,
    ) -> list[Post]:
        query = select(Post)

        if cursor:
            if cursor.tzinfo is not None:
                cursor = cursor.astimezone(timezone.utc).replace(tzinfo=None)
            query = query.filter(Post.created_at < cursor)

        query = query.order_by(Post.created_at.desc()).limit(limit)
        result = await db.execute(query)
        posts = list(result.scalars().all())

        if not posts:
            return posts

        post_ids = [post.id for post in posts]

        counts_result = await db.execute(
            select(Like.post_id, func.count(Like.id))
            .where(Like.post_id.in_(post_ids))
            .group_by(Like.post_id)
        )
        counts_map = dict(counts_result.all())

        liked_ids: set[int] = set()
        if current_user_id is not None:
            liked_result = await db.execute(
                select(Like.post_id).where(
                    Like.post_id.in_(post_ids), Like.user_id == current_user_id
                )
            )
            liked_ids = {row[0] for row in liked_result.all()}

        for post in posts:
            post.likes_count = counts_map.get(post.id, 0)
            post.liked_by_me = post.id in liked_ids

        return posts

    @staticmethod
    async def get_post_by_id(db: AsyncSession, post_id: int, current_user_id: int | None = None) -> Post:
        result = await db.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if post is None:
            raise HTTPException(status_code=404, detail="Post topilmadi")

        count_res = await db.execute(select(func.count(Like.id)).where(Like.post_id == post_id))
        post.likes_count = count_res.scalar() or 0

        if current_user_id is not None:
            liked_res = await db.execute(
                select(Like.id).where(Like.post_id == post_id, Like.user_id == current_user_id)
            )
            post.liked_by_me = liked_res.scalar_one_or_none() is not None
        else:
            post.liked_by_me = False

        return post

    @staticmethod
    async def delete_post(db: AsyncSession, post_id: int, user_id: int) -> None:
        result = await db.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if post is None:
            raise HTTPException(status_code=404, detail="Post topilmadi")

        if post.user_id != user_id:
            raise HTTPException(status_code=403, detail="Faqat o'zingizning postingizni o'chira olasiz")

        # Fayllarni diskdan tozalash
        if post.image_url:
            img_path = settings.UPLOAD_DIR / post.image_url
            if img_path.exists() and img_path.is_file():
                try:
                    img_path.unlink()
                except OSError:
                    pass

        if post.video_url:
            vid_path = settings.UPLOAD_DIR / post.video_url
            if vid_path.exists() and vid_path.is_file():
                try:
                    vid_path.unlink()
                except OSError:
                    pass

        await db.delete(post)
        await db.commit()

    @staticmethod
    async def post_exists(db: AsyncSession, post_id: int) -> bool:
        result = await db.execute(select(Post.id).where(Post.id == post_id))
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def like_post(db: AsyncSession, user_id: int, post_id: int) -> None:
        if not await PostService.post_exists(db, post_id):
            raise HTTPException(status_code=404, detail="Post topilmadi")

        result = await db.execute(
            select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        )
        if result.scalar_one_or_none() is not None:
            raise HTTPException(status_code=400, detail="Siz bu postni allaqachon layk qilgansiz")

        like = Like(user_id=user_id, post_id=post_id)
        db.add(like)
        await db.commit()

    @staticmethod
    async def unlike_post(db: AsyncSession, user_id: int, post_id: int) -> None:
        result = await db.execute(
            select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        )
        like = result.scalar_one_or_none()
        if like is None:
            raise HTTPException(status_code=404, detail="Siz bu postni layk qilmagansiz")

        await db.delete(like)
        await db.commit()
