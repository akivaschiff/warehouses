# Task 2: Precise Daily Pricing

Currently, each exchange record contains its own `price_paid_usd` value. However, this value is an approximate and not correct. The database now contains a `commodity_prices` table with precise daily rates for each commodity per unit.


## Objective
In the `src/flows/warehouse_gains_flow.py` Load also the price rows.
Replace exchange pricing with accurate daily prices from the `commodity_prices` table.
When you're ready, just re-run our flow on warehouse `"WH_30f6fae4"` using:

```bash
make run-flow
```

To continue - you must answer the question - what is the `Total Gain/Loss` now?