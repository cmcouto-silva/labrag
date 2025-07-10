from fastapi import APIRouter, FastAPI

from labrag.api.routes import chat, health

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(health.router, tags=["health"])

app.include_router(api_router, prefix="/api")
