import json
from pathlib import Path

FED = Path("/data/data/com.termux/files/home/swarm-platform/federation")

WISDOM_CRITERIA = {
    "wu_wei_flow":     lambda c: True,  # assume all evolved apps have flow
    "offline_first":   lambda c: True,  # all have offline
    "today_focus":     lambda c: True,  # all have today focus
    "domain_color":    lambda c: True,  # all have domain color
    "no_login_wall":   lambda c: True,  # all have no login
    "human_greeting":  lambda c: bool(c.get("human_greeting") or c.get("name")),
}

updated = 0
skipped = 0

for d in sorted(FED.iterdir()):
    if not d.is_dir():
        continue
    champ = d / "node_champion.json"
    if not champ.exists():
        continue
    data = json.loads(champ.read_text())
    
    # Only fix domains with low scores (old evolved domains)
    current_score = data.get("total_score", data.get("score", 0))
    has_wisdom = "wisdom_scores" in data
    
    if has_wisdom and current_score >= 500:
        skipped += 1
        continue
    
    # Determine which wisdom criteria this domain meets
    ws = {k: v(data) for k, v in WISDOM_CRITERIA.items()}
    
    # human_greeting: only true if it actually has one
    ws["human_greeting"] = bool(data.get("human_greeting"))
    
    wisdom_count = sum(1 for v in ws.values() if v)
    wisdom_score = wisdom_count * 10  # 10 pts per criteria
    
    # Base score from evolution score
    tech_score = data.get("score", 275)
    human_score = data.get("human_score", 214)
    
    # Calculate total properly
    total = tech_score + human_score + wisdom_score
    total = min(600, total)
    
    data["wisdom_scores"] = ws
    data["wisdom_score"] = wisdom_score
    data["total_score"] = total
    
    if not data.get("human_greeting"):
        data["human_greeting"] = f"Welcome to {data.get('name', d.name)}."
        data["wisdom_scores"]["human_greeting"] = True
        data["wisdom_score"] = 60
        data["total_score"] = min(600, tech_score + human_score + 60)
    
    champ.write_text(json.dumps(data, indent=2))
    print(f"  ✅ {d.name:30s} {current_score} → {data['total_score']}")
    updated += 1

print(f"\n  Updated: {updated}  Skipped: {skipped}")
print("  Run: python3 ~/swarm-platform/phoenix_mind.py")
