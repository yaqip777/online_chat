from fastapi import FastAPI
from backend.auth.controller import router as auth_router 
from backend.database import init_db 

app = FastAPI()

app.include_router(auth_router)

@app.on_event("startup")
async def startup_event():
    await init_db()

