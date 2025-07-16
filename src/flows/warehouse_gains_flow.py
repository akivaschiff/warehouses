"""
Warehouse Gains Flow

Top-level orchestration for warehouse gains analysis.
Handles data fetching, business logic execution, and result persistence.
"""

import os
from typing import Optional, Iterator
from datetime import datetime
from dotenv import load_dotenv
from decimal import Decimal

from src.database.supabase_client import SupabaseClient
from src.logic.gains_calculator import calculate_warehouse_gains
from src.models.gain_report import GainReport
from src.models.exchange import Exchange, CommodityStandard
from src.utils.utils import get_reporter_name

# Load environment variables
load_dotenv()


def analyze_warehouse_gains(
    warehouse_id: str,
    client: SupabaseClient,
) -> GainReport:
    
    # Validate warehouse exists
    warehouse_check = client.find('warehouses', {'warehouse_id': warehouse_id})
    if len(warehouse_check) == 0:
        raise ValueError(f"Warehouse {warehouse_id} not found")
    
    # Fetch ALL exchanges involving this warehouse (bulk commodities only)
    exchanges = _fetch_warehouse_exchanges(warehouse_id, client)

    # Call business logic to calculate gains
    report = calculate_warehouse_gains(
        warehouse_id=warehouse_id,
        exchanges=exchanges,
        analysis_date=datetime.now(),
        reporter_name=get_reporter_name()
    )
    
    return report


def _fetch_warehouse_exchanges(warehouse_id: str, client: SupabaseClient) -> Iterator[Exchange]:

    # Fetch INFLOWS (purchases) - money going OUT, commodities coming IN
    inflows = client.find('exchanges', {
        'to_warehouse': warehouse_id,
        'commodity_standard': 'bulk'
    })
    
    # Fetch OUTFLOWS (sales) - commodities going OUT, money coming IN  
    outflows = client.find('exchanges', {
        'from_warehouse': warehouse_id,
        'commodity_standard': 'bulk'
    })
    
    # Combine all exchanges
    all_exchanges = inflows + outflows
    
    return [Exchange(**exchange_dict) for exchange_dict in all_exchanges]
