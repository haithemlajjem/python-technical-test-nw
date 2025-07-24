build:
	docker compose build

up:
	docker compose up

down:
	docker compose down

stop:
	docker compose stop

restart:
	docker compose restart

sh:
	docker exec -it technical-test-api sh

migrations:
	docker exec -it technical-test-api alembic revision --autogenerate -m "$(msg)"

migrate:
	docker exec -it technical-test-api alembic upgrade head

downgrade:
	docker exec -it technical-test-api alembic downgrade -1

fmt:
	poetry run black . && poetry run isort .

lint:
	poetry run ruff check .

lint_fix:
	poetry run ruff check . --fix

generate_requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

test:
	poetry run pytest
