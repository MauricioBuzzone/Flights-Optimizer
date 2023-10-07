docker-image:
	docker build -f ./base-images/python-base.dockerfile -t "python-base:latest" .
	docker build -f ./client/Dockerfile -t "client:latest" .
	docker build -f ./clientHandler/Dockerfile -t "client_handler:latest" .
	docker build -f ./query1/Dockerfile -t "query1_handler:latest" .
	docker build -f ./query2/Dockerfile -t "query2_handler:latest" .
	docker build -f ./resultHandler/Dockerfile -t "result_handler:latest" .
.PHONY: docker-image

docker-compose-middleware-up: docker-image
	docker compose -f docker-compose-middleware.yaml up -d --build
	docker compose -f docker-compose-middleware.yaml logs -f
.PHONY: docker-compose-middleware-up

docker-compose-up: docker-image
	docker compose -f docker-compose-dev.yaml up -d --build
	docker compose -f docker-compose-dev.yaml logs -f
.PHONY: docker-compose-up

docker-compose-down:
	docker compose -f docker-compose-middleware.yaml stop -t 1
	docker compose -f docker-compose-middleware.yaml down 
	docker compose -f docker-compose-dev.yaml stop -t 1
	docker compose -f docker-compose-dev.yaml down
.PHONY: docker-compose-down

docker-compose-logs:
	docker compose -f docker-compose-dev.yaml logs -f
.PHONY: docker-compose-logs