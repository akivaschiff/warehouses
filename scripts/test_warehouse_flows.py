#!/usr/bin/env python3
"""
Test the new warehouse gains flow structure

This script tests the orchestration layer (flows) that coordinates
data fetching, business logic, and result persistence.
"""

import sys
import os
import traceback

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.flows.warehouse_gains_flow import analyze_warehouse_gains, get_reporter_name
from src.database.supabase_client import SupabaseClient


def test_new_flow_structure():
    """Test the new flows/logic separation"""
    
    print("🏗️ Testing New Flow Structure")
    print("=" * 50)
    
    # Test reporter name from environment
    reporter = get_reporter_name()
    print(f"📊 Reporter Name: {reporter}")
    
    # Get sample warehouses
    print("\n📋 Finding sample warehouses...")
    client = SupabaseClient()
    warehouses = client.find('warehouses', limit=5)
    
    if len(warehouses) == 0:
        print("❌ No warehouses found in database")
        return
    # Test the flow with a sample warehouse
    warehouse_id = warehouses.iloc[0].get('warehouse_id')
    warehouse_country = warehouses.iloc[0].get('country', 'Unknown')
    
    print(f"\n🏭 Testing Flow with: {warehouse_id} ({warehouse_country})")
    print("-" * 40)
    
    try:
        # Use the new orchestration flow (simplified signature)
        report = analyze_warehouse_gains(
            warehouse_id=warehouse_id,
            client=client,
        )
        
        # Display results
        print(f"📊 Flow Results:")
        print(f"   Warehouse: {report.warehouse_id}")
        print(f"   Reporter: {report.reporter_name}")
        print(f"   Analysis Date: {report.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Total Transactions: {report.total_transactions}")
        print(f"   Total Inflow Cost: ${report.total_inflow_cost:,.2f}")
        print(f"   Total Outflow Value: ${report.total_outflow_value:,.2f}")
        print(f"   Total Gain/Loss: ${report.total_gain_loss:,.2f}")
        
        if report.analysis_start_date and report.analysis_end_date:
            print(f"   Date Range: {report.analysis_start_date.strftime('%Y-%m-%d')} to {report.analysis_end_date.strftime('%Y-%m-%d')}")
        
        print(f"   Commodity Breakdown: {len(report.gains_by_commodity)} types")
        
        # Show commodity breakdown
        for commodity in report.gains_by_commodity:
            print(f"     • {commodity.commodity_type}: ${commodity.total_gain_loss:,.2f} ({commodity.number_of_transactions} transactions)")
    
    except ValueError as e:
        print(f"❌ Validation Error: {e}")
    except NotImplementedError:
        print("⚠️ Business logic not implemented yet - this is expected for Chapter 0 setup")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Callstack:")
        traceback.print_exc()
    
    print(f"\n" + "=" * 50)
    print("🎯 Flow structure test completed!")
    
    print(f"\n💡 Architecture Notes:")
    print(f"   • src/flows/ = Orchestration layer (DB fetch → logic → DB save)")
    print(f"   • src/logic/ = Pure business logic (no DB dependencies)")
    print(f"   • src/models/ = Data structures")
    print(f"   • src/database/ = Data access layer")


def verify_env_setup():
    """Verify environment setup and database connection"""
    
    print(f"\n🔧 Environment Setup:")
    print("=" * 30)
    
    database_url = os.getenv('DATABASE_URL')
    reporter_name = os.getenv('REPORTER_NAME')
    
    print(f"DATABASE_URL: {'✅ Set' if database_url else '❌ Missing'}")
    print(f"REPORTER_NAME: {'✅ Set' if reporter_name else '❌ Missing'}")
    
    # Check for missing required environment variables
    missing_vars = []
    if not database_url:
        missing_vars.append('DATABASE_URL')
    if not reporter_name:
        missing_vars.append('REPORTER_NAME')
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        print(f"\n❌ {error_msg}")
        if 'REPORTER_NAME' in missing_vars:
            print(f"\n💡 To set reporter name, add to your .env file:")
            print(f"   REPORTER_NAME=Your_Name_Here")
        raise EnvironmentError(error_msg)
    
    # Test database connection
    try:
        SupabaseClient()
        print("✅ Database connection successful")
    except Exception as e:
        error_msg = f"Database connection failed: {e}"
        print(f"\n❌ {error_msg}")
        raise ConnectionError(error_msg)


if __name__ == "__main__":
    try:
        verify_env_setup()
        test_new_flow_structure()
    except (EnvironmentError, ConnectionError) as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
