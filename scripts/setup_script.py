#!/usr/bin/env python3
"""
Project setup script for Warehouse Exchange System

Creates the full directory structure and placeholder files for a professional
Python project structure.
"""

import os
from pathlib import Path

def create_directory_structure():
    """Create the complete project directory structure"""
    
    directories = [
        "warehouse_system",
        "warehouse_system/config",
        "warehouse_system/data_generation", 
        "warehouse_system/models",
        "warehouse_system/analysis",
        "warehouse_system/database",
        "warehouse_system/database/migrations",
        "warehouse_system/utils",
        "tests",
        "tests/test_data_generation",
        "tests/test_analysis",
        "tests/test_models",
        "tests/fixtures",
        "data",
        "data/raw",
        "data/processed", 
        "data/outputs",
        "scripts",
        "docs",
        "docs/examples",
        "notebooks",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def create_init_files():
    """Create __init__.py files for Python packages"""
    
    init_files = [
        "warehouse_system/__init__.py",
        "warehouse_system/config/__init__.py",
        "warehouse_system/data_generation/__init__.py",
        "warehouse_system/models/__init__.py", 
        "warehouse_system/analysis/__init__.py",
        "warehouse_system/database/__init__.py",
        "warehouse_system/utils/__init__.py",
        "tests/__init__.py",
        "tests/test_data_generation/__init__.py",
        "tests/test_analysis/__init__.py",
        "tests/test_models/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"Created: {init_file}")

def create_placeholder_files():
    """Create placeholder files with basic structure"""
    
    # Main module init
    with open("warehouse_system/__init__.py", "w") as f:
        f.write('"""Warehouse Exchange System - An Etherscan for warehouses"""\n\n')
        f.write('__version__ = "0.1.0"\n')
        f.write('__author__ = "Workshop Organizer"\n')
    
    # Config settings
    with open("warehouse_system/config/settings.py", "w") as f:
        f.write('"""Configuration settings for the warehouse system"""\n\n')
        f.write('import os\n')
        f.write('from pathlib import Path\n\n')
        f.write('# Base directory\n')
        f.write('BASE_DIR = Path(__file__).parent.parent.parent\n\n')
        f.write('# Database settings\n')
        f.write('DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///warehouse.db")\n\n')
        f.write('# Data generation settings\n')
        f.write('DEFAULT_COMPANIES = int(os.getenv("DEFAULT_COMPANIES", "100"))\n')
        f.write('DEFAULT_EXCHANGES = int(os.getenv("DEFAULT_EXCHANGES", "50000"))\n')
    
    # Test configuration
    with open("tests/conftest.py", "w") as f:
        f.write('"""Pytest configuration and fixtures"""\n\n')
        f.write('import pytest\n')
        f.write('import pandas as pd\n\n')
        f.write('@pytest.fixture\n')
        f.write('def sample_exchange():\n')
        f.write('    """Sample exchange for testing"""\n')
        f.write('    return {\n')
        f.write('        "exchange_id": "test-123",\n')
        f.write('        "from_warehouse": "WH_A",\n')
        f.write('        "to_warehouse": "WH_B",\n')
        f.write('        "commodity_standard": "interchangeable",\n')
        f.write('        "quantity": 100.0,\n')
        f.write('        "price_paid_usd": 5000.0\n')
        f.write('    }\n')
    
    # Main entry point
    with open("warehouse_system/main.py", "w") as f:
        f.write('"""Main entry point for the warehouse system"""\n\n')
        f.write('import click\n')
        f.write('from warehouse_system.data_generation.generator import WarehouseDataGenerator\n\n')
        f.write('@click.command()\n')
        f.write('@click.option("--companies", default=100, help="Number of companies")\n')
        f.write('@click.option("--exchanges", default=50000, help="Number of exchanges")\n')
        f.write('def main(companies, exchanges):\n')
        f.write('    """Generate warehouse exchange data"""\n')
        f.write('    generator = WarehouseDataGenerator()\n')
        f.write('    generator.generate_companies_and_warehouses(companies)\n')
        f.write('    generator.generate_exchanges(exchanges)\n')
        f.write('    generator.save_to_csv()\n\n')
        f.write('if __name__ == "__main__":\n')
        f.write('    main()\n')
    
    print("Created placeholder files")

def create_sample_scripts():
    """Create sample utility scripts"""
    
    # Data generation script
    with open("scripts/generate_data.py", "w") as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('"""Generate sample warehouse exchange data"""\n\n')
        f.write('import sys\n')
        f.write('import os\n')
        f.write('sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n\n')
        f.write('from warehouse_system.data_generation.generator import WarehouseDataGenerator\n\n')
        f.write('if __name__ == "__main__":\n')
        f.write('    generator = WarehouseDataGenerator()\n')
        f.write('    generator.generate_companies_and_warehouses(100)\n')
        f.write('    generator.generate_exchanges(50000)\n')
        f.write('    generator.save_to_csv("data/outputs/warehouse_data")\n')
    
    # Analysis script
    with open("scripts/run_analysis.py", "w") as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('"""Run FIFO analysis on warehouse data"""\n\n')
        f.write('import sys\n')
        f.write('import os\n')
        f.write('import pandas as pd\n')
        f.write('sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n\n')
        f.write('if __name__ == "__main__":\n')
        f.write('    # Load exchange data\n')
        f.write('    exchanges_df = pd.read_csv("data/outputs/warehouse_data_exchanges.csv")\n')
        f.write('    print(f"Loaded {len(exchanges_df)} exchanges")\n')
        f.write('    \n')
        f.write('    # TODO: Implement FIFO analysis\n')
        f.write('    print("Analysis completed!")\n')
    
    # Make scripts executable
    os.chmod("scripts/generate_data.py", 0o755)
    os.chmod("scripts/run_analysis.py", 0o755)
    
    print("Created sample scripts")

def main():
    """Main setup function"""
    print("Setting up Warehouse Exchange System project structure...")
    
    create_directory_structure()
    create_init_files()
    create_placeholder_files()
    create_sample_scripts()
    
    print("\n✅ Project structure created successfully!")
    print("\nNext steps:")
    print("1. Copy your warehouse data generator to: warehouse_system/data_generation/generator.py")
    print("2. Create virtual environment: python3 -m venv warehouse_env")
    print("3. Activate environment: source warehouse_env/bin/activate")
    print("4. Install dependencies: pip install -r requirements.txt")
    print("5. Generate data: make data")
    print("6. Run tests: make test")

if __name__ == "__main__":
    main()