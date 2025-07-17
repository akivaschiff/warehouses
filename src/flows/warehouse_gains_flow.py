from datetime import datetime
from contextlib import suppress
from dotenv import load_dotenv

from src.database.supabase_client import SupabaseClient
from src.logic.gains_calculator import calculate_warehouse_gains
from src.models.gain_report import GainReport
from src.models.exchange import Exchange
from src.utils.utils import get_reporter_name

# Load environment variables
load_dotenv()


def analyze_warehouse_gains(
    warehouse_id: str,
    client: SupabaseClient,
) -> GainReport:

    warehouse_check = client.find("warehouses", {"warehouse_id": warehouse_id})
    if len(warehouse_check) == 0:
        raise ValueError(f"Warehouse {warehouse_id} not found")

    exchanges = _fetch_warehouse_exchanges(warehouse_id, client)

    return calculate_warehouse_gains(
        warehouse_id=warehouse_id,
        exchanges=exchanges,
        analysis_date=datetime.now(),
        reporter_name=get_reporter_name(),
    )


def _fetch_warehouse_exchanges(
    warehouse_id: str, client: SupabaseClient
) -> list[Exchange]:

    inflows = client.find(
        "exchanges", {"to_warehouse": warehouse_id}
    )
    outflows = client.find(
        "exchanges", {"from_warehouse": warehouse_id}
    )

    valid_exchanges = []
    for exchange_dict in inflows + outflows:
        with suppress(ValueError):
            exchange = Exchange(**exchange_dict)
            valid_exchanges.append(exchange)

    return valid_exchanges
