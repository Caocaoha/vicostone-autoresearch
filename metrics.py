"""
Vicostone Sentiment Monitor - Metrics
Composite score calculation inspired by val_bpb in AutoResearch

Composite Score = Higher is Better
Formula designed to balance sentiment quality with coverage
"""

import math
from typing import List, Dict


def calculate_composite_score(
    avg_sentiment: float,
    sources_collected: int,
    sentiment_std: float = 0.5,
    max_expected_sources: int = 30,
    sentiment_weight: float = 0.4,
    sources_weight: float = 0.3,
    consistency_weight: float = 0.3
) -> float:
    """
    Calculate composite sentiment score
    Inspired by val_bpb optimization in Karpathy's AutoResearch
    
    Args:
        avg_sentiment: Average sentiment score (-2 to +2)
        sources_collected: Number of sources collected
        sentiment_std: Standard deviation of sentiment (for consistency)
        max_expected_sources: Normalization factor for sources
        sentiment_weight: Weight for avg_sentiment (default 0.4)
        sources_weight: Weight for sources coverage (default 0.3)
        consistency_weight: Weight for consistency (default 0.3)
    
    Returns:
        float: Composite score (higher is better)
    
    Formula:
        composite = (
            avg_sentiment * sentiment_weight +
            sqrt(sources_collected) / sqrt(max_expected) * sources_weight +
            (1 - sentiment_std/4) * consistency_weight
        )
    """
    # Normalize sources (sqrt normalization to reduce impact of large numbers)
    sources_norm = math.sqrt(sources_collected) / math.sqrt(max_expected_sources)
    
    # Calculate consistency (1 - normalized_std)
    # sentiment_std ranges 0-4, we want 1 for consistent, 0 for random
    consistency = max(0, 1 - (sentiment_std / 4))
    
    # Weighted composite
    composite = (
        avg_sentiment * sentiment_weight +
        sources_norm * sources_weight +
        consistency * consistency_weight
    )
    
    return composite


def calculate_sentiment_consistency(sentiments: List[float]) -> float:
    """
    Calculate sentiment consistency from a list of sentiment scores
    Lower std = more consistent = higher consistency score
    
    Returns:
        float: Standard deviation of sentiments (0-4 scale)
    """
    if not sentiments:
        return 0.5  # Default medium consistency
    
    n = len(sentiments)
    
    # Calculate mean
    mean = sum(sentiments) / n
    
    # Calculate standard deviation
    variance = sum((s - mean) ** 2 for s in sentiments) / n
    std = math.sqrt(variance)
    
    return min(std, 4.0)  # Cap at 4


def score_to_trend(current_score: float, previous_score: float) -> str:
    """
    Convert score change to trend description
    
    Returns:
        str: "improving", "stable", or "declining"
    """
    if previous_score == 0:
        return "stable"
    
    change_pct = (current_score - previous_score) / previous_score
    
    if change_pct > 0.05:  # >5% improvement
        return "improving"
    elif change_pct < -0.05:  # >5% decline
        return "declining"
    else:
        return "stable"


def evaluate_experiment(
    experiment_score: float,
    baseline_score: float,
    improvement_threshold: float = 0.01
) -> Dict[str, any]:
    """
    Evaluate an experiment result
    
    Returns:
        dict with keys: improved (bool), change_pct (float), status (str)
    """
    change_pct = (experiment_score - baseline_score) / baseline_score if baseline_score != 0 else 0
    
    improved = experiment_score > baseline_score * (1 + improvement_threshold)
    
    status = "improved" if improved else "neutral"
    if change_pct < -0.05:
        status = "reverted"
    
    return {
        "improved": improved,
        "change_pct": change_pct,
        "status": status,
        "baseline": baseline_score,
        "experiment": experiment_score
    }


# ===========================
# METRIC FORMULAS (Reference)
# ===========================

# AutoResearch (Karpathy):
#   val_bpb = validation bits per byte
#   Lower = Better
#
# Vicostone Sentiment:
#   composite_score = sentiment * 0.4 + sources_norm * 0.3 + consistency * 0.3
#   Higher = Better

METRIC_REFERENCE = """
Metric Comparison:
==================

AutoResearch val_bpb:
  - Purpose: Compression efficiency
  - Lower = Better
  - Range: ~0.9-1.0 for text

Vicostone composite_score:
  - Purpose: Sentiment analysis quality
  - Higher = Better
  - Range: ~0.5-2.5 typical
  
Key Difference:
  - AutoResearch optimizes for LOWER (compression)
  - Vicostone optimizes for HIGHER (sentiment quality)
  - Both use weighted composite formulas
"""
