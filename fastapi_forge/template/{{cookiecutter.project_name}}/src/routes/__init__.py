from src.routes.health_routes import router as health_router

from fastapi import APIRouter


base_router = APIRouter(prefix="/api/v1")

base_router.include_router(health_router, tags=["health"])
