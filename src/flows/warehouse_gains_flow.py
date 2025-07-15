"""
Warehouse Gains Flow

Top-level orchestration for warehouse gains analysis.
Handles data fetching, business logic execution, and result persistence.
"""

import os
from typing import Optional, Iterator
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
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
    exchanges = fetch_warehouse_exchanges(warehouse_id, client)

    # Call business logic to calculate gains
    report = calculate_warehouse_gains(
        warehouse_id=warehouse_id,
        exchanges=exchanges,
        analysis_date=datetime.now(),
        reporter_name=get_reporter_name()
    )
    
    return report


def fetch_warehouse_exchanges(warehouse_id: str, client: SupabaseClient) -> Iterator[Exchange]:

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
    if len(inflows) > 0 and len(outflows) > 0:
        all_exchanges = pd.concat([inflows, outflows], ignore_index=True)
    elif len(inflows) > 0:
        all_exchanges = inflows
    elif len(outflows) > 0:
        all_exchanges = outflows
    else:
        all_exchanges = pd.DataFrame()
    
    return dataframe_to_exchange_iterator(all_exchanges)


def dataframe_to_exchange_iterator(exchanges_df: pd.DataFrame) -> Iterator[Exchange]:

    for _, row in exchanges_df.iterrows():
        # Convert DataFrame row to Exchange object
        exchange_data = {
            'exchange_id': row['exchange_id'],
            'from_warehouse': row['from_warehouse'],
            'to_warehouse': row['to_warehouse'],
            'brand_manufacturer': row['brand_manufacturer'],
            'item_type': row['item_type'],
            'commodity_standard': CommodityStandard(row['commodity_standard']),  # Convert to enum
            'quantity': Decimal(str(row['quantity'])),
            'unit': row['unit'],
            'price_paid_usd': Decimal(str(row['price_paid_usd'])),
            'timestamp': pd.to_datetime(row['timestamp']),
            'batch_id': row.get('batch_id'),
            'item_ids': row.get('item_ids')
        }
        
        yield Exchange(**exchange_data)
