#!/usr/bin/env python3
"""
Upload warehouse CSV data to Supabase PostgreSQL database

Usage:
    python scripts/upload_to_supabase.py

Prerequisites:
    1. Create .env file in project root with:
       DATABASE_URL=postgresql://postgres.[PROJECT]:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
    2. Generate CSV data first: make data
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_csv_files():
    """Load the generated CSV files"""
    data_files = {
        "companies": "data/outputs/warehouse_data_companies.csv",
        "warehouses": "data/outputs/warehouse_data_warehouses.csv",
        "exchanges": "data/outputs/warehouse_data_exchanges.csv",
    }

    dataframes = {}

    for table_name, file_path in data_files.items():
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            logger.info(
                "Please run 'make data' or 'python scripts/generate_data.py' first"
            )
            sys.exit(1)

        logger.info(f"Loading {file_path}...")
        df = pd.read_csv(file_path)

        # Clean up data types for better PostgreSQL compatibility
        if table_name == "exchanges":
            # Convert timestamp to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            # Ensure numeric columns are proper types
            df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
            df["price_paid_usd"] = pd.to_numeric(df["price_paid_usd"], errors="coerce")

        dataframes[table_name] = df
        logger.info(f"Loaded {len(df)} rows for {table_name}")

    return dataframes


def create_database_connection():
    """Create connection to Supabase PostgreSQL"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        logger.error("DATABASE_URL environment variable not set!")
        logger.info("Please create a .env file in your project root with:")
        logger.info(
            "DATABASE_URL='postgresql://postgres.[PROJECT]:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres'"
        )
        logger.info("Replace [PROJECT] and [PASSWORD] with your actual Supabase values")
        sys.exit(1)

    try:
        engine = create_engine(database_url)
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"Connected to PostgreSQL: {version[:50]}...")
        return engine

    except SQLAlchemyError as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.info(
            "Please check your DATABASE_URL and ensure Supabase project is running"
        )
        sys.exit(1)


def upload_data_to_supabase(engine, dataframes):
    """Upload dataframes to Supabase tables"""

    # Upload order matters due to foreign key relationships
    upload_order = ["companies", "warehouses", "exchanges"]

    for table_name in upload_order:
        df = dataframes[table_name]
        logger.info(f"Uploading {len(df)} rows to {table_name} table...")

        try:
            # Upload data (replace existing table)
            df.to_sql(
                table_name,
                engine,
                if_exists="replace",  # Replace existing table
                index=False,  # Don't include pandas index
                method="multi",  # Faster bulk insert
                chunksize=1000,  # Process in chunks for large datasets
            )
            logger.info(f"✅ Successfully uploaded {table_name}")

        except SQLAlchemyError as e:
            logger.error(f"❌ Failed to upload {table_name}: {e}")
            raise


def verify_upload(engine, dataframes):
    """Verify that data was uploaded correctly"""
    logger.info("\n=== Verifying Upload ===")

    for table_name, df in dataframes.items():
        try:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                db_count = result.fetchone()[0]
                csv_count = len(df)

                if db_count == csv_count:
                    logger.info(f"✅ {table_name}: {db_count} rows (matches CSV)")
                else:
                    logger.warning(
                        f"⚠️ {table_name}: {db_count} in DB vs {csv_count} in CSV"
                    )

        except SQLAlchemyError as e:
            logger.error(f"❌ Failed to verify {table_name}: {e}")


def print_sample_queries(engine):
    """Print some sample queries to test the data"""
    logger.info("\n=== Sample Queries ===")

    queries = [
        ("Total number of exchanges", "SELECT COUNT(*) FROM exchanges"),
        ("Date range", "SELECT MIN(timestamp), MAX(timestamp) FROM exchanges"),
        ("Total trade value", "SELECT SUM(price_paid_usd) FROM exchanges"),
        (
            "Top commodity by volume",
            """
            SELECT item_type, COUNT(*) as exchange_count 
            FROM exchanges 
            GROUP BY item_type 
            ORDER BY exchange_count DESC 
            LIMIT 5
        """,
        ),
    ]

    try:
        with engine.connect() as conn:
            for description, query in queries:
                result = conn.execute(text(query))
                row = result.fetchone()
                logger.info(f"{description}: {row}")

    except SQLAlchemyError as e:
        logger.error(f"Failed to run sample queries: {e}")


def main():
    """Main upload process"""
    logger.info("🚀 Starting Supabase upload process...")

    # Load CSV files
    dataframes = load_csv_files()

    # Create database connection
    engine = create_database_connection()

    # Upload data
    upload_data_to_supabase(engine, dataframes)

    # Verify upload
    verify_upload(engine, dataframes)

    # Run sample queries
    print_sample_queries(engine)

    logger.info("\n🎉 Upload completed successfully!")
    logger.info(
        "You can now query your data in Supabase or connect to it from other applications"
    )

    # Print connection info for participants
    logger.info(
        f"\n📊 Database URL: {os.getenv('DATABASE_URL').split('@')[1].split('/')[0]}"
    )
    logger.info("Tables created: companies, warehouses, exchanges")


if __name__ == "__main__":
    main()
