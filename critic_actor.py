#!/usr/bin/env python3
"""
Critic/Actor architecture for self-improvement [citation:2]
"""
import subprocess
import time

print("🎭 CRITIC/ACTOR ARCHITECTURE")

# Actor generates improvements
subprocess.run("python3 device_forge.py --cycles 50 > /dev/null 2>&1", shell=True)

# Critic evaluates and provides feedback
subprocess.run("python3 meta_evolver.py > /dev/null 2>&1", shell=True)

# Loop with self-reflection
for i in range(5):
    print(f"Self-reflection cycle {i+1}/5")
    time.sleep(2)
