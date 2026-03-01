#!/usr/bin/env python3
import re

with open('meta_evolver.py', 'r') as f:
    lines = f.readlines()

# Find and fix the RuleEvolver __init__
in_init = False
init_lines = []
init_start = None
init_end = None

for i, line in enumerate(lines):
    if 'def __init__(self, check_evolution_fn, measure_drift_fn):' in line:
        in_init = True
        init_start = i
        init_lines = [line.rstrip()]
    elif in_init and line.strip() and not line.startswith(' ' * 8):  # End of method
        init_end = i
        break
    elif in_init:
        init_lines.append(line.rstrip())

if init_start is not None:
    # Replace with proper implementation
    new_init = [
        '    def __init__(self, check_evolution_fn, measure_drift_fn):',
        '        print(f"🔵 INIT: storing check={check_evolution_fn}")',
        '        self.check = check_evolution_fn',
        '        self.drift = measure_drift_fn',
        '        self.history = []',
        '        self.rules = self._load_rules()',
        ''
    ]
    lines[init_start:init_end] = [l + '\n' for l in new_init]

# Fix the _load_rules method
in_load = False
load_start = None
load_end = None

for i, line in enumerate(lines):
    if 'def _load_rules(self):' in line:
        in_load = True
        load_start = i
    elif in_load and line.strip() and line[0] != ' ':
        load_end = i
        break

if load_start is not None:
    new_load = [
        '    def _load_rules(self):',
        '        print("🟡 _load_rules called")',
        '        print(f"🟡 self.check still = {getattr(self, \"check\", None)}")',
        '        rules_path = META / "evolved_rules.json"',
        '        if rules_path.exists():',
        '            try:',
        '                return json.loads(rules_path.read_text())',
        '            except:',
        '                pass',
        '        return self._default_rules()',
        ''
    ]
    lines[load_start:load_end] = [l + '\n' for l in new_load]

# Fix the evolve_rules method where the error occurred
in_evolve = False
evolve_start = None
evolve_end = None
pattern_line = None

for i, line in enumerate(lines):
    if 'approved, reason = self.check(proposed)' in line:
        pattern_line = i
    elif 'if approved:' in line and pattern_line and i > pattern_line:
        # Insert debug before this line
        lines.insert(i, '        print(f"🔴 About to call self.check: {self.check}")\n')
        break

# Write the fixed file
with open('meta_evolver_fixed.py', 'w') as f:
    f.writelines(lines)

print("✅ Fixed meta_evolver_fixed.py created")
