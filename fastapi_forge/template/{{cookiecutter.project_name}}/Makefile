run:
	uv run -m src

up:
	docker-compose up

test:
	docker exec -it $$(docker ps | grep "{{ cookiecutter.project_name }}-api" | awk '{print $$1}') pytest ./app/tests

lint:
	uv run ruff format
	uv run ruff check . --fix
