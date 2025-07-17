# Task 4: The Ancient Art of True Merchant Accounting
Masterful work! You've calculated both bulk commodities and serialized ones!, but I must reveal a dark secret... Our current gain calculation method has a terrible flaw!

Right now, you're using easy math - simple subtraction of total inflows from total outflows. But this ignores the sacred law of First-In-First-Out (FIFO)! When you sell 150 tons of wheat, which specific wheat did you sell? The expensive batch you bought last month, or the cheap batch from January? The answer determines your true profit!

Consider this warehouse's tale:

January: Buy 100 tons wheat @ $200/ton = $20,000
March: Buy 100 tons wheat @ $300/ton = $30,000
May: Sell 150 tons wheat @ $250/ton = $37,500

Our old calculation: $37,500 - $50,000 = -$12,500 LOSS 😱
FIFO Accounting: Sell the January wheat first (100 tons @ $200) + 50 tons from March (@ $300) = $35,000 cost basis → $2,500 PROFIT 🎯

## Objective
Replace your simple inflow/outflow subtraction with proper FIFO capital gains tracking. Each commodity type or serialized item needs its own FIFO queue, tracking purchases chronologically and matching them to sales in order.

note: Incase the FIFO queue tries to "sell" without a matching "buy" - ignore that part of the sell (it belongs to a buy from before the cutoff so we don't know the true buy price)

When you've mastered the sacred FIFO arts on warehouse "WH_30f6fae4", the True Capital Gains will be revealed - a number that reflects reality!
