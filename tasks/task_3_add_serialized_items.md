# Task 3: Add Serialized Items Support

## Objective
Expand the system to handle both bulk commodities and serialized items with updated reporting structure.

## Background
Currently, the system only processes `commodity_standard = 'bulk'`. We need to add support for `commodity_standard = 'serialized'` items (like art, cars, equipment) and restructure the GainReport to show separate summaries.

## Instructions

### 1. Update Exchange Model
Modify `src/models/exchange.py`:

**Add new enum value:**
```python
class CommodityStandard(str, Enum):
    BULK = "bulk"           # Existing: wheat, oil, steel
    SERIALIZED = "serialized"  # New: art, cars, equipment
```

**Add token_id field:**
```python
class Exchange(BaseModel):
    # ... existing fields ...
    token_id: Optional[str] = Field(None, description="Unique token ID for serialized items")
```

**Update helper methods:**
```python
def is_serialized(self) -> bool:
    """Check if this is a serialized item (art, cars, etc.)"""
    return self.commodity_standard == CommodityStandard.SERIALIZED
```

### 2. Update GainReport Structure
Modify `src/models/gain_report.py`:

**Add commodity standard breakdowns:**
```python
@dataclass
class GainReport:
    warehouse_id: str
    reporter_name: str
    analysis_date: datetime
    
    # Overall totals
    total_inflow_cost: Decimal
    total_outflow_value: Decimal
    total_gain_loss: Decimal
    total_transactions: int
    
    # NEW: Breakdown by commodity standard
    bulk_inflow_cost: Decimal
    bulk_outflow_value: Decimal
    bulk_gain_loss: Decimal
    bulk_transactions: int
    
    serialized_inflow_cost: Decimal
    serialized_outflow_value: Decimal
    serialized_gain_loss: Decimal
    serialized_transactions: int
    
    # Detailed breakdowns
    gains_by_commodity: List[CommodityGains]  # All commodities
    gains_by_bulk_commodity: List[CommodityGains]  # Bulk only
    gains_by_serialized_commodity: List[CommodityGains]  # Serialized only
    
    # Date range
    analysis_start_date: Optional[datetime] = None
    analysis_end_date: Optional[datetime] = None
```

### 3. Update Gains Calculator Logic
Modify `src/logic/gains_calculator.py`:

**Process both commodity standards:**
```python
def calculate_warehouse_gains(...) -> GainReport:
    # Initialize tracking for both standards
    bulk_inflow_cost = Decimal('0')
    bulk_outflow_value = Decimal('0')
    bulk_transactions = 0
    
    serialized_inflow_cost = Decimal('0')
    serialized_outflow_value = Decimal('0')
    serialized_transactions = 0
    
    # Process ALL exchanges (not just bulk)
    for exchange in exchanges:
        if not exchange.is_relevant_for(warehouse_id):
            continue
            
        # Track by commodity standard
        if exchange.is_bulk():
            if exchange.is_inflow_for(warehouse_id):
                bulk_inflow_cost += exchange.price_paid_usd
                bulk_transactions += 1
            elif exchange.is_outflow_for(warehouse_id):
                bulk_outflow_value += exchange.price_paid_usd
                bulk_transactions += 1
                
        elif exchange.is_serialized():
            if exchange.is_inflow_for(warehouse_id):
                serialized_inflow_cost += exchange.price_paid_usd
                serialized_transactions += 1
            elif exchange.is_outflow_for(warehouse_id):
                serialized_outflow_value += exchange.price_paid_usd
                serialized_transactions += 1
    
    # Calculate gains by standard
    bulk_gain_loss = bulk_outflow_value - bulk_inflow_cost
    serialized_gain_loss = serialized_outflow_value - serialized_inflow_cost
    
    # ... build separate commodity lists ...
```

### 4. Update Database Query
Modify `src/flows/warehouse_gains_flow.py`:

**Remove bulk-only filter:**
```python
def fetch_warehouse_exchanges(warehouse_id: str, client: SupabaseClient):
    # Fetch BOTH bulk AND serialized exchanges
    inflows = client.find('exchanges', {
        'to_warehouse': warehouse_id
        # Remove: 'commodity_standard': 'bulk'
    })
    
    outflows = client.find('exchanges', {
        'from_warehouse': warehouse_id
        # Remove: 'commodity_standard': 'bulk'
    })
```

### 5. Test with Mixed Data
Create test data with both standards:

```python
# Test with warehouse that has both bulk and serialized items
report = analyze_warehouse_gains("WH_mixed_inventory")

print(f"Total Gain: ${report.total_gain_loss:,.2f}")
print(f"Bulk Gain: ${report.bulk_gain_loss:,.2f}")
print(f"Serialized Gain: ${report.serialized_gain_loss:,.2f}")
print(f"Bulk Commodities: {len(report.gains_by_bulk_commodity)}")
print(f"Serialized Items: {len(report.gains_by_serialized_commodity)}")
```

## Expected Output Format
```
📊 Analysis Results for WH_12345
💰 Total Summary:
   Total Gain/Loss:        $125,000.00
   Total Transactions:     45

🏗️ Bulk Commodities:
   Bulk Gain/Loss:         $75,000.00
   Bulk Transactions:      40
   Top Commodities:
   • Wheat: $45,000.00 (25 trades)
   • Steel: $30,000.00 (15 trades)

🎨 Serialized Items:
   Serialized Gain/Loss:   $50,000.00
   Serialized Transactions: 5
   Top Items:
   • Art Pieces: $35,000.00 (3 trades)
   • Luxury Cars: $15,000.00 (2 trades)
```

## Success Criteria
✅ Exchange model accepts serialized commodity standard  
✅ GainReport shows separate bulk vs. serialized summaries  
✅ Calculator processes both commodity types  
✅ Database queries include all commodity standards  
✅ Results display clear breakdown between types  

## Next Steps
With support for both commodity types, you're ready to implement proper FIFO capital gains calculation in Task 4.
