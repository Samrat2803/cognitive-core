"""Utility functions for Deep Investigative Reporter"""
from .entity_extraction import extract_entities_from_text, extract_facts_from_results, create_entity_record
from .pattern_detection import detect_suspicious_patterns, find_contradictions, identify_clusters
from .causal_extraction import extract_causal_relationships, build_causal_chains
from .network_builder import build_network_graph, build_causal_diagram

__all__ = [
    "extract_entities_from_text",
    "extract_facts_from_results",
    "create_entity_record",
    "detect_suspicious_patterns",
    "find_contradictions",
    "identify_clusters",
    "extract_causal_relationships",
    "build_causal_chains",
    "build_network_graph",
    "build_causal_diagram"
]


