"""Health check routes for the LabRAG API."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Basic health check."""
    return {"status": "healthy"}
