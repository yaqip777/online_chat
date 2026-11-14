from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings

class Base(DeclarativeBase):
    pass


# Production uchun optimallashtirilgan async engine
engine = create_async_engine(
    settings.get_database_url(),
    pool_pre_ping=True,  # Buzilgan ulanishlarni avtomatik aniqlab qayta ulanadi
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,  # Har 30 daqiqada ulanishlarni yangilash
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


async def init_db() -> None:
    # Barcha modellarni Base metadata ga ro'yxatdan o'tkazish
    import backend.auth.models  # noqa: F401
    import backend.follows.models  # noqa: F401
    import backend.posts.models  # noqa: F401
    import backend.stories.models  # noqa: F401
    import backend.chat.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
