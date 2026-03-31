"""
Vicostone Sentiment Monitor — AutoResearch Module
GPU: NVIDIA T4 16GB (Google Colab)
Metric: composite_sentiment_score
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

# ===========================
# CONFIGURATION
# ===========================

class VicostoneConfig:
    """Parameters to tune - changed one at a time per experiment"""
    
    # Default parameters (can be changed during experiments)
    PERPLEXITY_QUERIES = 15          # Range: 10-20
    FORUMS_TO_CHECK = 6              # Range: 4-10
    MIN_REVIEW_LENGTH = 20          # Range: 10-50 chars
    SENTIMENT_THRESHOLD = 1.0        # Range: 0.5-1.5
    MAX_SOURCES_PER_QUERY = 10       # Range: 5-20
    
    # Fixed parameters (DO NOT CHANGE)
    SENTIMENT_SCALE = [-2, -1, 0, 1, 2]
    DATA_DIR = Path("memory/vicostone-sentiment")
    CHART_DIR = Path("memory/vicostone-sentiment/charts")
    EXPERIMENT_LOG = Path("memory/vicostone-sentiment/experiment_log.tsv")


class VicostoneMonitor:
    """Main module for Vicostone Sentiment Monitor AutoResearch"""
    
    def __init__(self, perplexity_api_key: str, output_dir: str = "."):
        self.config = VicostoneConfig()
        self.output_dir = Path(output_dir)
        self.perplexity_api_key = perplexity_api_key
        self.data_dir = self.output_dir / "memory" / "vicostone-sentiment"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "daily").mkdir(exist_ok=True)
        (self.data_dir / "charts").mkdir(exist_ok=True)
        (self.data_dir / "tmp").mkdir(exist_ok=True)
        
        # Experiment tracking
        self.experiment_log = self.data_dir / "experiment_log.tsv"
        self._init_experiment_log()
    
    def _init_experiment_log(self):
        """Initialize experiment log if not exists"""
        if not self.experiment_log.exists():
            header = "date\tparam_changed\told_value\tnew_value\tavg_sentiment\tsources\tcomposite_score\ttrend\tstatus\tnotes\n"
            with open(self.experiment_log, 'w') as f:
                f.write(header)
    
    def collect_data(self) -> dict:
        """
        Collect sentiment data from Perplexity API and other sources
        Returns: dict with collected data
        """
        print(f"[VicostoneMonitor] Collecting data with {self.config.PERPLEXITY_QUERIES} queries...")
        
        # Placeholder - actual implementation would call Perplexity API
        # For now, simulate data collection
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "sources_collected": self.config.FORUMS_TO_CHECK * 2,  # Simulated
            "items": [],
            "config_used": {
                "perplexity_queries": self.config.PERPLEXITY_QUERIES,
                "forums_to_check": self.config.FORUMS_TO_CHECK,
                "min_review_length": self.config.MIN_REVIEW_LENGTH
            }
        }
        
        print(f"[VicostoneMonitor] Collected {data['sources_collected']} sources")
        return data
    
    def calculate_sentiment(self, data: dict) -> float:
        """
        Calculate composite sentiment score from collected data
        Metric: Higher is better
        """
        avg_sentiment = 0.94  # Simulated - would be calculated from actual data
        sources = data.get("sources_collected", 18)
        
        # Composite score formula (inspired by val_bpb optimization)
        import math
        sources_norm = math.sqrt(sources) / math.sqrt(30)  # 30 = max expected
        sentiment_consistency = 0.85  # Simulated
        
        composite = (
            avg_sentiment * 0.4 +
            sources_norm * 0.3 +
            sentiment_consistency * 0.3
        )
        
        print(f"[VicostoneMonitor] Composite score: {composite:.3f}")
        return composite
    
    def run_day(self) -> dict:
        """Run one day of data collection and scoring"""
        print(f"\n{'='*50}")
        print(f"Vicostone AutoResearch - Day Run")
        print(f"{'='*50}")
        
        # Collect data
        data = self.collect_data()
        
        # Calculate composite score
        composite_score = self.calculate_sentiment(data)
        
        result = {
            "date": data["date"],
            "composite_score": composite_score,
            "config": data["config_used"],
            "sources": data["sources_collected"]
        }
        
        return result
    
    def run_baseline(self) -> float:
        """Run baseline with current parameters"""
        print("\n" + "="*50)
        print("RUNNING BASELINE")
        print("="*50)
        
        result = self.run_day()
        
        # Save to experiment log
        self._log_experiment(
            date=result["date"],
            param_changed="baseline",
            old_value="-",
            new_value="-",
            avg_sentiment="+0.94",
            sources=str(result["sources"]),
            composite_score=f"{result['composite_score']:.2f}",
            trend="stable",
            status="baseline",
            notes="First run"
        )
        
        print(f"\nBaseline complete: {result['composite_score']:.3f}")
        return result["composite_score"]
    
    def autonomous_loop(self, days: int = 7):
        """Run autonomous experiment loop for N days"""
        print(f"\n{'='*50}")
        print(f"AUTONOMOUS LOOP - {days} days")
        print(f"{'='*50}")
        
        baseline = self.run_baseline()
        print(f"Baseline: {baseline:.3f}")
        
        # Experiment loop would go here
        # For now, just log the run
        print(f"\nAutonomous loop complete. Check experiment_log.tsv for results.")


class VicostoneExperiment:
    """High-level interface for Vicostone AutoResearch"""
    
    def __init__(self, perplexity_api_key: str = None, output_dir: str = "."):
        self.perplexity_api_key = perplexity_api_key or os.environ.get('PERPLEXITY_API_KEY', '')
        self.output_dir = output_dir
        self.monitor = VicostoneMonitor(
            perplexity_api_key=self.perplexity_api_key,
            output_dir=self.output_dir
        )
    
    def run_baseline(self) -> float:
        """Run baseline measurement"""
        return self.monitor.run_baseline()
    
    def autonomous_loop(self, days: int = 7):
        """Run autonomous loop for N days"""
        self.monitor.autonomous_loop(days=days)


# ===========================
# HELPER FUNCTIONS
# ===========================

def calculate_composite_score(avg_sentiment: float, sources_collected: int, 
                               perplexity_queries: int) -> float:
    """
    Calculate composite sentiment score
    Formula inspired by val_bpb optimization in AutoResearch
    """
    import math
    
    sources_norm = math.sqrt(sources_collected) / math.sqrt(30)
    consistency = 0.85  # Placeholder - calculate from actual data
    
    composite = (
        avg_sentiment * 0.4 +
        sources_norm * 0.3 +
        consistency * 0.3
    )
    
    return composite
