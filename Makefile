start:
	python -m fastapi_forge start

lint:
	uv run ruff check . --fix