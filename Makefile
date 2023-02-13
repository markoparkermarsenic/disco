api-dev:
	docker compose -f docker-compose.debug.yml up --build

api-dev-down:
	docker compose -f docker-compose.debug.yml down

api-dev-restart:
	docker compose -f docker-compose.debug.yml restart

api:
	docker compose up --build

api-down:
	docker compose down
