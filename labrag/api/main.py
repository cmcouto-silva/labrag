from fastapi import FastAPI

from labrag.api.routes import chat, health

app = FastAPI()

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(health.router, tags=["health"])
