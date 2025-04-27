from {{cookiecutter.project_name}}.services.taskiq.broker import broker


async def setup_taskiq() -> None:
    if not broker.is_worker_process:
        await broker.startup()


async def shutdown_taskiq() -> None:
    if not broker.is_worker_process:
        await broker.shutdown()
