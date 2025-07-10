.PHONY: dev test compose-up compose-down

DEV_CMD=uvicorn app.rag_api:app --reload --port 8080

dev:
	$(DEV_CMD)

test:
	pytest

compose-up:
	docker-compose up -d

compose-down:
	docker-compose down
