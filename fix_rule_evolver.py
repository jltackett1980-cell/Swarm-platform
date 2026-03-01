#!/usr/bin/env python3
import re

with open('meta_evolver.py', 'r') as f:
    content = f.read()

# Fix RuleEvolver __init__ to properly store the check function
content = re.sub(
    r'def __init__\(self, check_evolution_fn, measure_drift_fn\):',
    'def __init__(self, check_evolution_fn, measure_drift_fn):\n        self.check = check_evolution_fn\n        self.drift = measure_drift_fn\n        self.history = []\n        self.rules = self._load_rules()',
    content
)

# Also fix ArchitectureEvolver __init__
content = re.sub(
    r'def __init__\(self, check_evolution_fn, rules\):',
    'def __init__(self, check_evolution_fn, rules):\n        self.check = check_evolution_fn\n        self.rules = rules\n        self.arch = self._load_architecture()',
    content
)

# Write the final fixed version
with open('meta_evolver_final.py', 'w') as f:
    f.write(content)

print("✅ Fixed RuleEvolver __init__ to store check function")
