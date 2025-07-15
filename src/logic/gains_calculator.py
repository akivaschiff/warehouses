"""
Simple Warehouse Gains Calculator

Chapter 0: Basic inflow/outflow analysis for bulk commodities only.
Pure business logic - no database dependencies.
"""

from typing import Iterator, Optional
from datetime import datetime

from src.models.gain_report import GainReport, CommodityGains
from src.models.exchange import Exchange


def calculate_warehouse_gains(
    warehouse_id: str,
    exchanges: Iterator[Exchange],
    analysis_date: Optional[datetime] = None,
    reporter_name: str = "Unknown Reporter"
) -> GainReport:
    """
    Calculate simple inflow/outflow gains for a warehouse.
    
    Pure logic function - takes an iterator of Exchange objects, returns GainReport.
    No database dependencies.
    
    Chapter 0 scope:
    - Only bulk commodities (wheat, steel, oil, etc.)
    - Simple calculation: total_outflow_value - total_inflow_cost = gain/loss
    - Breakdown by commodity type (wheat vs steel vs oil)
    - Analyzes entire time period (no date filtering)
    
    Args:
        warehouse_id: The warehouse ID being analyzed
        exchanges: Iterator of Exchange objects (both inflows and outflows)
        analysis_date: When this analysis was performed
        reporter_name: Who generated this report
        
    Returns:
        GainReport: Simple gains analysis with inflow/outflow totals and 
                   breakdown by commodity type
    """
    # TODO: Implementation goes here
    # 
    # Business logic should:
    # 1. Iterate through exchanges
    # 2. Filter for bulk commodities only
    # 3. Separate inflows (exchange.is_inflow_for(warehouse_id)) from outflows
    # 4. Sum costs and proceeds by commodity type  
    # 5. Calculate gains: proceeds - costs
    # 6. Return populated GainReport
    pass
