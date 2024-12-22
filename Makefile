all: up

up:
	docker compose --env-file ./chat/.env up

down:
	docker compose down

rebuild:
	docker compose --env-file ./chat/.env build app
	docker image prune -f
