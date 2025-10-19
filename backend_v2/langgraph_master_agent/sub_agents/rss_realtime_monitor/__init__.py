"""
RSS Realtime Monitor Sub-Agent

Monitors RSS feeds and detects explosive topics using clustering and scoring.
"""

from rss_realtime_monitor.graph import create_rss_realtime_monitor_graph
from rss_realtime_monitor.state import RSSRealtimeMonitorState

__all__ = [
    "create_rss_realtime_monitor_graph",
    "RSSRealtimeMonitorState"
]

