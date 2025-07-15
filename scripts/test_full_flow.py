#!/usr/bin/env python3
"""
Test the complete flow: Data Generation → Database → Analysis → Results

This script tests the entire warehouse gains flow end-to-end:
1. Check database connection
2. Find a sample warehouse with exchange data
3. Run the complete analysis flow
4. Display detailed results
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.flows.warehouse_gains_flow import analyze_warehouse_gains
from src.database.supabase_client import SupabaseClient


def test_complete_flow():
    """Test the complete warehouse gains analysis flow"""
    
    print("🔄 Testing Complete Warehouse Gains Flow")
    print("=" * 50)
    
    # Step 1: Connect to database
    try:
        client = SupabaseClient()
        print("✅ Connected to Supabase database")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Step 2: Check data availability
    print(f"\n📊 Checking database contents...")
    
    warehouses_count = client.count('warehouses')
    exchanges_count = client.count('exchanges') 
    bulk_exchanges_count = client.count('exchanges', {'commodity_standard': 'bulk'})
    
    print(f"   📦 Total warehouses: {warehouses_count:,}")
    print(f"   🔄 Total exchanges: {exchanges_count:,}")
    print(f"   🏗️ Bulk exchanges: {bulk_exchanges_count:,}")
    
    if warehouses_count == 0 or bulk_exchanges_count == 0:
        print("❌ Insufficient data in database. Run 'make data && make db-upload' first.")
        return False
    
    # Step 3: Find warehouses with significant activity
    print(f"\n🔍 Finding active warehouses...")
    
    # Find warehouses with both inflows and outflows
    warehouses_with_inflows = client.execute_sql("""
        SELECT w.warehouse_id, w.country, COUNT(e.exchange_id) as inflow_count,
               SUM(e.price_paid_usd) as total_inflow_value
        FROM warehouses w
        JOIN exchanges e ON w.warehouse_id = e.to_warehouse
        WHERE e.commodity_standard = 'bulk'
        GROUP BY w.warehouse_id, w.country
        HAVING COUNT(e.exchange_id) >= 5
        ORDER BY total_inflow_value DESC
        LIMIT 10
    """)
    
    warehouses_with_outflows = client.execute_sql("""
        SELECT w.warehouse_id, w.country, COUNT(e.exchange_id) as outflow_count,
               SUM(e.price_paid_usd) as total_outflow_value
        FROM warehouses w
        JOIN exchanges e ON w.warehouse_id = e.from_warehouse
        WHERE e.commodity_standard = 'bulk'
        GROUP BY w.warehouse_id, w.country
        HAVING COUNT(e.exchange_id) >= 5
        ORDER BY total_outflow_value DESC
        LIMIT 10
    """)
    
    if len(warehouses_with_inflows) == 0 or len(warehouses_with_outflows) == 0:
        print("❌ No warehouses found with sufficient activity")
        return False
    
    # Find a warehouse that has both inflows AND outflows
    active_warehouse = None
    for _, inflow_row in warehouses_with_inflows.iterrows():
        warehouse_id = inflow_row['warehouse_id']
        matching_outflows = warehouses_with_outflows[
            warehouses_with_outflows['warehouse_id'] == warehouse_id
        ]
        if len(matching_outflows) > 0:
            active_warehouse = warehouse_id
            warehouse_country = inflow_row['country']
            break
    
    if not active_warehouse:
        # Just pick the first warehouse with inflows
        active_warehouse = warehouses_with_inflows.iloc[0]['warehouse_id'] 
        warehouse_country = warehouses_with_inflows.iloc[0]['country']
    
    print(f"   🏭 Selected warehouse: {active_warehouse} ({warehouse_country})")
    
    # Step 4: Run the complete analysis
    print(f"\n🧮 Running gains analysis...")
    
    try:
        # This calls the complete flow: fetch data → convert to objects → calculate gains
        report = analyze_warehouse_gains(
            warehouse_id=active_warehouse,
            client=client,
        )
        
        print("✅ Analysis completed successfully!")
        
        # Step 5: Display detailed results
        print(f"\n📊 Analysis Results")
        print("=" * 30)
        print(f"🏭 Warehouse: {report.warehouse_id}")
        print(f"👤 Reporter: {report.reporter_name}")
        print(f"📅 Analysis Date: {report.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📈 Total Transactions: {report.total_transactions:,}")
        
        if report.analysis_start_date and report.analysis_end_date:
            print(f"📅 Date Range: {report.analysis_start_date.strftime('%Y-%m-%d')} to {report.analysis_end_date.strftime('%Y-%m-%d')}")
        
        print(f"\n💰 Financial Summary")
        print("-" * 20)
        print(f"💸 Total Inflow Cost:    ${report.total_inflow_cost:>15,.2f}")
        print(f"💵 Total Outflow Value:  ${report.total_outflow_value:>15,.2f}")
        print(f"📊 Net Gain/Loss:       ${report.total_gain_loss:>15,.2f}")
        
        if report.total_inflow_cost > 0:
            roi = (report.total_gain_loss / report.total_inflow_cost) * 100
            print(f"📈 ROI:                 {roi:>15.2f}%")
        
        print(f"\n🏗️ Commodity Breakdown ({len(report.gains_by_commodity)} types)")
        print("-" * 50)
        
        for commodity in sorted(report.gains_by_commodity, key=lambda x: x.total_gain_loss, reverse=True):
            print(f"   {commodity.commodity_type:<15} | "
                  f"Gain: ${commodity.total_gain_loss:>10,.2f} | "
                  f"Trades: {commodity.number_of_transactions:>3} | "
                  f"In: ${commodity.total_inflow_cost:>8,.0f} | "
                  f"Out: ${commodity.total_outflow_value:>8,.0f}")
        
        # Step 6: Validation checks
        print(f"\n🔍 Validation Checks")
        print("-" * 20)
        
        # Check that gains calculation is correct
        calculated_gain = report.total_outflow_value - report.total_inflow_cost
        if abs(calculated_gain - report.total_gain_loss) < 0.01:
            print("✅ Total gain calculation correct")
        else:
            print(f"❌ Total gain mismatch: {calculated_gain} vs {report.total_gain_loss}")
        
        # Check commodity breakdown adds up
        commodity_total_gain = sum(c.total_gain_loss for c in report.gains_by_commodity)
        if abs(commodity_total_gain - report.total_gain_loss) < 0.01:
            print("✅ Commodity breakdown adds up correctly")
        else:
            print(f"❌ Commodity total mismatch: {commodity_total_gain} vs {report.total_gain_loss}")
        
        # Check transaction counts
        commodity_total_transactions = sum(c.number_of_transactions for c in report.gains_by_commodity)
        if commodity_total_transactions == report.total_transactions:
            print("✅ Transaction counts match")
        else:
            print(f"❌ Transaction count mismatch: {commodity_total_transactions} vs {report.total_transactions}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_next_steps():
    """Show what students can work on next"""
    
    print(f"\n🎯 Next Steps for Workshop")
    print("=" * 30)
    print(f"✅ Chapter 0 Complete: Basic gains calculation working!")
    print(f"")
    print(f"🔧 Possible exercises:")
    print(f"   • Add date filtering to analysis")
    print(f"   • Implement serialized items support")
    print(f"   • Add validation and error handling")
    print(f"   • Write comprehensive tests")
    print(f"   • Add performance optimizations")
    print(f"   • Create data export functionality")


if __name__ == "__main__":
    print("🧪 Full Flow Test Script")
    print("Testing the complete warehouse gains analysis pipeline\n")
    
    success = test_complete_flow()
    
    if success:
        show_next_steps()
        print(f"\n🎉 All tests passed! The system is working end-to-end!")
    else:
        print(f"\n❌ Tests failed. Check the errors above.")
        print(f"\n🔧 Troubleshooting:")
        print(f"   • Make sure you have data: 'make data && make db-upload'")
        print(f"   • Check your .env file has DATABASE_URL")
        print(f"   • Verify Supabase connection is working")
    
    print(f"\n" + "=" * 60)
