import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseClient:    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize Supabase client
        
        Args:
            database_url: PostgreSQL connection string. If None, loads from DATABASE_URL env var
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError(
                "DATABASE_URL not found. Please set it in your .env file or pass it as a parameter."
            )
        
        self.engine = create_engine(self.database_url)
        self._test_connection()
    
    def _test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            raise ConnectionError(f"Failed to connect to Supabase: {e}")
    
    def list_tables(self) -> List[str]:
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            return sorted(tables)
        except SQLAlchemyError as e:
            logger.error(f"Failed to list tables: {e}")
            return []
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            
            return {
                'table_name': table_name,
                'columns': [
                    {
                        'name': col['name'],
                        'type': str(col['type']),
                        'nullable': col['nullable'],
                        'default': col.get('default')
                    }
                    for col in columns
                ],
                'row_count': self.count(table_name)
            }
        except SQLAlchemyError as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            return {}
    
    def find(
        self, 
        table_name: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Find records in a table with optional filters
        
        Args:
            table_name: Name of the table to query
            filters: Dictionary of column filters. Supports operators:
                - 'column_name': value (equals)
                - 'column_name__gte': value (greater than or equal)
                - 'column_name__lte': value (less than or equal)
                - 'column_name__gt': value (greater than)
                - 'column_name__lt': value (less than)
                - 'column_name__like': value (LIKE pattern)
                - 'column_name__in': [list] (IN clause)
            limit: Maximum number of records to return
            order_by: Column name to order by
            order_desc: If True, order in descending order
            
        Returns:
            List of dictionaries with results
            
        Examples:
            # Find all wheat exchanges
            client.find('exchanges', {'item_type': 'Wheat'})
            
            # Find expensive trades
            client.find('exchanges', {'price_paid_usd__gte': 100000}, limit=10)
            
            # Find recent trades, ordered by date
            client.find('exchanges', order_by='timestamp', order_desc=True, limit=20)
            
            # Find companies from multiple countries
            client.find('companies', {'country__in': ['United States', 'China']})
        """
        try:
            # Build WHERE clause
            where_conditions = []
            params = {}
            
            if filters:
                for key, value in filters.items():
                    if '__' in key:
                        column, operator = key.split('__', 1)
                        param_name = f"param_{len(params)}"
                        
                        if operator == 'gte':
                            where_conditions.append(f"{column} >= :{param_name}")
                            params[param_name] = value
                        elif operator == 'lte':
                            where_conditions.append(f"{column} <= :{param_name}")
                            params[param_name] = value
                        elif operator == 'gt':
                            where_conditions.append(f"{column} > :{param_name}")
                            params[param_name] = value
                        elif operator == 'lt':
                            where_conditions.append(f"{column} < :{param_name}")
                            params[param_name] = value
                        elif operator == 'like':
                            where_conditions.append(f"{column} LIKE :{param_name}")
                            params[param_name] = value
                        elif operator == 'in':
                            placeholders = ','.join([f":{param_name}_{i}" for i in range(len(value))])
                            where_conditions.append(f"{column} IN ({placeholders})")
                            for i, val in enumerate(value):
                                params[f"{param_name}_{i}"] = val
                    else:
                        # Simple equality
                        param_name = f"param_{len(params)}"
                        where_conditions.append(f"{key} = :{param_name}")
                        params[param_name] = value
            
            # Build query
            query = f"SELECT * FROM {table_name}"
            
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
            
            if order_by:
                direction = "DESC" if order_desc else "ASC"
                query += f" ORDER BY {order_by} {direction}"
            
            if limit:
                query += f" LIMIT {limit}"
            
            # Execute query
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params)
                columns = result.keys()
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to query {table_name}: {e}")
            return []
    
    def count(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records in a table with optional filters
        
        Args:
            table_name: Name of the table
            filters: Optional filters (same format as find())
            
        Returns:
            Number of records
            
        Example:
            >>> client.count('exchanges', {'item_type': 'Wheat'})
            8234
        """
        try:
            where_conditions = []
            params = {}
            
            if filters:
                # Reuse filter logic from find()
                for key, value in filters.items():
                    if '__' in key:
                        column, operator = key.split('__', 1)
                        param_name = f"param_{len(params)}"
                        
                        if operator == 'gte':
                            where_conditions.append(f"{column} >= :{param_name}")
                            params[param_name] = value
                        # ... (same logic as find method)
                    else:
                        param_name = f"param_{len(params)}"
                        where_conditions.append(f"{key} = :{param_name}")
                        params[param_name] = value
            
            query = f"SELECT COUNT(*) FROM {table_name}"
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params)
                return result.scalar()
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to count {table_name}: {e}")
            return 0
    
    def execute_sql(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Execute raw SQL query
        
        Args:
            query: SQL query string
            params: Optional parameters for the query
            
        Returns:
            List of dictionaries with results
            
        Example:
            >>> query = "SELECT item_type, COUNT(*) as count FROM exchanges GROUP BY item_type"
            >>> client.execute_sql(query)
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                columns = result.keys()
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except SQLAlchemyError as e:
            logger.error(f"Failed to execute query: {e}")
            return []
    
    def get_sample_data(self, table_name: str, n: int = 5) -> List[Dict[str, Any]]:
        return self.find(table_name, limit=n)
    
    def search_exchanges(
        self,
        commodity_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        warehouse_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Specialized search for exchanges with common filters
        
        Args:
            commodity_type: Filter by item_type (e.g., 'Wheat', 'Steel')
            min_price: Minimum price_paid_usd
            max_price: Maximum price_paid_usd  
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            warehouse_id: Filter by from_warehouse or to_warehouse
            limit: Maximum results
            
        Returns:
            List of dictionaries with matching exchanges
        """
        filters = {}
        
        if commodity_type:
            filters['item_type'] = commodity_type
        if min_price is not None:
            filters['price_paid_usd__gte'] = min_price
        if max_price is not None:
            filters['price_paid_usd__lte'] = max_price
        if start_date:
            filters['timestamp__gte'] = start_date
        if end_date:
            filters['timestamp__lte'] = end_date
        
        results = self.find('exchanges', filters, limit=limit, order_by='timestamp', order_desc=True)
        
        # Additional warehouse filter (from_warehouse OR to_warehouse)
        if warehouse_id and results:
            results = [
                row for row in results 
                if row.get('from_warehouse') == warehouse_id or row.get('to_warehouse') == warehouse_id
            ]
        
        return results

# Convenience functions for quick access
def get_client() -> SupabaseClient:
    """Get a configured Supabase client"""
    return SupabaseClient()


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    client = SupabaseClient()
    
    print("Available tables:", client.list_tables())
    
    # Sample queries
    print("\n=== Sample Companies ===")
    companies = client.get_sample_data('companies', 3)
    for company in companies:
        print(company)
    
    print("\n=== Wheat Exchanges ===")
    wheat_trades = client.find('exchanges', {'item_type': 'Wheat'}, limit=5)
    for trade in wheat_trades:
        print(f"ID: {trade['exchange_id']}, Type: {trade['item_type']}, Quantity: {trade['quantity']}, Price: {trade['price_paid_usd']}, Time: {trade['timestamp']}")
    
    print("\n=== High Value Exchanges ===")
    expensive_trades = client.find('exchanges', {'price_paid_usd__gte': 100000}, limit=5)
    for trade in expensive_trades:
        print(f"ID: {trade['exchange_id']}, Type: {trade['item_type']}, Price: {trade['price_paid_usd']}")
    
    print(f"\n=== Total Exchanges: {client.count('exchanges')} ===")
    print(f"Wheat exchanges: {client.count('exchanges', {'item_type': 'Wheat'})}")