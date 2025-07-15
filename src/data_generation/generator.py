"""
Warehouse Exchange Data Generator

Generates realistic warehouse exchange data with:
- Nuanced seasonal pricing patterns (12-month curves with random fluctuation)
- Real-world trade flows between exporter/importer countries  
- Realistic commodity pricing (non-round numbers)
- Multiple commodity types with different characteristics
- Manufacturing (mint) and disposal (burn) operations
- Proper business logic and trading relationships

Each commodity has a detailed seasonal curve reflecting real market patterns:
- Wheat: Pre-harvest high, harvest dip, recovery
- Cocoa: Dual harvest season pattern
- Oil: Winter heating and summer driving demand
- Steel: Construction season peaks
- Coffee: Harvest cycles and demand variations
- Copper: Industrial demand cycles
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import uuid

fake = Faker()

# Real-world trade patterns with nuanced seasonal curves
COMMODITY_PATTERNS = {
    'wheat': {
        'exporters': ['USA', 'Ukraine', 'Russia', 'Australia', 'Canada'],
        'importers': ['Egypt', 'Indonesia', 'Brazil', 'Nigeria', 'Japan'],
        # Seasonal pattern: Jan-Dec (pre-harvest high, harvest low, post-harvest recovery)
        'seasonal_multipliers': [1.15, 1.25, 1.30, 1.20, 0.95, 0.75, 0.70, 0.80, 0.90, 1.05, 1.10, 1.12],
        'base_price': 247.83,  # USD per ton
        'volatility': 0.28
    },
    'cocoa': {
        'exporters': ['Côte d\'Ivoire', 'Ghana', 'Ecuador', 'Nigeria', 'Brazil'],
        'importers': ['Netherlands', 'Germany', 'USA', 'Malaysia', 'Belgium'],
        # Seasonal pattern: Two harvest seasons with price dips
        'seasonal_multipliers': [0.85, 0.75, 0.80, 0.95, 1.10, 1.25, 1.30, 1.15, 1.05, 0.90, 0.70, 0.80],
        'base_price': 2847.92,  # USD per ton
        'volatility': 0.42
    },
    'crude_oil': {
        'exporters': ['Saudi Arabia', 'Russia', 'USA', 'Iraq', 'Canada'],
        'importers': ['China', 'USA', 'India', 'Japan', 'South Korea'],
        # Seasonal pattern: Winter heating demand, summer driving, refinery maintenance
        'seasonal_multipliers': [1.20, 1.25, 1.10, 0.95, 0.90, 1.05, 1.15, 1.10, 0.95, 0.85, 1.00, 1.15],
        'base_price': 73.42,  # USD per barrel
        'volatility': 0.48
    },
    'steel': {
        'exporters': ['China', 'Japan', 'India', 'Russia', 'South Korea'],
        'importers': ['USA', 'Germany', 'South Korea', 'Turkey', 'Mexico'],
        # Seasonal pattern: Construction season peak, winter low
        'seasonal_multipliers': [0.85, 0.90, 1.05, 1.20, 1.30, 1.35, 1.25, 1.15, 1.10, 1.00, 0.80, 0.75],
        'base_price': 634.17,  # USD per ton
        'volatility': 0.22
    },
    'coffee': {
        'exporters': ['Brazil', 'Vietnam', 'Colombia', 'Indonesia', 'Ethiopia'],
        'importers': ['USA', 'Germany', 'Japan', 'Italy', 'Belgium'],
        # Seasonal pattern: Harvest cycles and demand variations
        'seasonal_multipliers': [1.10, 1.05, 0.95, 0.85, 0.80, 0.90, 1.15, 1.25, 1.20, 1.10, 1.00, 1.05],
        'base_price': 4567.31,  # USD per ton
        'volatility': 0.35
    },
    'copper': {
        'exporters': ['Chile', 'Peru', 'China', 'USA', 'Australia'],
        'importers': ['China', 'Germany', 'Japan', 'South Korea', 'Italy'],
        # Seasonal pattern: Industrial demand cycles
        'seasonal_multipliers': [0.95, 1.00, 1.15, 1.25, 1.20, 1.10, 1.05, 1.15, 1.25, 1.20, 0.90, 0.85],
        'base_price': 8943.76,  # USD per ton
        'volatility': 0.31
    }
}

SERIALIZED_ITEMS = {
    'luxury_cars': {
        'manufacturers': ['Ferrari', 'Lamborghini', 'Porsche', 'McLaren'],
        'exporters': ['Italy', 'Germany', 'UK'],
        'importers': ['USA', 'China', 'UAE', 'Japan'],
        'seasonal_multipliers': [0.85, 0.90, 1.05, 1.10, 1.15, 1.20, 1.10, 1.05, 0.95, 0.90, 0.75, 0.80],  # Summer peak
        'base_price': 287643.19,
        'volatility': 0.18
    },
    'art_pieces': {
        'manufacturers': ['Sotheby\'s', 'Christie\'s', 'Phillips', 'Bonhams'],
        'exporters': ['USA', 'UK', 'France', 'Switzerland'],
        'importers': ['USA', 'China', 'Russia', 'UAE'],
        'seasonal_multipliers': [1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 0.85, 0.80, 0.90, 1.00, 1.10, 1.15],  # Spring auction season
        'base_price': 67891.42,
        'volatility': 0.73
    },
    'industrial_equipment': {
        'manufacturers': ['Caterpillar', 'Komatsu', 'Volvo', 'Liebherr'],
        'exporters': ['USA', 'Japan', 'Sweden', 'Germany'],
        'importers': ['China', 'India', 'Brazil', 'Australia'],
        'seasonal_multipliers': [0.90, 0.95, 1.10, 1.25, 1.35, 1.30, 1.20, 1.15, 1.10, 1.00, 0.85, 0.80],  # Construction season
        'base_price': 547329.83,
        'volatility': 0.12
    },
    'electronics': {
        'manufacturers': ['Apple', 'Samsung', 'Sony', 'LG'],
        'exporters': ['China', 'South Korea', 'Japan', 'Taiwan'],
        'importers': ['USA', 'Germany', 'UK', 'India'],
        'seasonal_multipliers': [0.80, 0.85, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 1.35, 1.40],  # Holiday season buildup
        'base_price': 1247.83,
        'volatility': 0.25
    }
}

class WarehouseDataGenerator:
    def __init__(self, start_date='2022-01-01', end_date='2024-12-31'):
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.warehouses = []
        self.companies = []
        self.exchanges = []
        
    def generate_companies_and_warehouses(self, num_companies=50):
        """Generate realistic companies and their warehouses"""
        
        for _ in range(num_companies):
            company = {
                'company_id': str(uuid.uuid4()),
                'name': fake.company(),
                'country': fake.country()
            }
            self.companies.append(company)
            
            # Each company has 2-8 warehouses
            num_warehouses = random.randint(2, 8)
            for _ in range(num_warehouses):
                warehouse = {
                    'warehouse_id': f"WH_{fake.uuid4()[:8]}",
                    'company_id': company['company_id'],
                    'address': fake.address().replace('\n', ', '),
                    'country': company['country'],
                    'warehouse_type': random.choice(['distribution', 'storage', 'manufacturing', 'retail'])
                }
                self.warehouses.append(warehouse)
        
        # Add special null warehouse for mint/burn
        self.warehouses.append({
            'warehouse_id': '0x0000',
            'company_id': None,
            'address': 'System Null Address',
            'country': 'Global',
            'warehouse_type': 'system'
        })
    
    def get_seasonal_price_multiplier(self, item_patterns, date):
        """Calculate nuanced seasonal price variation with random fluctuation"""
        month = date.month
        base_multiplier = item_patterns['seasonal_multipliers'][month - 1]  # 0-indexed
        
        # Add random fluctuation around the base seasonal pattern (±15%)
        fluctuation = random.uniform(-0.15, 0.15)
        final_multiplier = base_multiplier * (1 + fluctuation)
        
        # Ensure multiplier stays within reasonable bounds
        return max(0.5, min(2.0, final_multiplier))
    
    def generate_commodity_exchange(self, date):
        """Generate a realistic commodity exchange"""
        commodity = random.choice(list(COMMODITY_PATTERNS.keys()))
        pattern = COMMODITY_PATTERNS[commodity]
        
        # Choose realistic trade route
        is_mint = random.random() < 0.05  # 5% are new production
        
        if is_mint:
            from_warehouse = '0x0000'
            to_country = random.choice(pattern['exporters'])
            to_warehouses = [w for w in self.warehouses if w['country'] == to_country and w['warehouse_type'] in ['manufacturing', 'distribution']]
            to_warehouse = random.choice(to_warehouses)['warehouse_id'] if to_warehouses else random.choice(self.warehouses)['warehouse_id']
            brand_manufacturer = fake.company()
        else:
            # Regular trade: exporter -> importer
            from_country = random.choice(pattern['exporters'])
            to_country = random.choice(pattern['importers'])
            
            from_warehouses = [w for w in self.warehouses if w['country'] == from_country]
            to_warehouses = [w for w in self.warehouses if w['country'] == to_country]
            
            from_warehouse = random.choice(from_warehouses)['warehouse_id'] if from_warehouses else random.choice(self.warehouses)['warehouse_id']
            to_warehouse = random.choice(to_warehouses)['warehouse_id'] if to_warehouses else random.choice(self.warehouses)['warehouse_id']
            brand_manufacturer = fake.company()
        
        # Calculate price with nuanced seasonal variation
        base_price = pattern['base_price']
        seasonal_multiplier = self.get_seasonal_price_multiplier(pattern, date)
        volatility = pattern['volatility']
        price_per_unit = base_price * seasonal_multiplier * random.uniform(1-volatility, 1+volatility)
        
        # Generate realistic quantity based on commodity type
        if commodity == 'crude_oil':
            quantity = round(random.uniform(5000, 100000), 1)  # barrels (realistic shipment sizes)
            unit = 'barrels'
        elif commodity == 'copper':
            quantity = round(random.uniform(5, 500), 2)  # tons (smaller, more valuable shipments)
            unit = 'tons'
        elif commodity == 'coffee':
            quantity = round(random.uniform(10, 300), 1)  # tons (container loads)
            unit = 'tons'
        else:  # wheat, cocoa, steel
            quantity = round(random.uniform(50, 2000), 1)  # tons (bulk commodity shipments)
            unit = 'tons'
        
        total_price = quantity * price_per_unit
        
        return {
            'exchange_id': str(uuid.uuid4()),
            'from_warehouse': from_warehouse,
            'to_warehouse': to_warehouse,
            'brand_manufacturer': brand_manufacturer,
            'item_type': commodity.replace('_', ' ').title(),
            'commodity_standard': 'bulk',
            'quantity': quantity,
            'unit': unit,
            'price_paid_usd': round(total_price, 2),
            'timestamp': date,
            'batch_id': None,
            'item_ids': None
        }
    
    def generate_serialized_exchange(self, date):
        """Generate a realistic serialized item exchange"""
        item_type = random.choice(list(SERIALIZED_ITEMS.keys()))
        pattern = SERIALIZED_ITEMS[item_type]
        
        # Choose trade route
        is_mint = random.random() < 0.1  # 10% are new manufacturing
        
        if is_mint:
            from_warehouse = '0x0000'
            brand_manufacturer = random.choice(pattern['manufacturers'])
            to_country = random.choice(pattern['exporters'])
            to_warehouses = [w for w in self.warehouses if w['country'] == to_country and w['warehouse_type'] == 'manufacturing']
            to_warehouse = random.choice(to_warehouses)['warehouse_id'] if to_warehouses else random.choice(self.warehouses)['warehouse_id']
        else:
            from_country = random.choice(pattern['exporters'])
            to_country = random.choice(pattern['importers'])
            
            from_warehouses = [w for w in self.warehouses if w['country'] == from_country]
            to_warehouses = [w for w in self.warehouses if w['country'] == to_country]
            
            from_warehouse = random.choice(from_warehouses)['warehouse_id'] if from_warehouses else random.choice(self.warehouses)['warehouse_id']
            to_warehouse = random.choice(to_warehouses)['warehouse_id'] if to_warehouses else random.choice(self.warehouses)['warehouse_id']
            brand_manufacturer = random.choice(pattern['manufacturers'])
        
        # Calculate price with seasonal variation
        base_price = pattern['base_price']
        seasonal_multiplier = self.get_seasonal_price_multiplier(pattern, date)
        volatility = pattern['volatility']
        price = base_price * seasonal_multiplier * random.uniform(1-volatility, 1+volatility)
        
        # Generate item ID
        item_id = f"{brand_manufacturer[:3].upper()}-{fake.uuid4()[:8]}"
        
        return {
            'exchange_id': str(uuid.uuid4()),
            'from_warehouse': from_warehouse,
            'to_warehouse': to_warehouse,
            'brand_manufacturer': brand_manufacturer,
            'item_type': item_type.replace('_', ' ').title(),
            'commodity_standard': 'serialized',
            'quantity': 1,
            'unit': 'pieces',
            'price_paid_usd': round(price, 2),
            'timestamp': date,
            'batch_id': None,
            'item_ids': [item_id]
        }
    
    def generate_exchanges(self, num_exchanges=100000):
        """Generate the specified number of exchanges"""
        print(f"Generating {num_exchanges} exchanges...")
        
        # Generate date range
        date_range = pd.date_range(self.start_date, self.end_date, freq='D')
        
        for i in range(num_exchanges):
            if i % 10000 == 0:
                print(f"Generated {i} exchanges...")
            
            # Random date
            date = fake.date_between(self.start_date, self.end_date)
            
            # 80% commodities, 20% serialized items
            if random.random() < 0.8:
                exchange = self.generate_commodity_exchange(date)
            else:
                exchange = self.generate_serialized_exchange(date)
            
            self.exchanges.append(exchange)
        
        print(f"Generated {len(self.exchanges)} total exchanges!")
    
    def to_dataframes(self):
        """Convert to pandas DataFrames"""
        companies_df = pd.DataFrame(self.companies)
        warehouses_df = pd.DataFrame(self.warehouses)
        exchanges_df = pd.DataFrame(self.exchanges)
        
        return companies_df, warehouses_df, exchanges_df
    
    def save_to_csv(self, prefix='warehouse_data'):
        """Save all data to CSV files"""
        companies_df, warehouses_df, exchanges_df = self.to_dataframes()
        
        companies_df.to_csv(f'{prefix}_companies.csv', index=False)
        warehouses_df.to_csv(f'{prefix}_warehouses.csv', index=False)
        exchanges_df.to_csv(f'{prefix}_exchanges.csv', index=False)
        
        print(f"Saved {len(companies_df)} companies, {len(warehouses_df)} warehouses, {len(exchanges_df)} exchanges")

# Usage example
if __name__ == "__main__":
    generator = WarehouseDataGenerator()
    
    # Generate base data
    generator.generate_companies_and_warehouses(num_companies=100)
    
    # Generate exchanges (start small for testing)
    generator.generate_exchanges(num_exchanges=50000)
    
    # Save to files
    generator.save_to_csv()
    
    # Quick analysis
    companies_df, warehouses_df, exchanges_df = generator.to_dataframes()
    
    print("\n=== Data Summary ===")
    print(f"Companies: {len(companies_df)}")
    print(f"Warehouses: {len(warehouses_df)}")
    print(f"Exchanges: {len(exchanges_df)}")
    print(f"Date range: {exchanges_df['timestamp'].min()} to {exchanges_df['timestamp'].max()}")
    print(f"Total value: ${exchanges_df['price_paid_usd'].sum():,.2f}")
    
    print("\n=== Commodity Distribution ===")
    print(exchanges_df['item_type'].value_counts())
    
    print("\n=== Sample Exchanges ===")
    print(exchanges_df.head(3).to_string())
    
    print("\n=== Seasonal Price Analysis (Wheat) ===")
    wheat_exchanges = exchanges_df[exchanges_df['item_type'] == 'Wheat'].copy()
    if len(wheat_exchanges) > 0:
        wheat_exchanges['month'] = pd.to_datetime(wheat_exchanges['timestamp']).dt.month
        wheat_exchanges['price_per_unit'] = wheat_exchanges['price_paid_usd'] / wheat_exchanges['quantity']
        monthly_avg = wheat_exchanges.groupby('month')['price_per_unit'].mean()
        print("Average wheat price per ton by month:")
        for month, price in monthly_avg.items():
            print(f"Month {month:2d}: ${price:6.2f}")
    
    print("\n=== Geographic Trade Flow Analysis ===")
    trades_by_country = warehouses_df.merge(exchanges_df, left_on='warehouse_id', right_on='from_warehouse')
    country_exports = trades_by_country.groupby('country')['price_paid_usd'].sum().sort_values(ascending=False)
    print("Top 5 exporting countries by value:")
    print(country_exports.head().to_string())