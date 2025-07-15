#!/usr/bin/env python3
"""
Demo script for the Supabase Client

This script demonstrates how to use the SupabaseClient to query warehouse data.
Perfect for workshop participants to learn the API.

Run with: python scripts/demo_supabase_client.py
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.supabase_client import SupabaseClient
import pandas as pd

def main():
    """Demonstrate various SupabaseClient features"""
    
    print("🚀 Warehouse Data Explorer Demo\n")
    
    # Initialize client
    try:
        client = SupabaseClient()
        print("✅ Connected to Supabase successfully!")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("Make sure your DATABASE_URL is set in .env file")
        return
    
    # 1. List all tables
    print("\n" + "="*50)
    print("📋 AVAILABLE TABLES")
    print("="*50)
    tables = client.list_tables()
    for table in tables:
        info = client.get_table_info(table)
        print(f"📊 {table}: {info.get('row_count', 0)} rows")
    
    # 2. Explore table structures
    print("\n" + "="*50)
    print("🔍 TABLE STRUCTURES")
    print("="*50)
    for table in tables:
        info = client.get_table_info(table)
        print(f"\n📊 {table.upper()}:")
        for col in info.get('columns', []):
            print(f"  • {col['name']} ({col['type']})")
    
    # 3. Sample data from each table
    print("\n" + "="*50)
    print("📄 SAMPLE DATA")
    print("="*50)
    
    print("\n🏢 Sample Companies:")
    companies = client.get_sample_data('companies', 3)
    print(companies.to_string(index=False))
    
    print("\n🏭 Sample Warehouses:")
    warehouses = client.get_sample_data('warehouses', 3)
    print(warehouses.to_string(index=False))
    
    print("\n💱 Sample Exchanges:")
    exchanges = client.get_sample_data('exchanges', 3)
    # Show only key columns for readability
    key_cols = ['exchange_id', 'item_type', 'commodity_standard', 'quantity', 'price_paid_usd', 'timestamp']
    print(exchanges[key_cols].to_string(index=False))
    
    # 4. Filtered queries
    print("\n" + "="*50)
    print("🔍 FILTERED QUERIES")
    print("="*50)
    
    # Find wheat exchanges
    print("\n🌾 Wheat Exchanges (Top 5):")
    wheat = client.find('exchanges', {'item_type': 'Wheat'}, limit=5, order_by='price_paid_usd', order_desc=True)
    if len(wheat) > 0:
        print(wheat[['item_type', 'quantity', 'unit', 'price_paid_usd', 'timestamp']].to_string(index=False))
    else:
        print("No wheat exchanges found")
    
    # Find high-value trades
    print("\n💰 High-Value Trades (>$100k):")
    expensive = client.find('exchanges', {'price_paid_usd__gte': 100000}, limit=5, order_by='price_paid_usd', order_desc=True)
    if len(expensive) > 0:
        print(expensive[['item_type', 'commodity_standard', 'price_paid_usd', 'from_warehouse', 'to_warehouse']].to_string(index=False))
    else:
        print("No high-value trades found")
    
    # Find recent trades
    print("\n📅 Recent Trades (Last 5):")
    recent = client.find('exchanges', limit=5, order_by='timestamp', order_desc=True)
    if len(recent) > 0:
        print(recent[['timestamp', 'item_type', 'price_paid_usd', 'brand_manufacturer']].to_string(index=False))
    
    # 5. Aggregation queries with raw SQL
    print("\n" + "="*50)
    print("📊 ANALYTICS QUERIES")
    print("="*50)
    
    # Trade volume by commodity
    print("\n📈 Trade Volume by Commodity:")
    volume_query = """
        SELECT 
            item_type,
            COUNT(*) as trade_count,
            SUM(price_paid_usd) as total_value,
            AVG(price_paid_usd) as avg_value
        FROM exchanges 
        GROUP BY item_type 
        ORDER BY total_value DESC
        LIMIT 10
    """
    volume_data = client.execute_sql(volume_query)
    if len(volume_data) > 0:
        # Format currency columns
        volume_data['total_value'] = volume_data['total_value'].apply(lambda x: f"${x:,.0f}")
        volume_data['avg_value'] = volume_data['avg_value'].apply(lambda x: f"${x:,.0f}")
        print(volume_data.to_string(index=False))
    
    # Monthly trade patterns
    print("\n📅 Monthly Trade Patterns:")
    monthly_query = """
        SELECT 
            EXTRACT(YEAR FROM timestamp) as year,
            EXTRACT(MONTH FROM timestamp) as month,
            COUNT(*) as trades,
            SUM(price_paid_usd) as total_value
        FROM exchanges 
        GROUP BY 1, 2 
        ORDER BY 1, 2
        LIMIT 12
    """
    monthly_data = client.execute_sql(monthly_query)
    if len(monthly_data) > 0:
        monthly_data['total_value'] = monthly_data['total_value'].apply(lambda x: f"${x:,.0f}")
        print(monthly_data.to_string(index=False))
    
    # 6. Specialized search functions
    print("\n" + "="*50)
    print("🎯 SPECIALIZED SEARCHES")
    print("="*50)
    
    # Search for specific commodity in date range
    print("\n🔍 Steel trades in 2023:")
    steel_2023 = client.search_exchanges(
        commodity_type='Steel',
        start_date='2023-01-01',
        end_date='2023-12-31',
        min_price=50000,
        limit=5
    )
    if len(steel_2023) > 0:
        print(steel_2023[['timestamp', 'quantity', 'unit', 'price_paid_usd']].to_string(index=False))
    else:
        print("No steel trades found in 2023")
    
    # 7. Count examples
    print("\n" + "="*50)
    print("🔢 COUNT EXAMPLES")
    print("="*50)
    
    total_exchanges = client.count('exchanges')
    wheat_count = client.count('exchanges', {'item_type': 'Wheat'})
    expensive_count = client.count('exchanges', {'price_paid_usd__gte': 100000})
    
    print(f"📊 Total exchanges: {total_exchanges:,}")
    print(f"🌾 Wheat exchanges: {wheat_count:,}")
    print(f"💰 Expensive trades (>$100k): {expensive_count:,}")
    
    # 8. Tips for workshop participants
    print("\n" + "="*50)
    print("💡 TIPS FOR WORKSHOP PARTICIPANTS")
    print("="*50)
    print("""
🎯 Key Methods to Use:
    • client.find(table, filters, limit=10) - Find records with filters
    • client.count(table, filters) - Count matching records  
    • client.execute_sql(query) - Run custom SQL
    • client.search_exchanges(...) - Specialized exchange search
    
🔍 Filter Examples:
    • {'item_type': 'Wheat'} - Exact match
    • {'price_paid_usd__gte': 100000} - Greater than or equal
    • {'timestamp__gte': '2023-01-01'} - Date filtering
    • {'country__in': ['USA', 'China']} - Multiple values
    
📊 Great Questions to Explore:
    • Which commodities have the highest seasonal price variation?
    • What are the biggest FIFO opportunities (buy low, sell high)?
    • Which companies/warehouses are most active?
    • Are there unusual trading patterns that might indicate errors?
    """)
    
    print("\n🎉 Demo completed! Happy exploring! 🎉")

if __name__ == "__main__":
    main()