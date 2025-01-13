from fastapi import APIRouter


base_router = APIRouter(prefix="/api/v1")


@base_router.get("/health")
async def health_check() -> bool:
    """Return True if the service is healthy."""

    return True
