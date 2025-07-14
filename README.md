# Warehouse Exchange System

An "Etherscan for warehouses" - a comprehensive system for tracking and analyzing commodity and item exchanges between warehouses worldwide.

## 🚀 Overview

This system models real-world warehouse trading operations where entities exchange money (USD) for the movement of commodities and items between warehouse locations. Think of it as blockchain transaction tracking, but for physical goods in the real world.

## 📊 Key Features

- **Realistic Data Generation**: Generate millions of synthetic warehouse exchanges with realistic seasonal patterns, geographic trade flows, and market dynamics
- **FIFO Cost Accounting**: Calculate capital gains using First-In-First-Out methodology for different commodity types
- **Seasonal Market Modeling**: Built-in seasonal pricing patterns for commodities like wheat, oil, steel, and cocoa
- **Geographic Trade Flows**: Model real-world trade relationships between exporter and importer countries
- **Multiple Commodity Types**: Support for interchangeable commodities, serialized items, and batched goods

## 🏗️ Project Structure

```
warehouse-exchange-system/
├── warehouse_system/           # Main package
│   ├── data_generation/       # Data generation modules
│   ├── models/               # Data models (Exchange, Warehouse, Company)
│   ├── analysis/             # FIFO calculator, profit analyzer
│   └── database/             # Database schema and connections
├── tests/                    # Unit and integration tests
├── scripts/                  # Utility scripts
├── data/                     # Generated datasets
└── docs/                     # Documentation
```

## 🔧 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd warehouse-exchange-system

# Create virtual environment
python3 -m venv warehouse_env
source warehouse_env/bin/activate  # On Mac/Linux
# warehouse_env\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Sample Data

```bash
# Generate 50K exchanges across 100 companies
python scripts/generate_data.py

# Or use the main module
python -m warehouse_system.data_generation.generator
```

### 3. Run Analysis

```bash
# Calculate FIFO profits for all entities
python scripts/run_analysis.py

# Or run specific analysis
from warehouse_system.analysis import FIFOCalculator
calculator = FIFOCalculator()
profits = calculator.calculate_entity_profits('entity_id')
```

## 📈 Data Model

### Exchange Structure
```python
{
    "exchange_id": "uuid",
    "from_warehouse": "warehouse_id or 0x0000",
    "to_warehouse": "warehouse_id or 0x0000", 
    "brand_manufacturer": "Company Name",
    "item_type": "Wheat | Art | Electronics",
    "commodity_standard": "interchangeable | serialized | batched",
    "quantity": 100.5,
    "unit": "tons | pieces | barrels",
    "price_paid_usd": 25000.00,
    "timestamp": "2024-07-14",
    "batch_id": "optional",
    "item_ids": ["optional", "list"]
}
```

### Commodity Types

1. **Interchangeable** (like ERC20): Wheat, oil, steel - divisible by weight/volume
2. **Serialized** (like NFT): Art, cars, equipment - unique items with IDs  
3. **Batched** (like ERC1155): Limited editions - fungible within batch, unique across batches

### Special Operations

- **Mint** (`from_warehouse: "0x0000"`): New production entering the system
- **Burn** (`to_warehouse: "0x0000"`): Items leaving the system (disposal, export)

## 💰 FIFO Capital Gains

The system implements First-In-First-Out accounting for capital gains calculations:

```python
# Example: Wheat trading
Buy 100 tons @ $200/ton = $20,000 (Jan)
Buy 100 tons @ $250/ton = $25,000 (Mar)
Sell 150 tons @ $300/ton = $45,000 (May)

# FIFO Calculation:
Cost basis = (100 tons × $200) + (50 tons × $250) = $32,500
Capital gain = $45,000 - $32,500 = $12,500
```

## 🌍 Seasonal Patterns

Built-in seasonal pricing models based on real commodity markets:

- **Wheat**: Pre-harvest high → Harvest dip → Post-harvest recovery
- **Steel**: Construction season peaks (Apr-Sep)
- **Oil**: Winter heating + Summer driving demand
- **Cocoa**: Dual harvest seasons (Oct-Mar, May-Aug)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=warehouse_system

# Run specific test category
pytest tests/test_analysis/
```

## 📚 Documentation

- [Data Model Documentation](docs/data_model.md)
- [API Reference](docs/api.md)
- [Usage Examples](docs/examples/)

## 🛠️ Development

### Code Style
```bash
# Format code
black warehouse_system/

# Lint code  
flake8 warehouse_system/

# Type checking
mypy warehouse_system/
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## 📋 Makefile Commands

```bash
make install     # Install dependencies
make test        # Run tests
make lint        # Run linting
make format      # Format code
make clean       # Clean build artifacts
make data        # Generate sample data
```

## 🎯 Workshop Use Cases

This project is designed for hands-on coding workshops where participants can:

1. **Fix Bugs**: Debug FIFO calculation errors, data validation issues
2. **Add Features**: Implement new commodity types, analysis functions
3. **Write Tests**: Add comprehensive test coverage for edge cases
4. **Optimize Performance**: Improve database queries, batch processing
5. **Extend Analysis**: Add risk assessment, market trend analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by blockchain transaction tracking systems like Etherscan
- Real-world commodity pricing patterns from various trading platforms
- Geographic trade flow data from international trade statistics