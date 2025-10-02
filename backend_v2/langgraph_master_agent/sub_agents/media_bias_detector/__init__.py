"""
Media Bias Detector Sub-Agent

Analyzes how different media sources cover the same political event/topic.
Detects framing bias, political lean, and loaded language usage.
"""

from .state import MediaBiasDetectorState
from .config import MODEL, TEMPERATURE, DEFAULT_SOURCES

__all__ = ["MediaBiasDetectorState", "MODEL", "TEMPERATURE", "DEFAULT_SOURCES"]

