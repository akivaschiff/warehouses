# Task 1: The warehouse gain report

Every warehouse should be able to produce a report summarizing the total value that went through it. An "inflow" is the cost we pay to bring commodities into the warehouse and the "outflow" is the money we make from selling it out. The "gain" is the difference between these two numbers and is hopefully a positive one (but don't worry if it isn't - warehouses have more magic up their sleeves).

## Objective
Run the existing gains calculation on a specific warehouse and verify the expected result.

## Background
Your warehouse gains calculator should now be working end-to-end. We need to test it against known data to ensure accuracy.

## Instructions

### 1. Run Analysis on Target Warehouse
Execute the gains analysis for warehouse `WH_c979f0a5`:

```bash
# Test the specific warehouse
make test-full
```

Or run directly in Python:
```python
from src.flows.warehouse_gains_flow import analyze_warehouse_gains

report = analyze_warehouse_gains("WH_c979f0a5")
print(f"Total Gain: ${report.total_gain_loss:,.2f}")
```

### 2. Verification Target
**Expected Result**: Total gain should be approximately **$1,673,000 USD**

### 3. Debug if Different
If your result doesn't match:
- Check that you've updated the database from "interchangeable" to "bulk"
- Verify the warehouse exists and has exchange data
- Examine the commodity breakdown to understand the calculation
- Use `make test-demo` to verify your calculation logic is correct

### 4. Document Results
Record in your analysis:
- Actual total gain/loss amount
- Number of transactions processed
- Top 3 commodities by gain/loss
- Date range of the analysis

## Success Criteria
✅ Program runs without errors  
✅ Total gain matches expected $1,673,000 (±$1,000)  
✅ Results include detailed commodity breakdown  
✅ All validation checks pass  

## Next Steps
Once verified, you're ready to enhance the price calculation accuracy in Task 2.
