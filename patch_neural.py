import json, os, glob
from pathlib import Path

base = Path.home() / "swarm-platform"
neural = base / "neural"
fed = base / "federation"

# ── FIX 1: Rebuild organism_state with actual domain count ──
domains = [d.name for d in fed.iterdir() if d.is_dir() and (d / "node_champion.json").exists()]
print(f"  Actual domains found: {len(domains)}")

state_file = neural / "organism_state.json"
if state_file.exists():
    state = json.loads(state_file.read_text())
else:
    state = {}

state["domain_count"] = len(domains)
state["domains"] = domains
state_file.write_text(json.dumps(state, indent=2))
print(f"  organism_state.json updated: {len(domains)} domains")

# ── FIX 2: Deduplicate prefrontal question queue ──
q_file = neural / "prefrontal_questions.json"
if q_file.exists():
    data = json.loads(q_file.read_text())
    questions = data if isinstance(data, list) else data.get("questions", [])
    seen = set()
    unique = []
    for q in questions:
        key = q.get("question", str(q))[:80]
        if key not in seen:
            seen.add(key)
            unique.append(q)
    if isinstance(data, list):
        q_file.write_text(json.dumps(unique, indent=2))
    else:
        data["questions"] = unique
        q_file.write_text(json.dumps(data, indent=2))
    print(f"  Questions: {len(questions)} → {len(unique)} (removed {len(questions)-len(unique)} duplicates)")

# ── FIX 3: Mark domestic_violence_shelter as built ──
dvs = fed / "domestic_violence_shelter"
if dvs.exists():
    champ = dvs / "node_champion.json"
    if champ.exists():
        c = json.loads(champ.read_text())
        c["built"] = True
        c["status"] = "active"
        champ.write_text(json.dumps(c, indent=2))
        print(f"  domestic_violence_shelter marked as built")

# ── FIX 4: Write unbuilt_domains based on actual filesystem ──
all_108 = [d.name for d in fed.iterdir() if d.is_dir()]
pituitary = neural / "pituitary_directive.json"
if pituitary.exists():
    p = json.loads(pituitary.read_text())
    p["current_domains"] = len(domains)
    p["target_domains"] = 108
    p["unbuilt_count"] = max(0, 108 - len(domains))
    pituitary.write_text(json.dumps(p, indent=2))
    print(f"  pituitary_directive.json updated: {len(domains)}/108 domains")

print(f"\n  Patch complete. Run phoenix_mind.py to verify.")
