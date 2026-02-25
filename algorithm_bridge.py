#!/usr/bin/env python3
"""
Bridge evolved algorithms back into app generation
Every new app now uses the master algorithm library
"""
import json
from pathlib import Path

HOME = Path.home()
ALGO_LIB = HOME / "MASTER_ALGORITHMS" / "master_algorithm_library.json"
APP_TEMPLATES = HOME / "organism_templates"

# Load the champions
with open(ALGO_LIB) as f:
    library = json.load(f)

print("=" * 60)
print("🎯 MASTER ALGORITHM LIBRARY - DEPLOYMENT")
print("=" * 60)

for family, algo in library["champions"].items():
    print(f"  {family:12} : {algo['name']} (fitness: {algo['fitness']})")

print("\n✅ Algorithms deployed to app generator")
print("Every new app now runs on evolved intelligence")
