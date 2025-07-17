# Task 2: Precise Daily Pricing

## Background
Currently, each exchange record contains its own `price_paid_usd` value. However, this value is innacurate. The database now contains a `commodity_prices` table with precise daily rates for each commodity per unit.


## Objective
Load the exchange rows and the price rows 
Replace exchange pricing with accurate daily prices from the `commodity_prices` table.


## Table Structure
```csv
date,commodity_type,price_per_unit,unit
2024-01-01,Wheat,285.43,tons
2024-01-01,Steel,540.12,tons
...
```

## Instructions

1. **Update `fetch_warehouse_exchanges()`** in `src/flows/warehouse_gains_flow.py`
2. **Join exchanges with commodity_prices** on:
   - `DATE(exchange.timestamp)` = `commodity_prices.date`  
   - `exchange.item_type` = `commodity_prices.commodity_type`
3. **Calculate new price**: `quantity * price_per_unit`
4. **Use original price as fallback** if no match found

## Test Results
Run the same warehouse and compare:

```bash
make run-flow
```

Document the difference in total gain before/after the pricing update.

## Success Criteria
✅ Exchanges use daily market prices  
✅ Fallback to original price when needed  
✅ New total calculated and different from Task 1  

The updated pricing should give more realistic profit calculations.