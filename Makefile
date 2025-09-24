.PHONY: setup install run test worker migrations migrate test-vosk test-loop-fix install-vosk

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

worker:
	celery -A app.worker.tasks worker --loglevel=info

migrations:
	alembic revision --autogenerate -m "Auto migration"

migrate:
	alembic upgrade head