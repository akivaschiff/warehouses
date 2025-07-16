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
    
    return _dict_list_to_exchange_iterator(all_exchanges)


def _dict_list_to_exchange_iterator(exchanges_list: list) -> Iterator[Exchange]:

    for exchange_dict in exchanges_list:
        exchange_data = {
            'exchange_id': exchange_dict['exchange_id'],
            'from_warehouse': exchange_dict['from_warehouse'],
            'to_warehouse': exchange_dict['to_warehouse'],
            'brand_manufacturer': exchange_dict['brand_manufacturer'],
            'item_type': exchange_dict['item_type'],
            'commodity_standard': CommodityStandard(exchange_dict['commodity_standard']),  # Convert to enum
            'quantity': Decimal(str(exchange_dict['quantity'])),
            'unit': exchange_dict['unit'],
            'price_paid_usd': Decimal(str(exchange_dict['price_paid_usd'])),
            'timestamp': exchange_dict['timestamp'],  # Already a datetime object
            'batch_id': exchange_dict.get('batch_id'),
            'item_ids': exchange_dict.get('item_ids')
        }
        
        yield Exchange(**exchange_data)
