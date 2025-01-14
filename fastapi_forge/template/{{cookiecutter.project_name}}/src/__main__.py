from src.settings import settings


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.app:get_app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=settings.reload,
        lifespan="on",
        factory=True,
    )
