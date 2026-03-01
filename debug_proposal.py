#!/usr/bin/env python3
from meta_evolver import RuleEvolver
from constitutional_core import RealignmentEngine
import json

# Load the current rules
import json
from pathlib import Path

META = Path("/data/data/com.termux/files/home/swarm-platform/meta_evolution")
rules_path = META / "evolved_rules.json"
if rules_path.exists():
    rules = json.loads(rules_path.read_text())
    
    # Reconstruct what the proposal would look like
    domain_avg = {
        "physics": 1.004,
        "neuroscience": 1.003,
        "environment": 1.001,
        "computing": 0.999,
        "biology": 0.997,
        "materials": 0.997
    }
    total = sum(domain_avg.values())
    new_priorities = {k: round(v / total * len(domain_avg), 3) for k, v in domain_avg.items()}
    
    proposed = {
        "component": "domain_priority",
        "description": "Reweight domain priorities based on confidence scores from real discoveries",
        "reason": "Learned from 11,101 discoveries — domains with higher confidence scores should be explored more. Serves people better by focusing on solvable problems.",
        "new_code": json.dumps(new_priorities),
        "old_values": rules["domain_priority"],
        "new_values": new_priorities,
    }
    
    # Test it with the ethics shield directly
    engine = RealignmentEngine()
    approved, reason = engine.check_proposed_change(proposed)
    print(f"\n{'═'*60}")
    print(f"TESTING PROPOSAL DIRECTLY")
    print(f"{'═'*60}")
    print(f"Description: {proposed['description']}")
    print(f"Reason: {proposed['reason']}")
    print(f"\nResult: {'✅ APPROVED' if approved else '🚫 REJECTED'}")
    print(f"Reason: {reason}")
    print(f"{'═'*60}\n")
