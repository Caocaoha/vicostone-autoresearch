"""
Vicostone Sentiment Monitor - Parameters
Inspired by Karpathy's AutoResearch train.py concept

This file contains ALL parameters that can be tuned.
Each experiment changes ONE parameter at a time.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class VicostoneParams:
    """
    Parameters for Vicostone Sentiment Monitor
    Similar to how train.py contains hyperparameters in AutoResearch
    """
    
    # ===========================
    # DATA COLLECTION PARAMETERS
    # ===========================
    
    perplexity_queries: int = 15
    """Number of Perplexity API queries per day (range: 10-20)"""
    
    forums_to_check: int = 6
    """Number of forums to check per day (range: 4-10)"""
    
    max_sources_per_query: int = 10
    """Maximum sources to collect per query (range: 5-20)"""
    
    # ===========================
    # SENTIMENT ANALYSIS PARAMETERS
    # ===========================
    
    min_review_length: int = 20
    """Minimum review length in characters to evaluate (range: 10-50)"""
    
    sentiment_threshold: float = 1.0
    """Threshold for notable mention (range: 0.5-1.5)"""
    
    batch_size: int = 10
    """Number of reviews to batch for scoring (range: 5-15)"""
    
    # ===========================
    # SCORING PARAMETERS
    # ===========================
    
    sentiment_weight: float = 0.4
    """Weight for avg_sentiment in composite score"""
    
    sources_weight: float = 0.3
    """Weight for sources_collected in composite score"""
    
    consistency_weight: float = 0.3
    """Weight for sentiment_consistency in composite score"""
    
    max_expected_sources: int = 30
    """Maximum expected sources for normalization"""
    
    # ===========================
    # FIXED PARAMETERS (DO NOT CHANGE)
    # ===========================
    
    SENTIMENT_SCALE: List[int] = None
    """Sentiment scale: -2 to +2"""
    
    def __post_init__(self):
        if self.SENTIMENT_SCALE is None:
            self.SENTIMENT_SCALE = [-2, -1, 0, 1, 2]


# ===========================
# PARAMETER SEARCH SPACE
# ===========================

PARAM_SEARCH_SPACE = {
    "perplexity_queries": {
        "name": "perplexity_queries",
        "default": 15,
        "range": [10, 12, 14, 16, 18, 20],
        "step": 2,
        "priority": "high",
        "description": "Number of Perplexity API queries per day"
    },
    "forums_to_check": {
        "name": "forums_to_check",
        "default": 6,
        "range": [4, 5, 6, 7, 8, 9, 10],
        "step": 1,
        "priority": "medium",
        "description": "Number of forums to check per day"
    },
    "min_review_length": {
        "name": "min_review_length",
        "default": 20,
        "range": [10, 20, 30, 40, 50],
        "step": 10,
        "priority": "medium",
        "description": "Minimum review length in characters"
    },
    "sentiment_threshold": {
        "name": "sentiment_threshold",
        "default": 1.0,
        "range": [0.5, 0.7, 0.9, 1.1, 1.3, 1.5],
        "step": 0.2,
        "priority": "low",
        "description": "Threshold for notable mention"
    },
    "max_sources_per_query": {
        "name": "max_sources_per_query",
        "default": 10,
        "range": [5, 10, 15, 20],
        "step": 5,
        "priority": "low",
        "description": "Maximum sources per query"
    }
}


# ===========================
# DEFAULT CONFIGURATION
# ===========================

DEFAULT_PARAMS = VicostoneParams()


# ===========================
# HELPER FUNCTIONS
# ===========================

def get_current_params() -> VicostoneParams:
    """Get current parameters"""
    return DEFAULT_PARAMS


def update_param(param_name: str, new_value) -> VicostoneParams:
    """
    Update a single parameter
    Returns: Updated VicostoneParams
    """
    if hasattr(DEFAULT_PARAMS, param_name):
        setattr(DEFAULT_PARAMS, param_name, new_value)
    return DEFAULT_PARAMS


def validate_param(param_name: str, value) -> bool:
    """
    Validate if a parameter value is within acceptable range
    Returns: True if valid
    """
    if param_name not in PARAM_SEARCH_SPACE:
        return False
    
    range_values = PARAM_SEARCH_SPACE[param_name]["range"]
    return value in range_values


def get_next_value(param_name: str, current_value):
    """
    Get next value in the search space for a parameter
    Returns: Next value in range, or first value if at end
    """
    if param_name not in PARAM_SEARCH_SPACE:
        return current_value
    
    range_values = PARAM_SEARCH_SPACE[param_name]["range"]
    
    if current_value not in range_values:
        return range_values[0]
    
    current_index = range_values.index(current_value)
    next_index = (current_index + 1) % len(range_values)
    
    return range_values[next_index]
