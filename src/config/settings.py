"""Configuration settings for the warehouse system"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///warehouse.db")
