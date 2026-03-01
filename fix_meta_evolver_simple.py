#!/usr/bin/env python3
import re

with open('meta_evolver.py', 'r') as f:
    content = f.read()

# Find the __init__ method and fix it
content = content.replace('def __init__(self, None, None):', 'def __init__(self, check_evolution_fn, measure_drift_fn):')

# Fix the load_constitution function
old_load = '''def load_constitution():
    """Load and validate the constitutional core."""
    import sys
    sys.path.insert(0, str(SWARM))
    try:
        from constitutional_core import boot_check, check_evolution, measure_drift
        if not boot_check("Phoenix Meta-Evolver"):
            print("Constitutional validation failed. Cannot evolve.")
            sys.exit(1)
        return check_evolution, measure_drift, CHARTER_HASH
    except ImportError:
        print("⚠️  Constitutional core not found. Running in safe mode.")
        # Safe mode — always approve but log warning
        def safe_check(change):
            return True, "SAFE MODE — constitutional core not loaded"
        def safe_drift(outputs):
            return 0.0, "SAFE MODE — drift monitoring disabled"
        return safe_check, safe_drift, "SAFE_MODE"'''

new_load = '''def load_constitution():
    """Load and validate the constitutional core."""
    import sys
    sys.path.insert(0, str(SWARM))
    try:
        from constitutional_core import boot_check, RealignmentEngine, CHARTER_HASH
        if not boot_check("Phoenix Meta-Evolver"):
            print("Constitutional validation failed. Cannot evolve.")
            sys.exit(1)
        engine = RealignmentEngine()
        return engine.check_proposed_change, engine.measure_drift, CHARTER_HASH
    except ImportError as e:
        print(f"⚠️  Constitutional core import error: {e}")
        print("Running in safe mode.")
        def safe_check(change):
            return True, "SAFE MODE — constitutional core not loaded"
        def safe_drift(outputs):
            return 0.0, "SAFE MODE — drift monitoring disabled"
        return safe_check, safe_drift, "SAFE_MODE"'''

content = content.replace(old_load, new_load)

with open('meta_evolver_fixed.py', 'w') as f:
    f.write(content)

print("✅ Fixed meta_evolver_fixed.py created")
