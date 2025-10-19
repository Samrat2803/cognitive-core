"""
Tools for Investigative Journalist
"""

from .evidence_repository import (
    save_investigation,
    load_investigation,
    get_investigation_summary,
    list_investigations
)

__all__ = [
    'save_investigation',
    'load_investigation',
    'get_investigation_summary',
    'list_investigations'
]

