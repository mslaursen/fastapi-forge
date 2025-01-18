start:
	python -m fastapi_forge start

lint:
	uv run ruff format
	uv run ruff check . --fix

# Temp
a:
	docker rm -f $$(docker ps -aq)
b:
	docker rmi -f $$(docker images -aq)
c: a b
