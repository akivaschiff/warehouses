"""
Exchange Model

Pydantic model representing a warehouse exchange transaction.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class CommodityStandard(str, Enum):
    """Types of commodity standards supported"""
    BULK = "bulk"  # Bulk commodities like wheat, oil, steel


class Exchange(BaseModel):
    """
    A warehouse exchange transaction.
    
    Represents the transfer of money for moving resources/items between warehouses.
    """
    
    exchange_id: str = Field(..., description="Unique identifier for this exchange")
    from_warehouse: str = Field(..., description="Source warehouse ID (or '0x0000' for mint)")
    to_warehouse: str = Field(..., description="Destination warehouse ID (or '0x0000' for burn)")
    brand_manufacturer: str = Field(..., description="Who creates/licenses the item")
    item_type: str = Field(..., description="Category: 'Wheat', 'Steel', 'Art', etc.")
    commodity_standard: CommodityStandard = Field(..., description="Type of commodity standard")
    quantity: Decimal = Field(..., description="Amount being transferred")
    unit: str = Field(..., description="'tons', 'gallons', 'pieces', etc.")
    price_paid_usd: Decimal = Field(..., description="USD amount exchanged")
    timestamp: datetime = Field(..., description="When exchange occurred")
    
    # Optional fields for specific commodity types (future use)
    batch_id: Optional[str] = Field(None, description="For batched items (future)")
    item_ids: Optional[List[str]] = Field(None, description="For serialized items (future)")
    
    def is_inflow_for(self, warehouse_id: str) -> bool:
        """
        Check if this exchange is an inflow (purchase) for the given warehouse.
        
        Args:
            warehouse_id: The warehouse to check against
            
        Returns:
            True if this is money going out, commodities coming in
        """
        return self.to_warehouse == warehouse_id
    
    def is_outflow_for(self, warehouse_id: str) -> bool:
        """
        Check if this exchange is an outflow (sale) for the given warehouse.
        
        Args:
            warehouse_id: The warehouse to check against
            
        Returns:
            True if this is commodities going out, money coming in
        """
        return self.from_warehouse == warehouse_id
    
    def is_relevant_for(self, warehouse_id: str) -> bool:
        """
        Check if this exchange involves the given warehouse.
        
        Args:
            warehouse_id: The warehouse to check against
            
        Returns:
            True if this warehouse is either the source or destination
        """
        return self.is_inflow_for(warehouse_id) or self.is_outflow_for(warehouse_id)
    
    def is_mint(self) -> bool:
        """Check if this is a mint operation (new stock entering system)"""
        return self.from_warehouse == "0x0000"
    
    def is_burn(self) -> bool:
        """Check if this is a burn operation (stock leaving system)"""
        return self.to_warehouse == "0x0000"
    
    def is_bulk(self) -> bool:
        """Check if this is a bulk commodity (wheat, oil, steel, etc.)"""
        return self.commodity_standard == CommodityStandard.BULK
    
    def is_serialized(self) -> bool:
        """Not supported in Chapter 0"""
        return False
    
    def is_batched(self) -> bool:
        """Not supported in Chapter 0"""
        return False
    
    class Config:
        """Pydantic configuration"""
        # Allow using Decimal types
        arbitrary_types_allowed = True
        # Validate assignment after creation
        validate_assignment = True
        # Use enum values for serialization
        use_enum_values = True
        
        # Example for documentation
        schema_extra = {
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
                "batch_id": None,
                "item_ids": None
            }
        }
