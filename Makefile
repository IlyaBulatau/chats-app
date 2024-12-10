all: up

up:
	docker compose --env-file ./chat/.env up

down:
	docker compose down
