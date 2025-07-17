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

from src.flows.verify_env import verify_env_setup
from src.flows.warehouse_gains_flow import analyze_warehouse_gains, get_reporter_name
from src.database.supabase_client import SupabaseClient


def test_new_flow_structure(warehouse_id: str):

    print("=" * 50)
    print("🏗️ Testing main Flow")
    print("=" * 50)

    # Test reporter name from environment
    reporter = get_reporter_name()
    print(f"📊 Reporter Name: {reporter}")

    client = SupabaseClient()

    print(f"🏭 Running Flow with: {warehouse_id}")
    print("=" * 50)

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
        print(f"   Commodity Breakdown: {len(report.gains_by_commodity)} types")

        # Show commodity breakdown
        for commodity in report.gains_by_commodity:
            print(
                f"     • {commodity.commodity_type}: ${commodity.total_gain_loss:,.2f} ({commodity.number_of_transactions} transactions)"
            )

    except ValueError as e:
        print(f"❌ Validation Error: {e}")
    except NotImplementedError:
        print(
            "⚠️ Business logic not implemented yet - this is expected!"
        )
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Callstack:")
        traceback.print_exc()

    print(f"\n" + "=" * 50)
    print("🎯 Flow run completed!")


if __name__ == "__main__":
    try:
        verify_env_setup()
        test_new_flow_structure("WH_30f6fae4")
    except (EnvironmentError, ConnectionError) as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
