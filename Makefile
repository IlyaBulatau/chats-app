all: up

up:
	docker compose --env-file ./chat/.env up

down:
	docker compose down

rebuild:
	docker compose --env-file ./chat/.env build app
	docker compose --env-file ./chat/.env build worker
	docker image prune -f
