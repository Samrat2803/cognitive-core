"""
SitRep Generator Configuration
"""

import os
from datetime import datetime, timedelta

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

DEFAULT_MODEL = "gpt-4o-mini"
TEMPERATURE = 0  # Always 0 for consistency

# ============================================================================
# TIME PERIODS
# ============================================================================

PERIOD_CONFIGS = {
    "daily": {
        "days": 1,
        "label": "Daily",
        "description": "Last 24 hours"
    },
    "weekly": {
        "days": 7,
        "label": "Weekly",
        "description": "Last 7 days"
    },
    "custom": {
        "days": None,  # User-specified
        "label": "Custom",
        "description": "User-defined date range"
    }
}

# ============================================================================
# PRIORITY THRESHOLDS
# ============================================================================

PRIORITY_LEVELS = {
    "urgent": {
        "min_score": 80,
        "max_score": 100,
        "emoji": "🔴",
        "label": "URGENT",
        "description": "Critical developments requiring immediate attention"
    },
    "high": {
        "min_score": 60,
        "max_score": 79,
        "emoji": "🟠",
        "label": "HIGH PRIORITY",
        "description": "Significant developments affecting regional dynamics"
    },
    "notable": {
        "min_score": 40,
        "max_score": 59,
        "emoji": "🟡",
        "label": "NOTABLE",
        "description": "Important developments worth monitoring"
    },
    "routine": {
        "min_score": 0,
        "max_score": 39,
        "emoji": "⚪",
        "label": "ROUTINE",
        "description": "Standard political activity"
    }
}

# ============================================================================
# REGIONS
# ============================================================================

REGIONS = [
    "United States",
    "Europe",
    "Middle East",
    "Asia Pacific",
    "Latin America",
    "Africa",
    "Russia",
    "Global"
]

REGION_KEYWORDS = {
    "United States": ["US", "USA", "United States", "Washington", "Congress", "White House"],
    "Europe": ["EU", "Europe", "European Union", "UK", "France", "Germany", "Brussels"],
    "Middle East": ["Middle East", "Israel", "Iran", "Saudi Arabia", "UAE", "Iraq", "Syria"],
    "Asia Pacific": ["China", "Japan", "India", "Korea", "Taiwan", "ASEAN", "Australia"],
    "Latin America": ["Mexico", "Brazil", "Argentina", "Venezuela", "Colombia", "Chile"],
    "Africa": ["Africa", "Nigeria", "South Africa", "Egypt", "Kenya", "Ethiopia"],
    "Russia": ["Russia", "Moscow", "Kremlin", "Putin"]
}

# ============================================================================
# REPORT LIMITS
# ============================================================================

MAX_URGENT_EVENTS = 5  # Max urgent events to include in report
MAX_HIGH_PRIORITY_EVENTS = 10  # Max high priority events
MAX_NOTABLE_EVENTS = 15  # Max notable events
MAX_TRENDING_TOPICS = 8  # Max trending topics to show
MAX_WATCH_LIST_ITEMS = 10  # Max items in watch list

# ============================================================================
# ARTIFACT SETTINGS
# ============================================================================

ARTIFACT_DIR = "artifacts"
ARTIFACT_FORMATS = ["html", "pdf", "txt", "json"]

# Ensure artifact directory exists
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# ============================================================================
# AISTRA COLOR PALETTE
# ============================================================================

COLORS = {
    "primary": "#d9f378",      # Bright green
    "secondary": "#5d535c",    # Purple-gray
    "dark": "#333333",         # Dark gray
    "darkest": "#1c1e20",      # Almost black
    "white": "#FFFFFF",
    "accent": "#00D9FF",       # Bright cyan
    "urgent": "#e74c3c",       # Red
    "high": "#f39c12",         # Orange
    "notable": "#3498db",      # Blue
    "routine": "#95a5a6"       # Gray
}

# ============================================================================
# HTML TEMPLATE SETTINGS
# ============================================================================

FONT_FAMILY = "'Roboto Flex', Arial, sans-serif"
CONTAINER_MAX_WIDTH = "900px"
PADDING = "40px"

# ============================================================================
# SUMMARY GENERATION SETTINGS
# ============================================================================

EXECUTIVE_SUMMARY_MAX_SENTENCES = 4  # 3-4 sentences
EXECUTIVE_SUMMARY_STYLE = "Direct, factual, no speculation. Written for senior policymakers/executives."

# ============================================================================
# WATCH LIST SETTINGS
# ============================================================================

WATCH_LIST_TIMEFRAME_HOURS = 48  # Next 24-48 hours
WATCH_LIST_KEYWORDS = [
    "scheduled",
    "expected",
    "upcoming",
    "planned",
    "vote",
    "summit",
    "meeting",
    "election",
    "deadline",
    "announcement"
]

# ============================================================================
# DEFAULT VALUES
# ============================================================================

DEFAULT_PERIOD = "daily"
DEFAULT_REGION = None  # None = all regions
DEFAULT_TOPIC = None  # None = all topics

