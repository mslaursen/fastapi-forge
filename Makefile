start:
	python -m fastapi_forge start

lint:
	uv run ruff format
	uv run ruff check . --fix

test:
	uv run pytest tests -s