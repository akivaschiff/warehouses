# Task 5: Entity-Level Portfolio Analysis

## Objective
Create entity-level portfolio summaries that aggregate gains across multiple warehouses while properly excluding internal transfers.

## Background
**Current State**: Analysis is per-warehouse  
**Business Need**: Companies own multiple warehouses and need consolidated portfolio view  
**Key Challenge**: Internal transfers between company warehouses have transaction value but shouldn't count as gains/losses

### Example Problem:
```
Company ABC owns:
- Warehouse A: Buys wheat for $10,000
- Warehouse B: (empty)

Internal Transfer:
- Warehouse A → Warehouse B: Transfer wheat for $12,000

This $12,000 "sale" looks like profit but it's just moving inventory within the same company.
```

## Instructions

### 1. Create Entity Data Model
Create `src/models/entity_report.py`:

```python
@dataclass
class EntityGainReport:
    """Portfolio-level gains for an entity (company) across all warehouses"""
    entity_id: str
    entity_name: str
    reporter_name: str
    analysis_date: datetime
    
    # Warehouse portfolio
    warehouse_ids: List[str]
    warehouse_count: int
    
    # Consolidated financials (excluding internal transfers)
    total_external_inflow_cost: Decimal    # Purchases from outside entities
    total_external_outflow_value: Decimal  # Sales to outside entities
    total_capital_gains: Decimal           # Net gains from external trades
    total_external_transactions: int       # External transactions only
    
    # Internal activity (for transparency)
    total_internal_transfers: int          # Transfers between own warehouses
    total_internal_value: Decimal          # Value of internal transfers
    
    # Breakdown by commodity and warehouse
    gains_by_commodity: List[CommodityGains]
    gains_by_warehouse: List[GainReport]   # Individual warehouse reports
    
    # Portfolio metrics
    best_performing_warehouse: Optional[str]
    worst_performing_warehouse: Optional[str]
    most_active_commodity: Optional[str]
    
    # Date range
    analysis_start_date: Optional[datetime] = None
    analysis_end_date: Optional[datetime] = None
```

### 2. Create Entity Analysis Flow
Create `src/flows/entity_gains_flow.py`:

```python
def analyze_entity_gains(
    entity_id: str,
    save_to_db: bool = True,
    client: Optional[SupabaseClient] = None
) -> EntityGainReport:
    """
    Calculate consolidated gains for an entity across all warehouses.
    
    Key Logic:
    1. Find all warehouses owned by the entity
    2. Get all exchanges involving those warehouses
    3. Classify exchanges as external vs. internal
    4. Run FIFO calculation on external exchanges only
    5. Aggregate results across all warehouses
    """
    
    if client is None:
        client = SupabaseClient()
    
    # Step 1: Find entity and warehouses
    entity_info = client.find('companies', {'company_id': entity_id})
    if len(entity_info) == 0:
        raise ValueError(f"Entity {entity_id} not found")
    
    entity_name = entity_info.iloc[0]['name']
    warehouses = client.find('warehouses', {'company_id': entity_id})
    warehouse_ids = warehouses['warehouse_id'].tolist()
    
    # Step 2: Get ALL exchanges involving these warehouses
    all_exchanges = fetch_entity_exchanges(warehouse_ids, client)
    
    # Step 3: Classify exchanges
    external_exchanges, internal_exchanges = classify_exchanges(
        all_exchanges, warehouse_ids
    )
    
    # Step 4: Calculate gains on external exchanges only
    entity_gains = calculate_entity_gains_fifo(
        entity_id, warehouse_ids, external_exchanges
    )
    
    # Step 5: Generate individual warehouse reports for breakdown
    warehouse_reports = []
    for warehouse_id in warehouse_ids:
        warehouse_report = analyze_warehouse_gains(
            warehouse_id, save_to_db=False, client=client
        )
        warehouse_reports.append(warehouse_report)
    
    # Step 6: Build entity report
    return build_entity_report(
        entity_id, entity_name, warehouse_ids, 
        entity_gains, warehouse_reports, 
        external_exchanges, internal_exchanges
    )


def classify_exchanges(
    exchanges_df: pd.DataFrame, 
    entity_warehouse_ids: List[str]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separate external vs. internal exchanges.
    
    Internal = Both from_warehouse AND to_warehouse belong to same entity
    External = At least one warehouse is external to the entity
    """
    
    # Create boolean masks
    from_is_internal = exchanges_df['from_warehouse'].isin(entity_warehouse_ids)
    to_is_internal = exchanges_df['to_warehouse'].isin(entity_warehouse_ids)
    
    # Internal: both warehouses belong to this entity
    internal_mask = from_is_internal & to_is_internal
    
    # External: at least one warehouse is external
    external_mask = ~internal_mask
    
    internal_exchanges = exchanges_df[internal_mask].copy()
    external_exchanges = exchanges_df[external_mask].copy()
    
    return external_exchanges, internal_exchanges


def fetch_entity_exchanges(warehouse_ids: List[str], client: SupabaseClient) -> pd.DataFrame:
    """Get all exchanges where entity warehouses are involved"""
    
    # Build query for exchanges involving any of these warehouses
    warehouse_ids_str = "', '".join(warehouse_ids)
    
    query = f"""
    SELECT * FROM exchanges 
    WHERE from_warehouse IN ('{warehouse_ids_str}') 
       OR to_warehouse IN ('{warehouse_ids_str}')
    ORDER BY timestamp
    """
    
    return client.execute_sql(query)
```

### 3. Implement Entity FIFO Calculation
Add to `src/logic/gains_calculator.py`:

```python
def calculate_entity_gains_fifo(
    entity_id: str,
    warehouse_ids: List[str], 
    external_exchanges_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Calculate FIFO gains for an entity using only external exchanges.
    
    For each warehouse in the entity:
    - Inflows: External purchases (from_warehouse NOT in entity)
    - Outflows: External sales (to_warehouse NOT in entity)
    - Ignore: Internal transfers between entity warehouses
    """
    
    # Create per-warehouse FIFO trackers
    warehouse_trackers = {}
    for warehouse_id in warehouse_ids:
        warehouse_trackers[warehouse_id] = {}  # commodity -> FIFOTracker
    
    # Convert to Exchange objects and sort chronologically
    exchanges = dataframe_to_exchange_iterator(external_exchanges_df)
    exchange_list = list(exchanges)
    exchange_list.sort(key=lambda e: e.timestamp)
    
    # Process each external exchange
    for exchange in exchange_list:
        # Determine which warehouse this affects
        target_warehouse = None
        
        if exchange.from_warehouse in warehouse_ids:
            # This warehouse is selling (outflow)
            target_warehouse = exchange.from_warehouse
            is_inflow = False
            
        elif exchange.to_warehouse in warehouse_ids:
            # This warehouse is buying (inflow)
            target_warehouse = exchange.to_warehouse
            is_inflow = True
        
        if target_warehouse is None:
            continue  # Shouldn't happen with proper filtering
        
        # Get/create commodity tracker for this warehouse
        commodity_key = f"{exchange.commodity_standard}_{exchange.item_type}"
        
        if commodity_key not in warehouse_trackers[target_warehouse]:
            warehouse_trackers[target_warehouse][commodity_key] = FIFOTracker(
                exchange.item_type
            )
        
        tracker = warehouse_trackers[target_warehouse][commodity_key]
        
        # Process the exchange
        if is_inflow:
            tracker.add_purchase(
                timestamp=exchange.timestamp,
                quantity=exchange.quantity,
                total_cost=exchange.price_paid_usd
            )
        else:
            tracker.process_sale(
                timestamp=exchange.timestamp,
                quantity_sold=exchange.quantity,
                sale_proceeds=exchange.price_paid_usd
            )
    
    # Aggregate results across all warehouses
    total_capital_gains = Decimal('0')
    gains_by_commodity = {}
    
    for warehouse_id, commodity_trackers in warehouse_trackers.items():
        for commodity_key, tracker in commodity_trackers.items():
            capital_gains = tracker.get_total_capital_gains()
            total_capital_gains += capital_gains
            
            # Aggregate by commodity across warehouses
            if commodity_key not in gains_by_commodity:
                gains_by_commodity[commodity_key] = {
                    'total_gains': Decimal('0'),
                    'total_transactions': 0,
                    'commodity_type': tracker.commodity_type
                }
            
            gains_by_commodity[commodity_key]['total_gains'] += capital_gains
            gains_by_commodity[commodity_key]['total_transactions'] += len(tracker.sales)
    
    return {
        'total_capital_gains': total_capital_gains,
        'gains_by_commodity': gains_by_commodity,
        'warehouse_trackers': warehouse_trackers
    }
```

### 4. Test Entity Analysis
Test with a multi-warehouse entity:

```python
# Find an entity with multiple warehouses
client = SupabaseClient()
entities_with_multiple_warehouses = client.execute_sql("""
    SELECT company_id, name, COUNT(*) as warehouse_count
    FROM companies c
    JOIN warehouses w ON c.company_id = w.company_id
    GROUP BY company_id, name
    HAVING COUNT(*) >= 3
    ORDER BY warehouse_count DESC
    LIMIT 5
""")

# Test entity analysis
entity_id = entities_with_multiple_warehouses.iloc[0]['company_id']
entity_report = analyze_entity_gains(entity_id)

print(f"Entity: {entity_report.entity_name}")
print(f"Warehouses: {entity_report.warehouse_count}")
print(f"External Capital Gains: ${entity_report.total_capital_gains:,.2f}")
print(f"Internal Transfers: {entity_report.total_internal_transfers}")
print(f"Internal Value: ${entity_report.total_internal_value:,.2f}")
```

### 5. Expected Output Format
```
🏢 Entity Analysis: ABC Trading Company
📦 Portfolio: 5 warehouses
📊 External Activity:
   Capital Gains:      $245,000.00
   External Trades:    156 transactions
   
🔄 Internal Activity:
   Internal Transfers: 23 transactions  
   Transfer Value:     $89,000.00
   (Excluded from gains calculation)

🏭 Warehouse Performance:
   Best:  WH_12345 (+$125,000)
   Worst: WH_67890 (-$15,000)
   
🏗️ Top Commodities:
   • Wheat: +$95,000 (45 external trades)
   • Steel: +$78,000 (32 external trades)
   • Oil: +$72,000 (28 external trades)
```

## Key Business Rules
1. **Internal Transfers**: Excluded from gains calculation
2. **External Trades Only**: Only count trades with outside entities
3. **Separate FIFO**: Each warehouse maintains its own cost basis
4. **Consolidated View**: Roll up all external gains to entity level
5. **Transparency**: Show internal activity for audit purposes

## Success Criteria
✅ Entity analysis excludes internal transfers  
✅ External trades properly classified  
✅ FIFO calculation works at entity level  
✅ Individual warehouse breakdown available  
✅ Internal transfer activity tracked for transparency  
✅ Performance metrics identify best/worst performers  

## Final Deliverable
A complete entity-level portfolio analysis system that provides accurate capital gains calculations for multi-warehouse trading entities, properly handling the complex business logic of internal vs. external transactions.
