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

# Load environment variables
load_dotenv()


def analyze_warehouse_gains(
    warehouse_id: str,
    save_to_db: bool = True,
    client: Optional[SupabaseClient] = None
) -> GainReport:
    """
    Complete warehouse gains analysis flow.
    
    This is the main entry point that:
    1. Fetches all exchange data from database for the warehouse
    2. Converts to Exchange objects
    3. Calls business logic to calculate gains
    4. Optionally saves the report to database
    
    Args:
        warehouse_id: The warehouse ID to analyze
        save_to_db: Whether to save the report to database
        client: Optional SupabaseClient instance
        
    Returns:
        GainReport: Complete gains analysis for entire time period
        
    Raises:
        ValueError: If warehouse_id is invalid or no data found
        ConnectionError: If database connection fails
    """
    # Initialize client if not provided
    if client is None:
        client = SupabaseClient()
    
    # Validate warehouse exists
    warehouse_check = client.find('warehouses', {'warehouse_id': warehouse_id})
    if len(warehouse_check) == 0:
        raise ValueError(f"Warehouse {warehouse_id} not found")
    
    # Fetch ALL exchanges involving this warehouse (bulk commodities only)
    all_exchanges = fetch_warehouse_exchanges(warehouse_id, client)
    
    # Convert to iterator of Exchange objects
    exchanges_iterator = dataframe_to_exchange_iterator(all_exchanges)
    
    # Call business logic to calculate gains
    report = calculate_warehouse_gains(
        warehouse_id=warehouse_id,
        exchanges=exchanges_iterator,
        analysis_date=datetime.now(),
        reporter_name=get_reporter_name()
    )
    
    # Save to database if requested
    if save_to_db:
        save_gain_report(report, client)
    
    return report


def fetch_warehouse_exchanges(warehouse_id: str, client: SupabaseClient) -> pd.DataFrame:
    """
    Fetch all exchanges involving a warehouse.
    
    Args:
        warehouse_id: The warehouse to get exchanges for
        client: SupabaseClient instance
        
    Returns:
        DataFrame with all relevant exchanges (both inflows and outflows)
    """
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
    
    return all_exchanges


def dataframe_to_exchange_iterator(exchanges_df: pd.DataFrame) -> Iterator[Exchange]:
    """
    Convert DataFrame of exchanges to iterator of Exchange objects.
    
    Args:
        exchanges_df: DataFrame with exchange data
        
    Returns:
        Iterator yielding Exchange objects
    """
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


def save_gain_report(report: GainReport, client: SupabaseClient) -> None:
    """
    Save a GainReport to the database.
    
    Args:
        report: The GainReport to save
        client: SupabaseClient instance
    """
    # Convert report to dictionary for database storage
    report_data = {
        'warehouse_id': report.warehouse_id,
        'analysis_date': report.analysis_date.isoformat(),
        'reporter_name': report.reporter_name,
        'total_inflow_cost': float(report.total_inflow_cost),
        'total_outflow_value': float(report.total_outflow_value),
        'total_gain_loss': float(report.total_gain_loss),
        'total_transactions': report.total_transactions,
        'analysis_start_date': report.analysis_start_date.isoformat() if report.analysis_start_date else None,
        'analysis_end_date': report.analysis_end_date.isoformat() if report.analysis_end_date else None,
        # TODO: Add commodity breakdown serialization in later chapters
    }
    
    # TODO: Implement database insertion
    # This would insert into a 'gain_reports' table
    # For now, just print what would be saved
    print(f"📊 Would save GainReport to database:")
    print(f"   Warehouse: {report.warehouse_id}")
    print(f"   Reporter: {report.reporter_name}")
    print(f"   Gain/Loss: ${report.total_gain_loss:,.2f}")
    print(f"   Transactions: {report.total_transactions}")


def get_reporter_name() -> str:
    """
    Get the reporter name from environment variable.
    
    Returns:
        Reporter name from REPORTER_NAME env var, or default
    """
    return os.getenv('REPORTER_NAME', 'Unknown Reporter')
