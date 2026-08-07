from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.boards import router as boards_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.health import router as health_router
from app.api.v1.query import router as query_router
from app.api.v1.monday import router as monday_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(boards_router)
api_router.include_router(metrics_router)
api_router.include_router(health_router)
api_router.include_router(query_router)
api_router.include_router(monday_router)
