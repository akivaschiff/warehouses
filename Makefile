.PHONY: help install install-dev test test-cov lint format type-check clean data setup test-flows test-full test-mock test-demo tasks

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
	@echo "  test-full    Test complete end-to-end flow"
	@echo "  test-mock    Test gains calculator with mocked data"
	@echo "  test-demo    Demo two-exchange scenario"
	@echo "  tasks        Show workshop tasks"

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

test-full:
	python scripts/test_full_flow.py

test-mock:
	pytest tests/test_gains_calculator_mocked.py -v

test-demo:
	python scripts/test_two_exchange_demo.py

tasks:
	@echo "📚 Workshop Tasks Available:"
	@echo "  Task 1: Verify Warehouse Gains (30 min)"
	@echo "  Task 2: Precise Daily Pricing (2-3 hours)"  
	@echo "  Task 3: Add Serialized Items (2-4 hours)"
	@echo "  Task 4: FIFO Capital Gains (4-6 hours)"
	@echo "  Task 5: Entity Portfolio Analysis (4-8 hours)"
	@echo ""
	@echo "📖 See tasks/README.md for full details"
	@echo "🚀 Start with: tasks/task_1_verify_warehouse_gains.md"

# All quality checks
check: lint type-check test
