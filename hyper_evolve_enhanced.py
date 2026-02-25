#!/usr/bin/env python3
"""
Hyper-evolution with adaptive parameters and stagnation recovery
"""

import subprocess
import time
import json
import os
import re
from datetime import datetime

# Hyper-parameters
GENERATIONS = 50000
POPULATION = 500
INITIAL_MUTATION = 0.5
INITIAL_TOURNAMENT = 15
ISLANDS = 8

print(f"🚀 Starting HYPER-EVOLUTION with ADAPTIVE PARAMETERS")
print(f"   Generations: {GENERATIONS}")
print(f"   Population: {POPULATION} per island ({POPULATION * ISLANDS} total)")
print(f"   Initial mutation: {INITIAL_MUTATION}")
print(f"   Initial tournament: {INITIAL_TOURNAMENT}")
print("")

# Create log directory
log_dir = f"hyper_evolution_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(log_dir, exist_ok=True)

best_score_so_far = 0
stagnation_phases = 0

for phase in range(1, 6):  # 5 phases of 10,000 generations
    print(f"\n📈 PHASE {phase}/5 - Generations {(phase-1)*10000+1}-{phase*10000}")
    
    # Adaptive mutation based on stagnation
    if stagnation_phases > 2:
        mutation = min(0.9, INITIAL_MUTATION * (1 + phase * 0.2 + stagnation_phases * 0.1))
        tournament = max(3, INITIAL_TOURNAMENT - stagnation_phases * 2)
        print(f"⚠️ Stagnation detected! Boosting mutation to {mutation:.2f}, reducing tournament to {tournament}")
    else:
        mutation = INITIAL_MUTATION * (1 + phase * 0.1)
        tournament = INITIAL_TOURNAMENT
    
    cmd = [
        "python3", "turbo_evolve_enhanced_fixed.py",
        "--generations", "10000",
        "--population", str(POPULATION),
        "--mutation-rate", str(mutation),
        "--tournament-size", str(tournament),
        "--crossover-rate", "0.9",
        "--num-islands", str(ISLANDS),
        "--max-score", "430",
        "--print-interval", "50",
        "--verbose"
    ]
    
    log_file = f"{log_dir}/phase_{phase}.log"
    
    cmd_str = " ".join(cmd) + f" > {log_file} 2>&1"
    print(f"   Running phase {phase}...")
    print(f"   Command: python3 turbo_evolve_enhanced_fixed.py --generations 10000 --mutation-rate {mutation:.2f} --tournament-size {tournament}")
    
    start_time = time.time()
    result = subprocess.run(cmd_str, shell=True)
    elapsed = time.time() - start_time
    
    # Check for improvements
    try:
        with open(log_file, 'r') as f:
            log_content = f.read()
            
        # Extract best score from log
        scores = re.findall(r'ALL-TIME:\s+(\d+\.?\d*)', log_content)
        if scores:
            phase_best = max([float(s) for s in scores])
            print(f"   Phase {phase} best score: {phase_best}")
            
            if phase_best > best_score_so_far:
                improvement = phase_best - best_score_so_far
                best_score_so_far = phase_best
                stagnation_phases = 0
                print(f"🎉 IMPROVEMENT! +{improvement:.2f} (new best: {best_score_so_far:.2f})")
                
                # Save breakthrough info
                breakthrough = {
                    'phase': phase,
                    'score': best_score_so_far,
                    'improvement': improvement,
                    'timestamp': datetime.now().isoformat()
                }
                with open(f"{log_dir}/breakthrough_phase{phase}.json", 'w') as f:
                    json.dump(breakthrough, f, indent=2)
            else:
                stagnation_phases += 1
                print(f"   No improvement this phase. Stagnation count: {stagnation_phases}")
    except Exception as e:
        print(f"   Warning: Could not parse log file: {e}")
    
    print(f"   Phase {phase} complete in {elapsed:.1f}s")
    
    # Early breakthrough check
    if best_score_so_far >= 430:
        print(f"\n🎉🎉🎉 TARGET REACHED! Final score: {best_score_so_far}")
        break
    
    time.sleep(2)  # Brief pause between phases

print(f"\n✅ HYPER-EVOLUTION complete!")
print(f"   Best score achieved: {best_score_so_far}")
print(f"   Logs saved in: {log_dir}")
