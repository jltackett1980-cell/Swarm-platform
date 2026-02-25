#!/usr/bin/env python3
"""
Safe analysis of evolution logs
"""

import json
import glob
import os
import time
from datetime import datetime

def safe_load_json(filename):
    """Safely load JSON file, handling incomplete writes"""
    try:
        with open(filename, 'r') as f:
            content = f.read()
            # Try to find complete JSON array
            if content.strip().endswith(']'):
                return json.loads(content)
            else:
                # File might be incomplete, try to parse what we can
                print(f"⚠️ {filename} appears incomplete, attempting partial parse...")
                # Find the last complete entry
                last_complete = content.rfind('},') + 1
                if last_complete > 0:
                    partial_content = content[:last_complete] + ']'
                    return json.loads(partial_content)
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return None

# Find all evolution logs
log_files = glob.glob('evolution_log_*.json')
print(f"📊 Found {len(log_files)} evolution log files\n")

all_scores = []
best_overall = 0
best_log = None

for log_file in sorted(log_files):
    data = safe_load_json(log_file)
    if not data:
        continue
    
    # Extract scores
    scores = [entry.get('score', 0) for entry in data if 'score' in entry]
    if not scores:
        continue
    
    max_score = max(scores)
    all_scores.append(max_score)
    
    if max_score > best_overall:
        best_overall = max_score
        best_log = log_file
    
    # Get final parameters
    last_entry = data[-1] if data else {}
    
    print(f"\n📁 {log_file}")
    print(f"  Generations: {len(scores)}")
    print(f"  Start: {scores[0]:.2f} → End: {scores[-1]:.2f}")
    print(f"  Best: {max_score:.2f}")
    print(f"  Improvement: {max_score - scores[0]:.2f}")
    print(f"  Final params: μ={last_entry.get('mutation_rate', 0):.3f}, "
          f"τ={last_entry.get('tournament_size', 0)}, "
          f"χ={last_entry.get('crossover_rate', 0):.2f}")
    
    # Count recovery strategies
    recoveries = [e for e in data if 'action' in e and 'recovery' in e['action']]
    if recoveries:
        print(f"  Recovery attempts: {len(recoveries)}")
        # Show unique strategies
        strategies = {}
        for r in recoveries:
            strat = r['action']
            strategies[strat] = strategies.get(strat, 0) + 1
        print(f"  Strategies: {', '.join([f'{k}: {v}' for k, v in strategies.items()])}")

print(f"\n{'='*50}")
print(f"🏆 BEST OVERALL SCORE: {best_overall:.2f} in {best_log}")
print(f"{'='*50}")

# Find latest checkpoint
checkpoints = glob.glob('checkpoint_gen_*.json')
if checkpoints:
    latest_checkpoint = max(checkpoints, key=lambda x: int(x.split('_')[-1].split('.')[0]))
    print(f"\n💾 Latest checkpoint: {latest_checkpoint}")
    try:
        with open(latest_checkpoint, 'r') as f:
            cp = json.load(f)
        print(f"   Generation: {cp.get('generation', 'unknown')}")
        print(f"   Best score: {cp.get('best_score', 0):.2f}")
        print(f"   Parameters: μ={cp.get('mutation_rate', 0):.3f}, "
              f"τ={cp.get('tournament_size', 0)}")
    except:
        pass

# Show progress trend
if len(all_scores) > 1:
    print(f"\n📈 Progress over runs:")
    for i, score in enumerate(all_scores):
        print(f"  Run {i+1}: {score:.2f}")
    print(f"  Overall improvement: {all_scores[-1] - all_scores[0]:.2f}")
