.PHONY: help install install-dev test test-cov lint format type-check clean data setup docs

# Default target
help:
	@echo "Available commands:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run flake8 linting"
	@echo "  format       Format code with black"
	@echo "  type-check   Run mypy type checking"
	@echo "  clean        Clean build artifacts"
	@echo "  data         Generate sample data"
	@echo "  setup        Set up development environment"
	@echo "  db-upload    Upload data to Supabase database"
	@echo "  supabase-demo         Run Supabase client demo"
	@echo "  test-flows   Test warehouse flows structure"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"
	pre-commit install

# Testing
test:
	pytest tests/ -v

# Code quality
lint:
	flake8 src/ tests/

format:
	black src/ tests/ scripts/
	isort src/ tests/ scripts/

type-check:
	mypy src/

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Data generation
data:
	mkdir -p data/raw data/processed data/outputs
	python scripts/generate_data.py

data-small:
	mkdir -p data/raw data/processed data/outputs
	python scripts/generate_data.py --companies 20 --exchanges 5000

data-large:
	mkdir -p data/raw data/processed data/outputs
	python scripts/generate_data.py --companies 500 --exchanges 1000000

# Development setup
setup:
	python3 -m venv warehouse_env
	@echo "Virtual environment created. Activate with:"
	@echo "source warehouse_env/bin/activate"

supabase-demo:
	python scripts/demo_supabase_client.py

# Database
db-setup:
	python scripts/setup_database.py

db-upload:
	python scripts/upload_to_supabase.py

db-migrate:
	python scripts/migrate_database.py

test-flows:
	python scripts/test_warehouse_flows.py

# All quality checks
check: lint type-check test
