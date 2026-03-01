#!/usr/bin/env python3
import re

with open('meta_evolver_fixed.py', 'r') as f:
    content = f.read()

# Fix the ArchitectureEvolver __init__ method
content = re.sub(
    r'def __init__\(self, None, rules\):',
    'def __init__(self, check_evolution_fn, rules):',
    content
)

# Also fix any other None parameters
content = re.sub(
    r'def __init__\(self, None, None\):',
    'def __init__(self, check_evolution_fn, measure_drift_fn):',
    content
)

# Write the final fixed version
with open('meta_evolver_final.py', 'w') as f:
    f.write(content)

print("✅ Fixed ArchitectureEvolver __init__")
