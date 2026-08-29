from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "supportflow-ai",
        "timestamp": datetime.now(timezone.utc),
    }