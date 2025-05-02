default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: start
start: # Start the FastAPI Forge application.
	python -m fastapi_forge start

.PHONY: start-example
start-example: # Start the FastAPI Forge application with an example project.
	python -m fastapi_forge start --use-example

.PHONY: version
version: # Show the version of FastAPI Forge.
	python -m fastapi_forge version

.PHONY: lint
lint: # Run linters on the codebase.
	uv run ruff format
	uv run ruff check . --fix --unsafe-fixes
	uv run mypy fastapi_forge

.PHONY: test
test: # Run all tests in the codebase.
	uv run pytest tests -s -v

.PHONY: test-filter
test-filter: # Run tests with a specific filter.
	uv run pytest tests -v -s -k $(filter)

.PHONY: test-coverage
test-coverage: # Run tests with coverage.
	uv run pytest --cov=fastapi_forge tests/

.PHONY: db
db: # Start the database container.
	docker compose up
