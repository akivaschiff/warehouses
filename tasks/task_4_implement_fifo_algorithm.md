# Task 4: Implement FIFO Capital Gains Algorithm

## Objective
Replace simple inflow/outflow calculation with proper FIFO (First-In-First-Out) capital gains tracking for accurate cost basis calculation.

## Background: Why FIFO?
**Current Problem**: Simple subtraction (`outflow - inflow`) doesn't account for:
- **Cost basis tracking**: What did specific items cost when purchased?
- **Partial sales**: Selling only some of your inventory
- **Tax implications**: Which specific items were sold affects capital gains

**FIFO Solution**: Track the cost of specific inventory purchases and match them to sales in chronological order.

### Example:
```
Jan 1: Buy 100 tons wheat @ $200/ton = $20,000
Mar 1: Buy 100 tons wheat @ $300/ton = $30,000
May 1: Sell 150 tons wheat @ $250/ton = $37,500

FIFO Calculation:
- First 100 tons sold: cost $200/ton = $20,000 cost basis
- Next 50 tons sold: cost $300/ton = $15,000 cost basis
- Total cost basis: $35,000
- Capital gain: $37,500 - $35,000 = $2,500

Simple calculation would be: $37,500 - $50,000 = -$12,500 (WRONG!)
```

## Instructions

### 1. Create FIFO Data Structures
Create `src/logic/fifo_tracker.py`:

```python
from dataclasses import dataclass
from typing import List, Dict, Tuple
from decimal import Decimal
from datetime import datetime

@dataclass
class InventoryPurchase:
    """A single purchase of inventory"""
    timestamp: datetime
    quantity: Decimal
    price_per_unit: Decimal
    total_cost: Decimal
    remaining_quantity: Decimal  # How much is left unsold

@dataclass
class SaleAllocation:
    """How a sale was allocated against purchases"""
    sale_timestamp: datetime
    purchase_timestamp: datetime
    quantity_sold: Decimal
    cost_basis: Decimal
    sale_proceeds: Decimal
    capital_gain: Decimal

class FIFOTracker:
    """Tracks FIFO cost basis for a specific commodity"""
    
    def __init__(self, commodity_type: str):
        self.commodity_type = commodity_type
        self.purchases: List[InventoryPurchase] = []
        self.sales: List[SaleAllocation] = []
    
    def add_purchase(self, timestamp: datetime, quantity: Decimal, total_cost: Decimal):
        """Add a purchase to inventory"""
        purchase = InventoryPurchase(
            timestamp=timestamp,
            quantity=quantity,
            price_per_unit=total_cost / quantity,
            total_cost=total_cost,
            remaining_quantity=quantity
        )
        self.purchases.append(purchase)
        # Keep purchases sorted by timestamp
        self.purchases.sort(key=lambda p: p.timestamp)
    
    def process_sale(self, timestamp: datetime, quantity_sold: Decimal, sale_proceeds: Decimal) -> List[SaleAllocation]:
        """Process a sale using FIFO and return allocations"""
        allocations = []
        remaining_to_sell = quantity_sold
        
        for purchase in self.purchases:
            if remaining_to_sell <= 0:
                break
                
            if purchase.remaining_quantity <= 0:
                continue
            
            # How much can we sell from this purchase?
            quantity_from_this_purchase = min(remaining_to_sell, purchase.remaining_quantity)
            
            # Calculate cost basis and proceeds for this portion
            cost_basis = quantity_from_this_purchase * purchase.price_per_unit
            proceeds = (quantity_from_this_purchase / quantity_sold) * sale_proceeds
            capital_gain = proceeds - cost_basis
            
            # Create allocation
            allocation = SaleAllocation(
                sale_timestamp=timestamp,
                purchase_timestamp=purchase.timestamp,
                quantity_sold=quantity_from_this_purchase,
                cost_basis=cost_basis,
                sale_proceeds=proceeds,
                capital_gain=capital_gain
            )
            allocations.append(allocation)
            
            # Update remaining quantities
            purchase.remaining_quantity -= quantity_from_this_purchase
            remaining_to_sell -= quantity_from_this_purchase
        
        if remaining_to_sell > 0:
            # Selling more than we have in inventory - this is an error condition
            raise ValueError(f"Attempting to sell {remaining_to_sell} more than available inventory")
        
        self.sales.extend(allocations)
        return allocations
    
    def get_total_capital_gains(self) -> Decimal:
        """Get total capital gains for this commodity"""
        return sum(allocation.capital_gain for allocation in self.sales)
    
    def get_unrealized_value(self) -> Decimal:
        """Get cost basis of remaining inventory"""
        return sum(purchase.remaining_quantity * purchase.price_per_unit 
                  for purchase in self.purchases)
```

### 2. Update Gains Calculator
Modify `src/logic/gains_calculator.py`:

```python
from .fifo_tracker import FIFOTracker

def calculate_warehouse_gains(...) -> GainReport:
    # Create FIFO trackers for each commodity
    fifo_trackers: Dict[str, FIFOTracker] = {}
    
    # Collect all exchanges and sort by timestamp
    all_exchanges = list(exchanges)
    all_exchanges.sort(key=lambda e: e.timestamp)
    
    # Process chronologically for FIFO
    for exchange in all_exchanges:
        if not exchange.is_relevant_for(warehouse_id):
            continue
            
        commodity_key = f"{exchange.commodity_standard}_{exchange.item_type}"
        
        # Initialize tracker if needed
        if commodity_key not in fifo_trackers:
            fifo_trackers[commodity_key] = FIFOTracker(exchange.item_type)
        
        tracker = fifo_trackers[commodity_key]
        
        if exchange.is_inflow_for(warehouse_id):
            # Purchase: add to inventory
            tracker.add_purchase(
                timestamp=exchange.timestamp,
                quantity=exchange.quantity,
                total_cost=exchange.price_paid_usd
            )
            
        elif exchange.is_outflow_for(warehouse_id):
            # Sale: process using FIFO
            allocations = tracker.process_sale(
                timestamp=exchange.timestamp,
                quantity_sold=exchange.quantity,
                sale_proceeds=exchange.price_paid_usd
            )
    
    # Calculate final results
    total_capital_gains = Decimal('0')
    gains_by_commodity = []
    
    for commodity_key, tracker in fifo_trackers.items():
        capital_gains = tracker.get_total_capital_gains()
        total_capital_gains += capital_gains
        
        # Create commodity gains report
        commodity_gains = CommodityGains(
            commodity_type=tracker.commodity_type,
            total_inflow_cost=tracker.get_unrealized_value(),  # Cost of remaining inventory
            total_outflow_value=Decimal('0'),  # Not relevant for FIFO
            total_gain_loss=capital_gains,
            number_of_transactions=len(tracker.sales)
        )
        gains_by_commodity.append(commodity_gains)
    
    return GainReport(
        # ... other fields ...
        total_gain_loss=total_capital_gains,
        gains_by_commodity=gains_by_commodity
    )
```

### 3. Handle Each Commodity Separately
**Important**: Create separate FIFO trackers for:
- **Each commodity type**: Wheat, Steel, Oil, etc.
- **Each commodity standard**: Bulk vs. Serialized
- **Combination key**: `f"{commodity_standard}_{item_type}"`

This ensures wheat purchases don't affect steel cost basis.

### 4. Test FIFO Implementation
Create a test with known FIFO results:

```python
def test_fifo_calculation():
    exchanges = [
        # Buy 100 wheat @ $200/ton = $20,000
        create_exchange("2023-01-01", "inflow", "Wheat", 100, 20000),
        # Buy 100 wheat @ $300/ton = $30,000  
        create_exchange("2023-03-01", "inflow", "Wheat", 100, 30000),
        # Sell 150 wheat @ $250/ton = $37,500
        create_exchange("2023-05-01", "outflow", "Wheat", 150, 37500)
    ]
    
    report = calculate_warehouse_gains("WH_TEST", iter(exchanges))
    
    # Expected: Cost basis = (100*$200) + (50*$300) = $35,000
    # Expected: Capital gain = $37,500 - $35,000 = $2,500
    assert report.total_gain_loss == Decimal('2500')
```

### 5. Re-run Analysis
Test on `WH_c979f0a5` with FIFO:

```python
report = analyze_warehouse_gains("WH_c979f0a5")
print(f"FIFO Capital Gains: ${report.total_gain_loss:,.2f}")
```

## Expected Changes
- **More accurate gains**: Reflects actual cost of items sold
- **Different total**: May be significantly different from simple calculation
- **Proper cost basis**: Tracks remaining inventory value
- **Realistic results**: Matches real-world trading scenarios

## Success Criteria
✅ FIFO tracker correctly processes purchases and sales  
✅ Chronological order maintained across all commodities  
✅ Each commodity type tracked separately  
✅ Capital gains calculated using proper cost basis  
✅ Test cases validate FIFO math  
✅ Performance acceptable for large datasets  

## Next Steps
With accurate FIFO calculations, you're ready to implement entity-level aggregation in Task 5.
