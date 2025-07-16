from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class CommodityStandard(str, Enum):
    BULK = "bulk"  # Bulk commodities like wheat, oil, steel


class Exchange(BaseModel):
    exchange_id: str = Field(..., description="Unique identifier for this exchange")
    from_warehouse: str = Field(..., description="Source warehouse ID")
    to_warehouse: str = Field(..., description="Destination warehouse ID")
    brand_manufacturer: str = Field(..., description="Who creates/licenses the item")
    item_type: str = Field(..., description="Category: 'Wheat', 'Steel', 'Art', etc.")
    commodity_standard: CommodityStandard = Field(..., description="Type of commodity standard")
    quantity: Decimal = Field(..., description="Amount being transferred")
    unit: str = Field(..., description="'tons', 'gallons', 'pieces', etc.")
    price_paid_usd: Decimal = Field(..., description="USD amount exchanged")
    timestamp: datetime = Field(..., description="When exchange occurred")
    class Config:
        """Pydantic configuration"""

        # Allow using Decimal types
        arbitrary_types_allowed = True
        # Validate assignment after creation
        validate_assignment = True
        # Use enum values for serialization
        use_enum_values = True

        # Example for documentation
        json_schema_extra = {
            "example": {
                "exchange_id": "EX001",
                "from_warehouse": "WH_A12345",
                "to_warehouse": "WH_B67890",
                "brand_manufacturer": "Cargill",
                "item_type": "Wheat",
                "commodity_standard": "bulk",
                "quantity": "100.5",
                "unit": "tons",
                "price_paid_usd": "5025.00",
                "timestamp": "2023-06-15T10:30:00Z",
            }
        }
