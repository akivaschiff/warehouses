"""Main entry point for the warehouse system"""

import click
from warehouse_system.data_generation.generator import WarehouseDataGenerator

@click.command()
@click.option("--companies", default=100, help="Number of companies")
@click.option("--exchanges", default=50000, help="Number of exchanges")
def main(companies, exchanges):
    """Generate warehouse exchange data"""
    generator = WarehouseDataGenerator()
    generator.generate_companies_and_warehouses(companies)
    generator.generate_exchanges(exchanges)
    generator.save_to_csv()

if __name__ == "__main__":
    main()
