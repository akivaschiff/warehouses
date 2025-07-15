# Task 2: Implement Precise Daily Pricing

## Objective
Replace the current monthly-average pricing with precise daily prices from dedicated price tables.

## Background
Currently, commodity prices use seasonal/monthly averages. The database contains daily price tables (`prices_wheat`, `prices_steel`, etc.) with exact historical prices. We need to join exchange data with these precise prices for accurate calculations.

## Database Schema
Price tables follow this structure:
```sql
-- Example: prices_wheat table
CREATE TABLE prices_wheat (
    date DATE,
    price_per_unit DECIMAL(10,2),  -- USD per ton/barrel/etc
    commodity_type VARCHAR(50),
    region VARCHAR(100)
);
```

## Instructions

### 1. Explore Price Tables
First, examine the available price data:

```python
from src.database.supabase_client import SupabaseClient

client = SupabaseClient()

# Check available price tables
tables = client.list_tables()
price_tables = [t for t in tables if t.startswith('prices_')]
print("Price tables:", price_tables)

# Sample wheat prices
wheat_prices = client.find('prices_wheat', limit=10)
print(wheat_prices)
```

### 2. Modify Exchange Data Loading
Update `src/flows/warehouse_gains_flow.py`:

**In `fetch_warehouse_exchanges()` function:**
- Join exchanges with appropriate price tables
- Match on: `exchange.timestamp` → `prices.date` and `exchange.item_type` → `prices.commodity_type`
- Replace `exchange.price_paid_usd` with `(exchange.quantity * prices.price_per_unit)`

### 3. Handle Missing Prices
For exchanges without matching price data:
- Use the original `price_paid_usd` as fallback
- Log a warning about missing price data
- Track how many exchanges used fallback pricing

### 4. Update SQL Query Example
```sql
-- Join exchanges with wheat prices
SELECT 
    e.*,
    p.price_per_unit,
    (e.quantity * p.price_per_unit) as calculated_price,
    CASE 
        WHEN p.price_per_unit IS NULL THEN e.price_paid_usd
        ELSE (e.quantity * p.price_per_unit)
    END as updated_price
FROM exchanges e
LEFT JOIN prices_wheat p ON DATE(e.timestamp) = p.date 
    AND e.item_type = p.commodity_type
WHERE e.commodity_standard = 'bulk'
```

### 5. Re-run Analysis
Test on the same warehouse `WH_c979f0a5`:
```python
report = analyze_warehouse_gains("WH_c979f0a5")
print(f"Updated Total Gain: ${report.total_gain_loss:,.2f}")
```

## Expected Changes
- **More accurate pricing** reflecting daily market fluctuations
- **Different total gain** due to precise vs. averaged prices
- **Better seasonal patterns** in commodity breakdown

## Deliverables
1. **Modified flow code** with price table integration
2. **Comparison report**:
   - Original gain: $1,673,000
   - Updated gain: $_______ (document new amount)
   - Percentage change: _____%
3. **Price coverage analysis**: How many exchanges used precise vs. fallback pricing

## Success Criteria
✅ All price tables successfully queried  
✅ Exchange prices updated with daily rates  
✅ Fallback handling works for missing prices  
✅ New total gain calculated and documented  
✅ Performance remains acceptable (<30 seconds)  

## Next Steps
With accurate pricing in place, you're ready to expand the data model for serialized items in Task 3.
