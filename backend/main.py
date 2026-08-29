from fastapi import FastAPI
from backend.auth.controller import router as auth_router
from backend.posts.controller import router as posts_router
from backend.websocket.controller import router as websocket_router
from backend.chat.controller import router as chat_router
from backend.stories.controller import router as stories_router
from backend.database import Base, engine

app = FastAPI()

app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(websocket_router)
app.include_router(chat_router)
app.include_router(stories_router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)