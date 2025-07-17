#!/usr/bin/env python3
"""Test commodity price generation"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_generation.generator import WarehouseDataGenerator
import pandas as pd

def test_commodity_prices():
    print("🧪 Testing Commodity Price Generation...")
    
    # Create generator with short date range for testing
    generator = WarehouseDataGenerator(
        start_date="2024-01-01", 
        end_date="2024-01-31"  # Just January 2024
    )
    
    # Generate only commodity prices (skip other data for speed)
    generator.generate_commodity_prices()
    
    # Convert to DataFrame
    commodity_prices_df = pd.DataFrame(generator.commodity_prices)
    
    print(f"\n📊 Generated {len(commodity_prices_df)} price records")
    
    # Analysis
    print("\n🏷️ Commodities covered:")
    print(commodity_prices_df['commodity_type'].unique())
    
    print("\n📅 Date range:")
    print(f"From: {commodity_prices_df['date'].min()}")
    print(f"To: {commodity_prices_df['date'].max()}")
    
    print("\n💰 Price summary by commodity:")
    price_summary = commodity_prices_df.groupby('commodity_type')['price_per_unit'].agg(['min', 'max', 'mean']).round(2)
    print(price_summary)
    
    print("\n🌾 Sample Wheat prices (first 10 days):")
    wheat_sample = commodity_prices_df[commodity_prices_df['commodity_type'] == 'Wheat'].head(10)
    for _, row in wheat_sample.iterrows():
        print(f"  {row['date']}: ${row['price_per_unit']:6.2f}/{row['unit']}")
    
    print("\n🛢️ Sample Crude Oil prices (first 10 days):")
    oil_sample = commodity_prices_df[commodity_prices_df['commodity_type'] == 'Crude Oil'].head(10)
    for _, row in oil_sample.iterrows():
        print(f"  {row['date']}: ${row['price_per_unit']:6.2f}/{row['unit']}")
    
    # Check data structure
    print(f"\n📋 Table structure:")
    print(f"Columns: {list(commodity_prices_df.columns)}")
    print(f"Sample record:")
    print(commodity_prices_df.iloc[0].to_dict())
    
    # Save test output
    commodity_prices_df.to_csv('test_commodity_prices.csv', index=False)
    print(f"\n💾 Saved test data to: test_commodity_prices.csv")
    
    print("\n✅ Commodity price generation test complete!")

if __name__ == "__main__":
    test_commodity_prices()
