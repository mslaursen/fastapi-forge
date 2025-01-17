from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
async def health_check() -> bool:
    """Return True if the service is healthy."""

    return True
