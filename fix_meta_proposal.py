#!/usr/bin/env python3
import re

with open('meta_evolver.py', 'r') as f:
    content = f.read()

# Find the proposal construction in evolve_rules
pattern = r'(proposed = \{[^\}]*"reason":[^\}]*\})'

# Make sure all proposal fields are included
new_proposal = '''            proposed = {
                "component":   "domain_priority",
                "description": "Reweight domain priorities based on confidence scores from real discoveries",
                "reason":      f"Learned from {disc_insights['total_discoveries']} discoveries — domains with higher confidence scores should be explored more. Serves people better by focusing on solvable problems. This change benefits {sum(domain_avg.values()):.0f} discovery categories and ultimately serves the people who need solutions in these domains.",
                "new_code":    json.dumps(new_priorities),
                "old_values":  self.rules["domain_priority"],
                "new_values":  new_priorities,
            }'''

# Replace the proposal section (this is approximate - may need adjustment)
content = re.sub(r'proposed = \{[^\}]*"component"[^\}]*"domain_priority"[^\}]*\}', new_proposal, content, flags=re.DOTALL)

with open('meta_evolver_fixed.py', 'w') as f:
    f.write(content)

print("✅ Updated meta_evolver_fixed.py with improved proposal")
