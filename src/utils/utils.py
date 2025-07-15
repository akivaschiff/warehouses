"""
Utility functions for the warehouse exchange system.
"""

import os


def get_reporter_name() -> str:
    """
    Get the reporter name from environment variable.
    
    Returns:
        Reporter name from REPORTER_NAME env var, or default
    """
    return os.getenv('REPORTER_NAME', 'Unknown Reporter') 