#!/usr/bin/env python3
import re

with open('turbo_evolve_enhanced.py', 'r') as f:
    content = f.read()

# Fix line 242 — convert deque to list before slicing
old_line = '            avg_div = sum(self.diversity_history[-10:]) / min(10, len(self.diversity_history))'
new_line = '            # Convert deque to list for slicing\n            history_list = list(self.diversity_history)\n            avg_div = sum(history_list[-10:]) / min(10, len(history_list))'

content = content.replace(old_line, new_line)

# Also fix the diversity tracking at line 325 (replace random with real measure later)
old_placeholder = '        diversity = random.uniform(0.05, 0.4)  # Placeholder'
new_placeholder = '        # Calculate actual diversity\n        if len(population) > 1:\n            scores = [ind.get(\'score\', 0) for ind in population if ind]\n            if scores:\n                mean_score = sum(scores) / len(scores)\n                variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)\n                diversity = variance ** 0.5 / 100  # Normalize\n            else:\n                diversity = 0.0\n        else:\n            diversity = 0.0'

content = content.replace(old_placeholder, new_placeholder)

with open('turbo_evolve_fixed.py', 'w') as f:
    f.write(content)

print("✅ Fixed diversity slice error")
print("✅ Added real diversity calculation")
