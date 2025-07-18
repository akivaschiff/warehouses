from dataclasses import dataclass
from typing import List
from datetime import datetime
from decimal import Decimal


@dataclass
class CommodityGains:
    """Gains/losses for a specific commodity type"""

    commodity_type: str  # e.g., "Wheat", "Steel"
    total_inflow_cost: Decimal  # Money spent buying this commodity
    total_outflow_value: Decimal  # Money received selling this commodity
    total_gain_loss: Decimal  # outflow_value - inflow_cost
    number_of_transactions: int


@dataclass
class GainReport:
    """Simple inflow/outflow gains report for a warehouse"""

    warehouse_id: str
    reporter_name: str
    analysis_date: datetime

    total_inflow_cost: Decimal  # Total money spent on purchases
    total_outflow_value: Decimal  # Total money received from sales
    total_gain_loss: Decimal  # total_outflow_value - total_inflow_cost
    total_transactions: int

    gains_by_commodity: List[CommodityGains]
