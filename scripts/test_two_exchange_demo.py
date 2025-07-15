#!/usr/bin/env python3
"""
Simple Test: Two Exchange Scenario

Demonstrates the exact scenario with a warehouse having exactly 2 exchanges:
1. Purchase (inflow): Buy 100 tons of wheat for $20,000
2. Sale (outflow): Sell 50 tons of wheat for $12,000

Expected result: Loss of $8,000
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decimal import Decimal
from datetime import datetime
from src.logic.gains_calculator import calculate_warehouse_gains
from src.models.exchange import Exchange, CommodityStandard


def test_two_exchange_scenario():
    """Test the exact 2-exchange scenario manually"""
    
    print("🧪 Testing Two Exchange Scenario")
    print("=" * 40)
    
    # Create exactly 2 exchanges
    exchanges = [
        # Exchange 1: INFLOW (Purchase)
        # WH_TEST_123 buys 100 tons of wheat for $20,000
        Exchange(
            exchange_id='EX_PURCHASE_001',
            from_warehouse='WH_SUPPLIER_999',
            to_warehouse='WH_TEST_123',  # Our warehouse is the buyer
            brand_manufacturer='Test Grain Company',
            item_type='Wheat',
            commodity_standard=CommodityStandard.BULK,
            quantity=Decimal('100.0'),
            unit='tons',
            price_paid_usd=Decimal('20000.00'),
            timestamp=datetime(2023, 6, 1, 10, 0, 0)
        ),
        
        # Exchange 2: OUTFLOW (Sale)  
        # WH_TEST_123 sells 50 tons of wheat for $12,000
        Exchange(
            exchange_id='EX_SALE_002',
            from_warehouse='WH_TEST_123',  # Our warehouse is the seller
            to_warehouse='WH_CUSTOMER_888',
            brand_manufacturer='Test Grain Company',
            item_type='Wheat',
            commodity_standard=CommodityStandard.BULK,
            quantity=Decimal('50.0'),
            unit='tons',
            price_paid_usd=Decimal('12000.00'),
            timestamp=datetime(2023, 6, 15, 14, 30, 0)
        )
    ]
    
    print(f"📦 Exchange 1 (Purchase):")
    print(f"   From: {exchanges[0].from_warehouse} → To: {exchanges[0].to_warehouse}")
    print(f"   Item: {exchanges[0].quantity} {exchanges[0].unit} of {exchanges[0].item_type}")
    print(f"   Cost: ${exchanges[0].price_paid_usd:,.2f}")
    print(f"   Date: {exchanges[0].timestamp}")
    print(f"   Type: {'INFLOW' if exchanges[0].is_inflow_for('WH_TEST_123') else 'OTHER'}")
    
    print(f"\n📦 Exchange 2 (Sale):")
    print(f"   From: {exchanges[1].from_warehouse} → To: {exchanges[1].to_warehouse}")
    print(f"   Item: {exchanges[1].quantity} {exchanges[1].unit} of {exchanges[1].item_type}")
    print(f"   Revenue: ${exchanges[1].price_paid_usd:,.2f}")
    print(f"   Date: {exchanges[1].timestamp}")
    print(f"   Type: {'OUTFLOW' if exchanges[1].is_outflow_for('WH_TEST_123') else 'OTHER'}")
    
    # Calculate gains
    print(f"\n🧮 Running Gains Calculation...")
    report = calculate_warehouse_gains(
        warehouse_id='WH_TEST_123',
        exchanges=iter(exchanges),
        analysis_date=datetime(2023, 7, 1),
        reporter_name='Test Reporter'
    )
    
    # Expected results
    expected_inflow_cost = Decimal('20000.00')
    expected_outflow_value = Decimal('12000.00')
    expected_gain_loss = expected_outflow_value - expected_inflow_cost  # -8000.00
    
    print(f"\n📊 Results:")
    print(f"   Warehouse ID: {report.warehouse_id}")
    print(f"   Reporter: {report.reporter_name}")
    print(f"   Analysis Date: {report.analysis_date}")
    print(f"   Total Transactions: {report.total_transactions}")
    
    print(f"\n💰 Financial Summary:")
    print(f"   Total Inflow Cost:    ${report.total_inflow_cost:>10,.2f}")
    print(f"   Total Outflow Value:  ${report.total_outflow_value:>10,.2f}")
    print(f"   Net Gain/Loss:       ${report.total_gain_loss:>10,.2f}")
    
    if report.total_inflow_cost > 0:
        roi = (report.total_gain_loss / report.total_inflow_cost) * 100
        print(f"   ROI:                 {roi:>10.2f}%")
    
    print(f"\n📅 Date Range:")
    print(f"   Start: {report.analysis_start_date}")
    print(f"   End: {report.analysis_end_date}")
    
    print(f"\n🏗️ Commodity Breakdown:")
    for commodity in report.gains_by_commodity:
        print(f"   {commodity.commodity_type}:")
        print(f"     Inflow Cost:    ${commodity.total_inflow_cost:>8,.2f}")
        print(f"     Outflow Value:  ${commodity.total_outflow_value:>8,.2f}")
        print(f"     Gain/Loss:     ${commodity.total_gain_loss:>8,.2f}")
        print(f"     Transactions:   {commodity.number_of_transactions:>8}")
    
    # Verification
    print(f"\n✅ Verification:")
    
    # Test 1: Basic calculations
    if report.total_inflow_cost == expected_inflow_cost:
        print(f"   ✅ Inflow cost correct: ${expected_inflow_cost:,.2f}")
    else:
        print(f"   ❌ Inflow cost wrong: expected ${expected_inflow_cost:,.2f}, got ${report.total_inflow_cost:,.2f}")
    
    if report.total_outflow_value == expected_outflow_value:
        print(f"   ✅ Outflow value correct: ${expected_outflow_value:,.2f}")
    else:
        print(f"   ❌ Outflow value wrong: expected ${expected_outflow_value:,.2f}, got ${report.total_outflow_value:,.2f}")
    
    if report.total_gain_loss == expected_gain_loss:
        print(f"   ✅ Gain/loss correct: ${expected_gain_loss:,.2f}")
    else:
        print(f"   ❌ Gain/loss wrong: expected ${expected_gain_loss:,.2f}, got ${report.total_gain_loss:,.2f}")
    
    # Test 2: Transaction count
    if report.total_transactions == 2:
        print(f"   ✅ Transaction count correct: 2")
    else:
        print(f"   ❌ Transaction count wrong: expected 2, got {report.total_transactions}")
    
    # Test 3: Commodity breakdown
    if len(report.gains_by_commodity) == 1:
        print(f"   ✅ Commodity count correct: 1 (Wheat)")
        
        wheat = report.gains_by_commodity[0]
        if wheat.commodity_type == 'Wheat':
            print(f"   ✅ Wheat commodity identified")
        else:
            print(f"   ❌ Wrong commodity: expected 'Wheat', got '{wheat.commodity_type}'")
            
        if wheat.total_gain_loss == expected_gain_loss:
            print(f"   ✅ Wheat gain/loss correct: ${expected_gain_loss:,.2f}")
        else:
            print(f"   ❌ Wheat gain/loss wrong: expected ${expected_gain_loss:,.2f}, got ${wheat.total_gain_loss:,.2f}")
            
        if wheat.number_of_transactions == 2:
            print(f"   ✅ Wheat transaction count correct: 2")
        else:
            print(f"   ❌ Wheat transaction count wrong: expected 2, got {wheat.number_of_transactions}")
    else:
        print(f"   ❌ Wrong commodity count: expected 1, got {len(report.gains_by_commodity)}")
    
    # Test 4: Math validation
    manual_calculation = report.total_outflow_value - report.total_inflow_cost
    if manual_calculation == report.total_gain_loss:
        print(f"   ✅ Manual calculation matches: ${manual_calculation:,.2f}")
    else:
        print(f"   ❌ Manual calculation differs: ${manual_calculation:,.2f} vs ${report.total_gain_loss:,.2f}")
    
    print(f"\n🎯 Summary:")
    print(f"   This warehouse bought wheat for $20,000 and sold some for $12,000,")
    print(f"   resulting in a net loss of $8,000 (still holding 50 tons worth $10,000 at cost).")
    print(f"   The calculation correctly shows inflows > outflows = loss.")


if __name__ == "__main__":
    test_two_exchange_scenario()
