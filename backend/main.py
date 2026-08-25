from fastapi import FastAPI
from backend.auth.controller import router as auth_router
from backend.posts.controller import router as posts_router
from backend.database import Base, engine

app = FastAPI()

app.include_router(auth_router)
app.include_router(posts_router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)