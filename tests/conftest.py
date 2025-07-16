"""Pytest configuration and fixtures"""

import pytest
import pandas as pd


@pytest.fixture
def sample_exchange():
    """Sample exchange for testing"""
    return {
        "exchange_id": "test-123",
        "from_warehouse": "WH_A",
        "to_warehouse": "WH_B",
        "commodity_standard": "bulk",
        "quantity": 100.0,
        "price_paid_usd": 5000.0,
    }
