"""
Vicostone AutoResearch - TRUE AUTONOMOUS RUNNER
Inspired by Karpathy's AutoResearch: https://github.com/karpathy/autoresearch

Nguyên lý:
1. Clone repo (hoặc dùng code hiện tại)
2. Mỗi ngày: thay đổi 1 parameter
3. Commit thay đổi đó
4. Chạy data collection + evaluate
5. Nếu BETTER → giữ thay đổi
   Nếu WORSE → git revert
6. Lặp lại

Chạy: python autonomous_runner.py
"""

import os
import sys
import json
import subprocess
import importlib
from datetime import datetime
from pathlib import Path

# ===========================
# CONFIG
# ===========================

OUTPUT_DIR = "/content/drive/MyDrive/vicostone-autoresearch"
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Parameter search space
PARAM_SEARCH_SPACE = {
    "GEMINI_REQUESTS": {
        "name": "GEMINI_REQUESTS",
        "current": 20,
        "range": [10, 15, 20, 25, 30, 35, 40],
        "step": 5,
        "priority": "high"
    },
    "FORUMS_TO_CHECK": {
        "name": "FORUMS_TO_CHECK", 
        "current": 6,
        "range": [4, 6, 8, 10],
        "step": 2,
        "priority": "medium"
    },
    "MIN_REVIEW_LENGTH": {
        "name": "MIN_REVIEW_LENGTH",
        "current": 20,
        "range": [10, 20, 30, 40],
        "step": 10,
        "priority": "low"
    }
}

# ===========================
# UTILITY FUNCTIONS
# ===========================

def git_commit(message: str):
    """Git commit changes"""
    try:
        subprocess.run(["git", "add", "-A"], cwd=OUTPUT_DIR, check=True, capture_output=True)
        result = subprocess.run(["git", "commit", "-m", message], cwd=OUTPUT_DIR, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git commit: {message}")
            return True
        else:
            print(f"⚠️ Git commit failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠️ Git error: {e}")
        return False

def git_push():
    """Git push to remote"""
    try:
        result = subprocess.run(["git", "push", "origin", "master"], cwd=OUTPUT_DIR, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git push successful")
            return True
        else:
            print(f"⚠️ Git push failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠️ Git push error: {e}")
        return False

def git_revert():
    """Revert last commit"""
    try:
        subprocess.run(["git", "rev-parse", "HEAD~1"], cwd=OUTPUT_DIR, check=True, capture_output=True)
        result = subprocess.run(["git", "reset", "--hard", "HEAD~1"], cwd=OUTPUT_DIR, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Reverted last commit")
            return True
    except:
        print("⚠️ Could not revert")
        return False

def update_config(param_name: str, new_value: int):
    """Update parameter in config file"""
    config_file = Path(OUTPUT_DIR) / "vicostone_monitor.py"
    
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Update the parameter value
    old_line = f'{param_name} = {PARAM_SEARCH_SPACE[param_name]["current"]}'
    new_line = f'{param_name} = {new_value}'
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        PARAM_SEARCH_SPACE[param_name]["current"] = new_value
        
        with open(config_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {param_name}: {old_line.split('=')[1].strip()} → {new_value}")
        return True
    
    return False

def log_to_file(message: str):
    """Log to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    
    log_file = Path(OUTPUT_DIR) / "memory" / "vicostone-sentiment" / "autonomous_log.txt"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_file, 'a') as f:
        f.write(log_line + "\n")

# ===========================
# AUTONOMOUS LOOP
# ===========================

class AutonomousRunner:
    """
    TRUE AUTONOMOUS RUNNER
    Mỗi vòng lặp:
    1. Chọn parameter tiếp theo
    2. Thay đổi giá trị
    3. Commit
    4. Chạy experiment
    5. Evaluate
    6. Keep hoặc Revert
    """
    
    def __init__(self):
        self.day = 0
        self.baseline_score = None
        self.current_param_idx = 0
        self.param_names = list(PARAM_SEARCH_SPACE.keys())
        self.experiment_count = 0
        
        # Setup paths - VERIFY BEFORE CHANGING
        if not Path(OUTPUT_DIR).exists():
            raise FileNotFoundError(f"❌ OUTPUT_DIR does not exist: {OUTPUT_DIR}\n"
                                    f"   Please mount Google Drive first or check path.")
        
        # Verify we're in the right place
        log_to_file(f"📁 Working directory: {OUTPUT_DIR}")
        log_to_file(f"📁 Contents: {os.listdir(OUTPUT_DIR)[:5]}...")
        
        os.chdir(OUTPUT_DIR)
        sys.path.insert(0, OUTPUT_DIR)
        
        log_to_file("=" * 60)
        log_to_file("VICOSTONE AUTONOMOUS AUTORESEARCH")
        log_to_file("=" * 60)
    
    def get_next_parameter(self) -> tuple:
        """Get next parameter to experiment"""
        param_name = self.param_names[self.current_param_idx % len(self.param_names)]
        param_info = PARAM_SEARCH_SPACE[param_name]
        
        current_val = param_info["current"]
        range_vals = param_info["range"]
        
        # Find next value in range
        if current_val not in range_vals:
            next_idx = 0
        else:
            current_idx = range_vals.index(current_val)
            next_idx = (current_idx + 1) % len(range_vals)
        
        next_val = range_vals[next_idx]
        
        self.current_param_idx += 1
        
        return param_name, current_val, next_val
    
    def run_experiment_day(self) -> float:
        """Run one experiment day"""
        log_to_file(f"\n--- Day {self.day} Experiment ---")
        
        # Import modules fresh
        if 'vicostone_monitor' in sys.modules:
            del sys.modules['vicostone_monitor']
        if 'data_collector' in sys.modules:
            del sys.modules['data_collector']
        
        import vicostone_monitor
        importlib.reload(vicostone_monitor)
        
        from vicostone_monitor import VicostoneExperiment
        
        # Run experiment
        exp = VicostoneExperiment(
            gemini_api_key=GEMINI_API_KEY,
            output_dir=OUTPUT_DIR
        )
        
        score = exp.run_baseline()
        
        log_to_file(f"Day {self.day} Score: {score:.4f}")
        
        return score
    
    def evaluate_and_decide(self, experiment_score: float, baseline_score: float) -> bool:
        """
        Decide if experiment is better than baseline
        Returns: True if improved, False if worse
        """
        improvement_threshold = 0.01  # 1% minimum
        
        change_pct = (experiment_score - baseline_score) / baseline_score if baseline_score > 0 else 0
        
        log_to_file(f"\n📊 EVALUATION:")
        log_to_file(f"   Baseline:  {baseline_score:.4f}")
        log_to_file(f"   Experiment: {experiment_score:.4f}")
        log_to_file(f"   Change: {change_pct*100:+.2f}%")
        
        improved = experiment_score > baseline_score * (1 + improvement_threshold)
        
        if improved:
            log_to_file("   Result: ✅ IMPROVED - Keeping change")
        else:
            log_to_file("   Result: ❌ NOT IMPROVED - Will revert")
        
        return improved
    
    def run_autonomous_loop(self, num_days: int = 7):
        """
        MAIN AUTONOMOUS LOOP
        Chạy N ngày tự động
        """
        log_to_file(f"\n🚀 STARTING AUTONOMOUS LOOP: {num_days} days")
        log_to_file(f"Parameters: {self.param_names}")
        
        # Step 1: Run baseline
        log_to_file("\n" + "=" * 40)
        log_to_file("PHASE 1: BASELINE")
        log_to_file("=" * 40)
        
        self.day = 0
        self.baseline_score = self.run_experiment_day()
        log_to_file(f"✅ Baseline Score: {self.baseline_score:.4f}")
        
        # Save baseline as starting point
        best_score = self.baseline_score
        best_commit = self.get_git_commit_hash()
        
        # Step 2: Autonomous experiments
        log_to_file("\n" + "=" * 40)
        log_to_file("PHASE 2: AUTONOMOUS EXPERIMENTS")
        log_to_file("=" * 40)
        
        for day in range(1, num_days + 1):
            self.day = day
            
            # Get next parameter to change
            param_name, old_val, new_val = self.get_next_parameter()
            
            log_to_file(f"\n{'='*40}")
            log_to_file(f"DAY {day}/{num_days}: Testing {param_name}")
            log_to_file(f"{'='*40}")
            
            # Update parameter
            log_to_file(f"Changing {param_name}: {old_val} → {new_val}")
            update_config(param_name, new_val)
            
            # Commit this change
            commit_msg = f"autonomous: day{day} {param_name} {old_val}→{new_val}"
            git_commit(commit_msg)
            
            # Run experiment
            experiment_score = self.run_experiment_day()
            
            # Evaluate
            improved = self.evaluate_and_decide(experiment_score, best_score)
            
            if improved:
                # Keep this change
                log_to_file(f"✅ Keeping change - New best: {experiment_score:.4f}")
                best_score = experiment_score
                best_commit = self.get_git_commit_hash()
                
                # Push to remote
                git_push()
            else:
                # Revert this change
                log_to_file(f"❌ Reverting change...")
                git_revert()
                update_config(param_name, old_val)  # Ensure config is correct
                log_to_file(f"Reverted to {old_val}")
            
            self.experiment_count += 1
            
            # Checkpoint
            log_to_file(f"\n📁 Checkpoint: Day {day} complete")
            log_to_file(f"   Best score so far: {best_score:.4f}")
            log_to_file(f"   Experiments run: {self.experiment_count}")
        
        # Final summary
        log_to_file("\n" + "=" * 60)
        log_to_file("AUTONOMOUS LOOP COMPLETE")
        log_to_file("=" * 60)
        log_to_file(f"Total days: {num_days}")
        log_to_file(f"Total experiments: {self.experiment_count}")
        log_to_file(f"Final best score: {best_score:.4f}")
        log_to_file(f"Best commit: {best_commit}")
        log_to_file("\n🎉 AutoResearch complete! Check logs for details.")
        
        return best_score
    
    def get_git_commit_hash(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=OUTPUT_DIR,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()[:8]
        except:
            return "unknown"


# ===========================
# MAIN
# ===========================

def verify_environment():
    """Verify environment before running"""
    print("\n🔍 VERIFYING ENVIRONMENT...")
    
    # Check OUTPUT_DIR
    if not Path(OUTPUT_DIR).exists():
        print(f"❌ ERROR: OUTPUT_DIR does not exist: {OUTPUT_DIR}")
        print("   Run this FIRST to mount Google Drive:")
        print("   >>> from google.colab import drive")
        print("   >>> drive.mount('/content/drive')")
        return False
    
    print(f"✅ OUTPUT_DIR exists: {OUTPUT_DIR}")
    
    # Check if it's a git repo
    if not Path(OUTPUT_DIR, '.git').exists():
        print(f"⚠️ WARNING: {OUTPUT_DIR} is not a git repo - git operations will fail")
    else:
        print(f"✅ Git repo verified")
    
    # Check Python path
    if Path(OUTPUT_DIR, 'vicostone_monitor.py').exists():
        print(f"✅ vicostone_monitor.py found")
    else:
        print(f"❌ WARNING: vicostone_monitor.py not found in {OUTPUT_DIR}")
    
    print("\n" + "=" * 50)
    return True


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║     VICOSTONE AUTONOMOUS AUTORESEARCH                       ║
║     Inspired by Karpathy's AutoResearch                     ║
║                                                              ║
║     Starting autonomous loop...                              ║
║     Press Ctrl+C to stop                                    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Verify environment FIRST
    if not verify_environment():
        print("\n❌ Environment verification failed. Fix errors above and try again.")
        exit(1)
    
    runner = AutonomousRunner()
    
    try:
        # Run for 7 days of experiments
        final_score = runner.run_autonomous_loop(num_days=7)
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║     AUTONOMOUS RUN COMPLETE                                  ║
║     Final Best Score: {final_score:.4f}                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        print("AutoResearch paused. Resume by running again.")
