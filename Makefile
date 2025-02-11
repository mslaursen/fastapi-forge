start:
	python -m fastapi_forge start

start-defaults:
	python -m fastapi_forge start --use-defaults

lint:
	uv run ruff format
	uv run ruff check . --fix

test:
	uv run pytest tests -s