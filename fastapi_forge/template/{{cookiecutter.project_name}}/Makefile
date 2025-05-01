DOCKER_CMD = docker compose exec -it api

default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: run
run: # Run the application.
	uv run -m {{cookiecutter.project_name}}

.PHONY: up
up: # Start the project with Docker Compose.
	docker-compose up --watch

.PHONY: down
down: # Stop the project with Docker Compose.
	docker-compose down

.PHONY: test
test: # Run all tests in the codebase.
	$(DOCKER_CMD) pytest ./tests -v -s

.PHONY: test-filter
test-filter: # Run tests with a specific filter.
	$(DOCKER_CMD) pytest ./tests -v -s -k $(filter)

.PHONY: test-coverage
test-coverage: # Run tests with coverage.
	$(DOCKER_CMD) pytest --cov={{cookiecutter.project_name}} tests/

.PHONY: mig-gen
mig-gen: # Generate a new migration file.
	$(DOCKER_CMD) alembic revision --autogenerate -m "$(name)"

.PHONY: mig-head
mig-head: # Migrate to the latest version.
	$(DOCKER_CMD) alembic upgrade head

.PHONY: mig-up
mig-up: # Migrate to the next version.
	$(DOCKER_CMD) alembic upgrade +1

.PHONY: mig-down
mig-down: # Migrate to the previous version.
	$(DOCKER_CMD) alembic downgrade -1

.PHONY: lint
lint: # Run linters on the codebase.
	uv run ruff format {{cookiecutter.project_name}} tests
	uv run ruff check {{cookiecutter.project_name}} tests --fix --unsafe-fixes
	uv run mypy {{cookiecutter.project_name}}