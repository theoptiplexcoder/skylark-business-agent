from fastapi import APIRouter
from app.services.monday_service import monday_service

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    monday_ok = await monday_service.check_health()
    return {
        "status": "healthy" if monday_ok else "degraded",
        "monday": "connected" if monday_ok else "disconnected",
        "version": "1.0.0",
    }


@router.get("/live")
async def liveness():
    return {"status": "alive"}


@router.get("/ready")
async def readiness():
    return {"status": "ready"}
