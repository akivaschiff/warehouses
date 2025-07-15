#!/usr/bin/env python3
"""Generate warehouse exchange data"""

import sys
import os
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_generation.generator import WarehouseDataGenerator

def main():
    parser = argparse.ArgumentParser(description='Generate warehouse exchange data')
    parser.add_argument('--companies', type=int, default=100, help='Number of companies')
    parser.add_argument('--exchanges', type=int, default=50000, help='Number of exchanges')
    parser.add_argument('--output', default='data/outputs/warehouse_data', help='Output file prefix')
    
    args = parser.parse_args()
    
    generator = WarehouseDataGenerator()
    generator.generate_companies_and_warehouses(args.companies)
    generator.generate_exchanges(args.exchanges)
    generator.save_to_csv(args.output)

if __name__ == "__main__":
    main()