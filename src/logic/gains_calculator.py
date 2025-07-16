from datetime import datetime

from src.models.gain_report import GainReport, CommodityGains
from src.models.exchange import Exchange


def calculate_warehouse_gains(
    warehouse_id: str,
    exchanges: list[Exchange],
    analysis_date: datetime,
    reporter_name: str = "Unknown Reporter"
) -> GainReport:
    from decimal import Decimal
    from collections import defaultdict
    
    # Initialize tracking variables
    total_inflow_cost = Decimal('0')
    total_outflow_value = Decimal('0')
    total_transactions = 0
    
    # Track by commodity type
    commodity_inflows = defaultdict(Decimal)  # commodity -> total cost
    commodity_outflows = defaultdict(Decimal)  # commodity -> total value
    commodity_transaction_counts = defaultdict(int)  # commodity -> count
    
    # Process all exchanges
    for exchange in exchanges:
        # Filter for bulk commodities only (Chapter 0 scope)
        if not exchange.is_bulk():
            continue
            
        # Check if this exchange involves our warehouse
        if not exchange.is_relevant_for(warehouse_id):
            continue
            
        # Determine if this is an inflow (purchase) or outflow (sale)
        if exchange.is_inflow_for(warehouse_id):
            # INFLOW: Money going OUT, commodities coming IN
            # This warehouse is buying commodities
            total_inflow_cost += exchange.price_paid_usd
            commodity_inflows[exchange.item_type] += exchange.price_paid_usd
            commodity_transaction_counts[exchange.item_type] += 1
            total_transactions += 1
            
        elif exchange.is_outflow_for(warehouse_id):
            # OUTFLOW: Commodities going OUT, money coming IN
            # This warehouse is selling commodities
            total_outflow_value += exchange.price_paid_usd
            commodity_outflows[exchange.item_type] += exchange.price_paid_usd
            commodity_transaction_counts[exchange.item_type] += 1
            total_transactions += 1
    
    # Calculate total gain/loss
    total_gain_loss = total_outflow_value - total_inflow_cost
    
    # Build commodity breakdown
    gains_by_commodity = []
    all_commodities = set(commodity_inflows.keys()) | set(commodity_outflows.keys())
    
    for commodity_type in sorted(all_commodities):
        inflow_cost = commodity_inflows[commodity_type]
        outflow_value = commodity_outflows[commodity_type]
        gain_loss = outflow_value - inflow_cost
        transaction_count = commodity_transaction_counts[commodity_type]
        
        commodity_gains = CommodityGains(
            commodity_type=commodity_type,
            total_inflow_cost=inflow_cost,
            total_outflow_value=outflow_value,
            total_gain_loss=gain_loss,
            number_of_transactions=transaction_count
        )
        gains_by_commodity.append(commodity_gains)
    
    # Set analysis date
    if analysis_date is None:
        analysis_date = datetime.now()
    
    # Build and return the report
    return GainReport(
        warehouse_id=warehouse_id,
        reporter_name=reporter_name,
        analysis_date=analysis_date,
        total_inflow_cost=total_inflow_cost,
        total_outflow_value=total_outflow_value,
        total_gain_loss=total_gain_loss,
        total_transactions=total_transactions,
        gains_by_commodity=gains_by_commodity,
    )
