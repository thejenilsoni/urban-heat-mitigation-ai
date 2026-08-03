.PHONY: install dev api web test lint build validate data train

install:
	npm install
	python -m pip install -e ".[dev]"

dev:
	docker compose up --build

api:
	uvicorn services.api.app.main:app --reload --port 8000

web:
	npm run dev

data:
	python scripts/generate_demo_data.py

train:
	python scripts/train_demo_model.py

test:
	pytest
	npm run test:web

lint:
	ruff check ml services scripts tests
	npm run lint

build:
	npm run build

validate: test lint build
