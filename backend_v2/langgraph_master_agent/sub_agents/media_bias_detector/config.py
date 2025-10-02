"""
Configuration for Media Bias Detector Agent
"""

import os

# LLM Configuration
MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
TEMPERATURE = 0  # Always 0 for consistency

# Default Sources to Analyze (if not specified by user)
# Mix of left-leaning, right-leaning, and centrist sources
DEFAULT_SOURCES = [
    "cnn.com",
    "foxnews.com",
    "bbc.com",
    "reuters.com",
    "nytimes.com",
    "wsj.com",
    "theguardian.com",
    "apnews.com"
]

# Search Configuration
MAX_SOURCES = 8
MAX_ARTICLES_PER_SOURCE = 3
DEFAULT_TIME_RANGE_DAYS = 7
SEARCH_DEPTH = "advanced"  # More thorough for media analysis

# Bias Classification Spectrum
BIAS_SPECTRUM = {
    "far_left": -1.0,
    "left": -0.6,
    "center_left": -0.3,
    "center": 0.0,
    "center_right": 0.3,
    "right": 0.6,
    "far_right": 1.0
}

# Loaded Language Categories
LOADED_LANGUAGE_TYPES = [
    "emotionally_charged",      # Emotional manipulation
    "sensationalist",           # Exaggeration
    "fear_based",               # Fear-mongering
    "propaganda_terms",         # Propaganda language
    "euphemisms",               # Softening language
    "dysphemisms",              # Harsh language
    "loaded_adjectives",        # Biased descriptors
    "false_equivalence"         # Misleading comparisons
]

# Framing Types (How stories are presented)
FRAMING_TYPES = [
    "conflict_frame",           # Us vs them, winners vs losers
    "human_interest",           # Personal stories, emotional angle
    "economic",                 # Financial impact, costs/benefits
    "morality",                 # Right vs wrong, ethical issues
    "responsibility",           # Who's to blame, accountability
    "progress",                 # Innovation, change, future
    "victim_frame",             # Portraying as victims
    "hero_frame"                # Portraying as heroes
]

# Bias Detection Techniques
BIAS_TECHNIQUES = [
    "selective_quoting",
    "omission",
    "placement",
    "labeling",
    "spin",
    "cherry_picking_facts",
    "false_balance",
    "strawman_argument"
]

# Visualization
ARTIFACT_DIR = "artifacts"
BIAS_COLOR_SCALE = ["#2E86AB", "#A6D7E8", "#E8E8E8", "#F4A261", "#E76F51"]  # Blue (left) to Red (right)

