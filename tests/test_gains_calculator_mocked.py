"""
Test Warehouse Gains Calculator with Mocked Data

Tests the complete gains calculation logic using fixtures and mocks.
No database dependencies - pure unit testing of business logic.
"""

import pytest
import pandas as pd
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch
from typing import Dict, Any

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.flows.warehouse_gains_flow import analyze_warehouse_gains
from src.logic.gains_calculator import calculate_warehouse_gains
from src.models.exchange import Exchange, CommodityStandard
from src.models.gain_report import GainReport


class TestWarehouseGainsWithMocks:
    """Test warehouse gains calculation with mocked database"""

    @pytest.fixture
    def mock_warehouse_data(self):
        """Mock warehouse data"""
        return pd.DataFrame(
            [
                {
                    "warehouse_id": "WH_TEST_123",
                    "company_id": "COMP_TEST_456",
                    "address": "123 Test Street, Test City",
                    "country": "United States",
                    "warehouse_type": "distribution",
                }
            ]
        )

    @pytest.fixture
    def mock_exchange_data(self):
        """
        Mock exchange data with exactly 2 exchanges:
        1. Inflow: WH_TEST_123 buys 100 tons of Wheat for $20,000
        2. Outflow: WH_TEST_123 sells 50 tons of Wheat for $12,000

        Expected result: Loss of $8,000 ($12,000 - $20,000)
        """
        return pd.DataFrame(
            [
                {
                    "exchange_id": "EX_INFLOW_001",
                    "from_warehouse": "WH_SUPPLIER_999",
                    "to_warehouse": "WH_TEST_123",  # This is an INFLOW (purchase)
                    "brand_manufacturer": "Test Grain Co",
                    "item_type": "Wheat",
                    "commodity_standard": "bulk",
                    "quantity": 100.0,
                    "unit": "tons",
                    "price_paid_usd": 20000.00,  # Cost to buy wheat
                    "timestamp": "2023-06-01T10:00:00Z",
                    "batch_id": None,
                    "item_ids": None,
                },
                {
                    "exchange_id": "EX_OUTFLOW_002",
                    "from_warehouse": "WH_TEST_123",  # This is an OUTFLOW (sale)
                    "to_warehouse": "WH_CUSTOMER_888",
                    "brand_manufacturer": "Test Grain Co",
                    "item_type": "Wheat",
                    "commodity_standard": "bulk",
                    "quantity": 50.0,
                    "unit": "tons",
                    "price_paid_usd": 12000.00,  # Revenue from selling wheat
                    "timestamp": "2023-06-15T14:30:00Z",
                    "batch_id": None,
                    "item_ids": None,
                },
            ]
        )

    @pytest.fixture
    def mock_supabase_client(self, mock_warehouse_data, mock_exchange_data):
        """Mock SupabaseClient with realistic responses"""
        mock_client = Mock()

        # Mock warehouse lookup
        mock_client.find.side_effect = lambda table, filters: {
            "warehouses": (
                mock_warehouse_data
                if filters.get("warehouse_id") == "WH_TEST_123"
                else pd.DataFrame()
            ),
            "exchanges": self._filter_exchanges(mock_exchange_data, filters),
        }[table]

        return mock_client

    def _filter_exchanges(
        self, exchange_data: pd.DataFrame, filters: Dict[str, Any]
    ) -> pd.DataFrame:
        """Helper to filter exchange data based on mock database query"""
        df = exchange_data.copy()

        # Apply filters
        for key, value in filters.items():
            if key in df.columns:
                df = df[df[key] == value]

        return df

    @pytest.fixture
    def expected_results(self):
        """Expected calculation results for the test data"""
        return {
            "total_inflow_cost": Decimal("20000.00"),  # Bought wheat for $20,000
            "total_outflow_value": Decimal("12000.00"),  # Sold wheat for $12,000
            "total_gain_loss": Decimal("-8000.00"),  # Loss of $8,000
            "total_transactions": 2,  # 2 exchanges total
            "wheat_inflow_cost": Decimal("20000.00"),  # All wheat purchases
            "wheat_outflow_value": Decimal("12000.00"),  # All wheat sales
            "wheat_gain_loss": Decimal("-8000.00"),  # Wheat-specific loss
            "wheat_transactions": 2,  # 2 wheat transactions
        }

    def test_pure_logic_with_exchange_objects(self, expected_results):
        """Test the pure business logic with Exchange objects directly"""

        # Create Exchange objects manually
        exchanges = [
            Exchange(
                exchange_id="EX_INFLOW_001",
                from_warehouse="WH_SUPPLIER_999",
                to_warehouse="WH_TEST_123",
                brand_manufacturer="Test Grain Co",
                item_type="Wheat",
                commodity_standard=CommodityStandard.BULK,
                quantity=Decimal("100.0"),
                unit="tons",
                price_paid_usd=Decimal("20000.00"),
                timestamp=datetime(2023, 6, 1, 10, 0, 0),
            ),
            Exchange(
                exchange_id="EX_OUTFLOW_002",
                from_warehouse="WH_TEST_123",
                to_warehouse="WH_CUSTOMER_888",
                brand_manufacturer="Test Grain Co",
                item_type="Wheat",
                commodity_standard=CommodityStandard.BULK,
                quantity=Decimal("50.0"),
                unit="tons",
                price_paid_usd=Decimal("12000.00"),
                timestamp=datetime(2023, 6, 15, 14, 30, 0),
            ),
        ]

        # Call pure business logic
        report = calculate_warehouse_gains(
            warehouse_id="WH_TEST_123",
            exchanges=iter(exchanges),
            analysis_date=datetime(2023, 7, 1),
            reporter_name="Test Reporter",
        )

        # Verify results
        assert report.warehouse_id == "WH_TEST_123"
        assert report.reporter_name == "Test Reporter"
        assert report.total_inflow_cost == expected_results["total_inflow_cost"]
        assert report.total_outflow_value == expected_results["total_outflow_value"]
        assert report.total_gain_loss == expected_results["total_gain_loss"]
        assert report.total_transactions == expected_results["total_transactions"]

        # Verify commodity breakdown
        assert len(report.gains_by_commodity) == 1
        wheat_gains = report.gains_by_commodity[0]
        assert wheat_gains.commodity_type == "Wheat"
        assert wheat_gains.total_inflow_cost == expected_results["wheat_inflow_cost"]
        assert (
            wheat_gains.total_outflow_value == expected_results["wheat_outflow_value"]
        )
        assert wheat_gains.total_gain_loss == expected_results["wheat_gain_loss"]
        assert (
            wheat_gains.number_of_transactions == expected_results["wheat_transactions"]
        )

        # Verify date range
        assert report.analysis_start_date == datetime(2023, 6, 1, 10, 0, 0)
        assert report.analysis_end_date == datetime(2023, 6, 15, 14, 30, 0)

    @patch("src.flows.warehouse_gains_flow.SupabaseClient")
    def test_complete_flow_with_mocked_database(
        self, mock_client_class, mock_supabase_client, expected_results
    ):
        """Test the complete flow with mocked database client"""

        # Configure the mock client class to return our mock instance
        mock_client_class.return_value = mock_supabase_client

        # Call the complete flow
        report = analyze_warehouse_gains(
            warehouse_id="WH_TEST_123", client=mock_supabase_client
        )

        # Verify the same results as pure logic test
        assert report.warehouse_id == "WH_TEST_123"
        assert report.total_inflow_cost == expected_results["total_inflow_cost"]
        assert report.total_outflow_value == expected_results["total_outflow_value"]
        assert report.total_gain_loss == expected_results["total_gain_loss"]
        assert report.total_transactions == expected_results["total_transactions"]

        # Verify database calls were made correctly
        expected_warehouse_call = mock_supabase_client.find.call_args_list[0]
        assert expected_warehouse_call[0][0] == "warehouses"
        assert expected_warehouse_call[0][1] == {"warehouse_id": "WH_TEST_123"}

    def test_exchange_helper_methods(self):
        """Test the Exchange model helper methods work correctly"""

        # Test inflow exchange
        inflow_exchange = Exchange(
            exchange_id="EX_001",
            from_warehouse="WH_OTHER",
            to_warehouse="WH_TEST_123",
            brand_manufacturer="Test Co",
            item_type="Wheat",
            commodity_standard=CommodityStandard.BULK,
            quantity=Decimal("100"),
            unit="tons",
            price_paid_usd=Decimal("10000"),
            timestamp=datetime.now(),
        )

        assert inflow_exchange.is_inflow_for("WH_TEST_123") == True
        assert inflow_exchange.is_outflow_for("WH_TEST_123") == False
        assert inflow_exchange.is_relevant_for("WH_TEST_123") == True
        assert inflow_exchange.is_bulk() == True

        # Test outflow exchange
        outflow_exchange = Exchange(
            exchange_id="EX_002",
            from_warehouse="WH_TEST_123",
            to_warehouse="WH_OTHER",
            brand_manufacturer="Test Co",
            item_type="Wheat",
            commodity_standard=CommodityStandard.BULK,
            quantity=Decimal("50"),
            unit="tons",
            price_paid_usd=Decimal("6000"),
            timestamp=datetime.now(),
        )

        assert outflow_exchange.is_inflow_for("WH_TEST_123") == False
        assert outflow_exchange.is_outflow_for("WH_TEST_123") == True
        assert outflow_exchange.is_relevant_for("WH_TEST_123") == True

    def test_empty_exchanges(self):
        """Test behavior with no exchanges"""

        report = calculate_warehouse_gains(
            warehouse_id="WH_EMPTY",
            exchanges=iter([]),  # Empty iterator
            analysis_date=datetime.now(),
            reporter_name="Test Reporter",
        )

        assert report.warehouse_id == "WH_EMPTY"
        assert report.total_inflow_cost == Decimal("0")
        assert report.total_outflow_value == Decimal("0")
        assert report.total_gain_loss == Decimal("0")
        assert report.total_transactions == 0
        assert len(report.gains_by_commodity) == 0
        assert report.analysis_start_date is None
        assert report.analysis_end_date is None

    def test_multiple_commodities(self):
        """Test with multiple commodity types"""

        exchanges = [
            Exchange(
                exchange_id="EX_WHEAT_IN",
                from_warehouse="WH_OTHER",
                to_warehouse="WH_TEST_123",
                brand_manufacturer="Grain Co",
                item_type="Wheat",
                commodity_standard=CommodityStandard.BULK,
                quantity=Decimal("100"),
                unit="tons",
                price_paid_usd=Decimal("10000"),
                timestamp=datetime(2023, 6, 1),
            ),
            Exchange(
                exchange_id="EX_STEEL_IN",
                from_warehouse="WH_OTHER",
                to_warehouse="WH_TEST_123",
                brand_manufacturer="Steel Co",
                item_type="Steel",
                commodity_standard=CommodityStandard.BULK,
                quantity=Decimal("50"),
                unit="tons",
                price_paid_usd=Decimal("25000"),
                timestamp=datetime(2023, 6, 2),
            ),
            Exchange(
                exchange_id="EX_WHEAT_OUT",
                from_warehouse="WH_TEST_123",
                to_warehouse="WH_OTHER",
                brand_manufacturer="Grain Co",
                item_type="Wheat",
                commodity_standard=CommodityStandard.BULK,
                quantity=Decimal("80"),
                unit="tons",
                price_paid_usd=Decimal("12000"),
                timestamp=datetime(2023, 6, 10),
            ),
        ]

        report = calculate_warehouse_gains(
            warehouse_id="WH_TEST_123",
            exchanges=iter(exchanges),
            analysis_date=datetime.now(),
            reporter_name="Test Reporter",
        )

        # Overall totals
        assert report.total_inflow_cost == Decimal("35000")  # 10000 + 25000
        assert report.total_outflow_value == Decimal("12000")  # 12000
        assert report.total_gain_loss == Decimal("-23000")  # 12000 - 35000
        assert report.total_transactions == 3

        # Should have 2 commodity types
        assert len(report.gains_by_commodity) == 2

        # Find wheat and steel gains
        wheat_gains = next(
            c for c in report.gains_by_commodity if c.commodity_type == "Wheat"
        )
        steel_gains = next(
            c for c in report.gains_by_commodity if c.commodity_type == "Steel"
        )

        # Wheat: bought 10000, sold 12000 = +2000 gain
        assert wheat_gains.total_inflow_cost == Decimal("10000")
        assert wheat_gains.total_outflow_value == Decimal("12000")
        assert wheat_gains.total_gain_loss == Decimal("2000")
        assert wheat_gains.number_of_transactions == 2

        # Steel: bought 25000, sold 0 = -25000 loss
        assert steel_gains.total_inflow_cost == Decimal("25000")
        assert steel_gains.total_outflow_value == Decimal("0")
        assert steel_gains.total_gain_loss == Decimal("-25000")
        assert steel_gains.number_of_transactions == 1

    def test_calculation_validation(self):
        """Test that calculations are mathematically correct"""

        # Test data with known results
        exchanges = [
            # Buy 100 tons wheat @ $200/ton = $20,000
            Exchange(
                exchange_id="EX_001",
                from_warehouse="WH_OTHER",
                to_warehouse="WH_TEST",
                brand_manufacturer="Co",
                item_type="Wheat",
                commodity_standard=CommodityStandard.BULK,
                quantity=Decimal("100"),
                unit="tons",
                price_paid_usd=Decimal("20000"),
                timestamp=datetime.now(),
            ),
            # Sell 60 tons wheat @ $250/ton = $15,000
            Exchange(
                exchange_id="EX_002",
                from_warehouse="WH_TEST",
                to_warehouse="WH_OTHER",
                brand_manufacturer="Co",
                item_type="Wheat",
                commodity_standard=CommodityStandard.BULK,
                quantity=Decimal("60"),
                unit="tons",
                price_paid_usd=Decimal("15000"),
                timestamp=datetime.now(),
            ),
        ]

        report = calculate_warehouse_gains("WH_TEST", iter(exchanges))

        # Manual calculation verification
        expected_inflow = Decimal("20000")
        expected_outflow = Decimal("15000")
        expected_gain = expected_outflow - expected_inflow  # -5000

        assert report.total_inflow_cost == expected_inflow
        assert report.total_outflow_value == expected_outflow
        assert report.total_gain_loss == expected_gain

        # Verify commodity breakdown adds up to totals
        commodity_total_inflow = sum(
            c.total_inflow_cost for c in report.gains_by_commodity
        )
        commodity_total_outflow = sum(
            c.total_outflow_value for c in report.gains_by_commodity
        )
        commodity_total_gain = sum(c.total_gain_loss for c in report.gains_by_commodity)

        assert commodity_total_inflow == report.total_inflow_cost
        assert commodity_total_outflow == report.total_outflow_value
        assert commodity_total_gain == report.total_gain_loss


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
