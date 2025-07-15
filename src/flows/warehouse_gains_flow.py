"""
Warehouse Gains Flow

Top-level orchestration for warehouse gains analysis.
Handles data fetching, business logic execution, and result persistence.
"""

import os
from typing import Optional, Iterator, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

from src.database.supabase_client import SupabaseClient
from src.logic.gains_calculator import calculate_warehouse_gains
from src.models.gain_report import GainReport

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
    2. Calls business logic to calculate gains
    3. Optionally saves the report to database
    
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
    
    # Fetch ALL exchanges involving this warehouse (interchangeable commodities only)
    all_exchanges = fetch_warehouse_exchanges(warehouse_id, client)
    
    # Convert to iterator of exchange dictionaries
    exchanges_iterator = exchanges_to_iterator(all_exchanges)
    
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
        'commodity_standard': 'interchangeable'
    })
    
    # Fetch OUTFLOWS (sales) - commodities going OUT, money coming IN  
    outflows = client.find('exchanges', {
        'from_warehouse': warehouse_id,
        'commodity_standard': 'interchangeable'
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


def exchanges_to_iterator(exchanges_df: pd.DataFrame) -> Iterator[Dict[str, Any]]:
    """
    Convert DataFrame of exchanges to iterator of dictionaries.
    
    Args:
        exchanges_df: DataFrame with exchange data
        
    Returns:
        Iterator yielding exchange dictionaries
    """
    for _, row in exchanges_df.iterrows():
        yield row.to_dict()


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