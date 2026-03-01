#!/usr/bin/env python3
import re

with open('meta_evolver.py', 'r') as f:
    content = f.read()

# Add Phase 3 loading and printing
phase3_print = '''

    # Load and display Phase 3 results (if any)
    arch_path = META / "evolved_architecture.json"
    if arch_path.exists():
        arch = json.loads(arch_path.read_text())
        print(f"  Phase 3 — New domains:   {len(arch.get('new_domains', []))}")
        print(f"  Phase 3 — New components: {len(arch.get('new_brain_components', []))}")
        if arch.get('new_domains'):
            print("  New domains proposed:")
            for d in arch['new_domains']:
                print(f"    • {d['name']} — {d['population']:,} people")
        if arch.get('new_brain_components'):
            print("  New brain components:")
            for c in arch['new_brain_components']:
                print(f"    • {c['name']}")
'''

# Insert after Phase 2 output
content = content.replace(
    '    print(f"  Phase 2 — Rules evolved: v{new_rules.get(\'version\', 1)}")',
    '    print(f"  Phase 2 — Rules evolved: v{new_rules.get(\'version\', 1)}")' + phase3_print
)

with open('meta_evolver_phase3_show.py', 'w') as f:
    f.write(content)

print("✅ Phase 3 display added")
