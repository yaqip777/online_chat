from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.auth.controller import router as auth_router
from backend.chat.controller import router as chat_router
from backend.config import settings
from backend.database import engine, init_db
from backend.follows.controller import router as follows_router
from backend.posts.controller import router as posts_router
from backend.stories.controller import router as stories_router
from backend.websocket.controller import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dastur ishga tushganda: ma'lumotlar bazasini initsializatsiya qilish
    await init_db()
    yield
    # Dastur to'xtaganda: connection pool ni toza yopish
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statik fayllar (yuklangan rasm va videolar)
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

# Routerlarni ulash
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(stories_router)
app.include_router(chat_router)
app.include_router(follows_router)
app.include_router(websocket_router)


@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
