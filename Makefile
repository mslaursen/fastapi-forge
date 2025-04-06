start:
	python -m fastapi_forge start

start-defaults:
	python -m fastapi_forge start --use-defaults

version:
	python -m fastapi_forge version

lint:
	uv run ruff format
	uv run ruff check . --fix --unsafe-fixes

test:
	uv run pytest tests -s -v

test-filter:
	uv run pytest tests -v -s -k $(filter)

db:
	docker compose up
