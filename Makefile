.PHONY: help install install-dev test test-cov lint format type-check clean data setup test-flows test-full test-mock test-demo tasks

# Default target
help:
	@echo "Available commands:"
	@echo "  setup        Set up development environment"
	@echo "  install      Install production dependencies"
	@echo "  run-flow     Run warehouse main flow"
	@echo "  test         Run tests"
	@echo "  lint         Run flake8 linting"
	@echo "  format       Format code with black"
	@echo "  data         Generate sample data"
	@echo "  db-upload    Upload data to Supabase database"

# Installation
install:
	pip install -r requirements.txt

# Testing
test:
	pytest tests/ -v

# Code quality
lint:
	flake8 src/ tests/

format:
	black src/ tests/ scripts/
	isort src/ tests/ scripts/

setup:
	python3 -m venv warehouse_env
	@echo "Virtual environment created. Activate with:"
	@echo "source warehouse_env/bin/activate"
	@echo "Then run:"
	@echo "pip install -r requirements.txt"

data:
	mkdir -p data/raw data/processed data/outputs
	python scripts/generate_data.py

db-upload:
	python scripts/upload_to_supabase.py

run-flow:
	python scripts/test_warehouse_flows.py
