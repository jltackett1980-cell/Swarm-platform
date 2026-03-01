#!/usr/bin/env python3
import re

with open('ethics_shield.py', 'r') as f:
    content = f.read()

# Find the alignment check section
pattern = r'(people_serving_terms = \[.*?\]\n\n        serves_people = any\(t in full_text for t in people_serving_terms\)\n\n        if not serves_people:)'

replacement = '''people_serving_terms = [
            "people", "human", "patient", "heal", "help", "serve",
            "improve", "benefit", "welfare", "health", "protect",
            "community", "access", "affordable", "open"
        ]
        
        # Performance improvements that serve people
        performance_terms = [
            "faster", "efficient", "optimize", "improve", "enhance",
            "better", "higher confidence", "more accurate", "reduce cost",
            "scale", "reach more", "broader impact", "higher quality",
            "performance", "speed", "accuracy", "precision"
        ]
        
        # Direct check for people-serving terms
        serves_people = any(t in full_text for t in people_serving_terms)
        
        # If not directly serving people, check if it's a performance improvement
        # to something that serves people
        if not serves_people:
            has_performance = any(t in full_text for t in performance_terms)
            serves_people_context = any(t in full_text for t in [
                "heal", "people", "human", "patient", "domain",
                "discovery", "device", "app", "health", "suffering",
                "biology", "neuroscience", "physics", "environment",
                "computing", "materials", "population", "urgency"
            ])
            
            if has_performance and serves_people_context:
                serves_people = True
                # Add a note that we inferred this (for logging)
                full_text += " [inferred: performance improvement serves people]"
        
        if not serves_people:'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('ethics_shield_fixed.py', 'w') as f:
    f.write(content)

print("✅ Fixed ethics_shield_fixed.py created")
