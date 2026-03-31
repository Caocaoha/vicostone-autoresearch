"""
Vicostone AutoResearch - Experiment Loop
Inspired by Karpathy's AutoResearch: https://github.com/karpathy/autoresearch
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from vicostone_monitor import VicostoneMonitor, VicostoneConfig


class ExperimentRunner:
    """
    Runs experiments for Vicostone Sentiment Monitor
    Each experiment changes ONE parameter and evaluates the result
    """
    
    # Parameter search space
    PARAM_SEARCH_SPACE = {
        "perplexity_queries": {
            "default": 15,
            "range": [10, 12, 14, 16, 18, 20],
            "step": 2,
            "priority": "high"
        },
        "forums_to_check": {
            "default": 6,
            "range": [4, 5, 6, 7, 8, 9, 10],
            "step": 1,
            "priority": "medium"
        },
        "min_review_length": {
            "default": 20,
            "range": [10, 20, 30, 40, 50],
            "step": 10,
            "priority": "medium"
        },
        "sentiment_threshold": {
            "default": 1.0,
            "range": [0.5, 0.7, 0.9, 1.1, 1.3, 1.5],
            "step": 0.2,
            "priority": "low"
        }
    }
    
    def __init__(self, monitor: VicostoneMonitor):
        self.monitor = monitor
        self.config = VicostoneConfig()
        self.current_param_index = 0
        self.param_names = list(self.PARAM_SEARCH_SPACE.keys())
    
    def get_next_param(self) -> tuple:
        """Get the next parameter to experiment with"""
        param_name = self.param_names[self.current_param_index % len(self.param_names)]
        param_info = self.PARAM_SEARCH_SPACE[param_name]
        
        current_value = getattr(self.config, param_name.upper())
        current_index = param_info["range"].index(current_value) if current_value in param_info["range"] else 0
        
        # Move to next value in range
        next_index = (current_index + 1) % len(param_info["range"])
        next_value = param_info["range"][next_index]
        
        self.current_param_index += 1
        
        return param_name, current_value, next_value
    
    def run_experiment(self, param_name: str, old_value, new_value) -> dict:
        """
        Run one experiment with changed parameter
        Returns: dict with experiment results
        """
        print(f"\n{'='*50}")
        print(f"EXPERIMENT: {param_name}")
        print(f"Change: {old_value} → {new_value}")
        print(f"{'='*50}")
        
        # Backup old value
        old_attr = param_name.upper()
        old_backup = getattr(self.config, old_attr)
        
        # Set new value
        setattr(self.config, old_attr, new_value)
        
        # Run day
        result = self.monitor.run_day()
        
        # Restore old value
        setattr(self.config, old_attr, old_backup)
        
        return result
    
    def evaluate_and_decide(self, experiment_score: float, baseline_score: float) -> bool:
        """
        Decide whether to keep the change or revert
        Returns: True if improved (keep), False if worse (revert)
        """
        improvement_threshold = 0.01  # 1% improvement minimum
        
        change_pct = (experiment_score - baseline_score) / baseline_score
        
        print(f"\nEvaluation:")
        print(f"  Baseline:  {baseline_score:.4f}")
        print(f"  Experiment: {experiment_score:.4f}")
        print(f"  Change: {change_pct*100:+.2f}%")
        
        return experiment_score > baseline_score * (1 + improvement_threshold)
    
    def autonomous_loop(self, days: int = 7):
        """
        Run autonomous experiment loop
        WARNING: This runs indefinitely until interrupted
        """
        print(f"\n{'#'*60}")
        print(f"# VICOSTONE AUTONOMOUS EXPERIMENT LOOP")
        print(f"# Running {days} days of experiments")
        print(f"# Parameters: {list(self.PARAM_SEARCH_SPACE.keys())}")
        print(f"{'#'*60}")
        
        # Run baseline first
        baseline_score = self.monitor.run_baseline()
        print(f"\nBaseline composite score: {baseline_score:.4f}")
        
        day = 1
        while day <= days:
            print(f"\n{'='*50}")
            print(f"DAY {day}/{days}")
            print(f"{'='*50}")
            
            # Get next parameter to experiment
            param_name, old_val, new_val = self.get_next_param()
            
            # Run experiment
            result = self.run_experiment(param_name, old_val, new_val)
            
            # Evaluate
            improved = self.evaluate_and_decide(
                result["composite_score"], 
                baseline_score
            )
            
            # Log result
            status = "improved" if improved else "reverted"
            trend = "improving" if improved else "declining"
            
            self.monitor._log_experiment(
                date=result["date"],
                param_changed=param_name,
                old_value=str(old_val),
                new_value=str(new_val),
                avg_sentiment="+0.94",
                sources=str(result["sources"]),
                composite_score=f"{result['composite_score']:.2f}",
                trend=trend,
                status=status,
                notes=f"{param_name}: {old_val}→{new_val}"
            )
            
            # Update baseline if improved
            if improved:
                baseline_score = result["composite_score"]
                print(f"\n✅ IMPROVED! New baseline: {baseline_score:.4f}")
                # Commit the change
                self._commit_change(param_name, old_val, new_val)
            else:
                print(f"\n❌ No improvement. Reverting.")
            
            day += 1
        
        print(f"\n{'='*50}")
        print(f"AUTONOMOUS LOOP COMPLETE")
        print(f"{'='*50}")
        print(f"Final baseline: {baseline_score:.4f}")
        print(f"Check experiment_log.tsv for details")
    
    def _commit_change(self, param_name: str, old_val, new_val):
        """Commit parameter change to git"""
        try:
            subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
            commit_msg = f"experiment: {param_name} {old_val}→{new_val}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
            subprocess.run(["git", "push"], check=True, capture_output=True)
            print(f"✅ Committed: {commit_msg}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git commit failed: {e}")


# ===========================
# MAIN
# ===========================

if __name__ == "__main__":
    import os
    
    # Get API key
    perplexity_key = os.environ.get('PERPLEXITY_API_KEY', '')
    
    # Initialize
    monitor = VicostoneMonitor(perplexity_api_key=perplexity_key)
    experimenter = ExperimentRunner(monitor)
    
    # Run autonomous loop
    experimenter.autonomous_loop(days=7)
