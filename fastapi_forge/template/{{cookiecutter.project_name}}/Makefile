DOCKER_CMD = docker compose exec -it api


run:
	uv run -m src

up:
	docker-compose up

test:
	$(DOCKER_CMD) pytest ./tests -v -s

test-filter:
	$(DOCKER_CMD) /tests -v -s -k $(filter)

mig-gen:
	$(DOCKER_CMD) alembic revision --autogenerate -m "$(name)"

mig-head:
	$(DOCKER_CMD) alembic upgrade head

mig-up:
	$(DOCKER_CMD) alembic upgrade +1

mig-down:
	$(DOCKER_CMD) alembic downgrade -1

lint:
	uv run ruff format
	uv run ruff check . --fix
