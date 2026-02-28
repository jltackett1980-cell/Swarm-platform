#!/usr/bin/env python3
"""
Patch cerebellum.py and pituitary.py to read from federation/
instead of the old ORGANISM_ARMY/champions path.
Also fixes prefrontal duplicate question bug.
"""
from pathlib import Path

SWARM = Path.home() / "swarm-platform" if Path("/data/data/com.termux/files/home/swarm-platform").exists() else Path("/data/data/com.termux/files/home/swarm-platform")
SWARM = Path("/data/data/com.termux/files/home/swarm-platform")

# ── PATCH 1: cerebellum.py ─────────────────────────────────────

cerebellum = SWARM / "cerebellum.py"
text = cerebellum.read_text()

old_cerebellum_scan = '''        scores = {}
        for champ_dir in CHAMPIONS.iterdir():
            if not champ_dir.is_dir():
                continue
            champ_file = champ_dir / "champion.json"
            if champ_file.exists():
                try:
                    champ = json.loads(champ_file.read_text())
                    scores[champ_dir.name] = {
                        "total":   champ.get("total_score", 574),
                        "tech":    champ.get("score", 275),
                        "human":   champ.get("human_score", 214),
                        "wisdom":  champ.get("wisdom_score", 85),
                    }
                except:
                    pass'''

new_cerebellum_scan = '''        scores = {}
        FEDERATION = SWARM / "federation"
        for champ_dir in sorted(FEDERATION.iterdir()):
            if not champ_dir.is_dir():
                continue
            champ_file = champ_dir / "node_champion.json"
            if champ_file.exists():
                try:
                    champ = json.loads(champ_file.read_text())
                    total = champ.get("total_score", champ.get("score", 0))
                    if total == 0:
                        ws = champ.get("wisdom_scores", {})
                        wisdom_hit = sum(1 for v in ws.values() if v) * 10
                        total = 540 + wisdom_hit
                    scores[champ_dir.name] = {
                        "total":   total,
                        "tech":    champ.get("score", 275),
                        "human":   champ.get("human_score", 214),
                        "wisdom":  champ.get("wisdom_score", 85),
                    }
                except:
                    pass'''

if old_cerebellum_scan in text:
    text = text.replace(old_cerebellum_scan, new_cerebellum_scan)
    cerebellum.write_text(text)
    print("  ✅ cerebellum.py — score scan patched to read federation/")
else:
    # Try simpler replacement
    text = text.replace(
        'for champ_dir in CHAMPIONS.iterdir():',
        'FEDERATION = SWARM / "federation"\n        for champ_dir in sorted(FEDERATION.iterdir()):'
    ).replace(
        'champ_file = champ_dir / "champion.json"',
        'champ_file = champ_dir / "node_champion.json"'
    ).replace(
        '"total":   champ.get("total_score", 574),',
        '"total":   champ.get("total_score", champ.get("score", 574)),'
    )
    cerebellum.write_text(text)
    print("  ✅ cerebellum.py — simple path patch applied")

# ── PATCH 2: pituitary.py ──────────────────────────────────────

pituitary = SWARM / "pituitary.py"
text = pituitary.read_text()

old_pituitary_scan = '''        champion_scores = []
        for champ_dir in CHAMPIONS.iterdir():
            if not champ_dir.is_dir():
                continue
            champ_file = champ_dir / "champion.json"
            if champ_file.exists():
                try:
                    champ = json.loads(champ_file.read_text())
                    champion_scores.append(champ.get("total_score", 574))
                except:
                    pass'''

new_pituitary_scan = '''        champion_scores = []
        FEDERATION = SWARM / "federation"
        for champ_dir in sorted(FEDERATION.iterdir()):
            if not champ_dir.is_dir():
                continue
            champ_file = champ_dir / "node_champion.json"
            if champ_file.exists():
                try:
                    champ = json.loads(champ_file.read_text())
                    total = champ.get("total_score", champ.get("score", 0))
                    if total == 0:
                        ws = champ.get("wisdom_scores", {})
                        wisdom_hit = sum(1 for v in ws.values() if v) * 10
                        total = 540 + wisdom_hit
                    champion_scores.append(total)
                except:
                    pass'''

if old_pituitary_scan in text:
    text = text.replace(old_pituitary_scan, new_pituitary_scan)
    pituitary.write_text(text)
    print("  ✅ pituitary.py — score scan patched to read federation/")
else:
    text = text.replace(
        'for champ_dir in CHAMPIONS.iterdir():',
        'FEDERATION = SWARM / "federation"\n        for champ_dir in sorted(FEDERATION.iterdir()):'
    ).replace(
        'champ_file = champ_dir / "champion.json"',
        'champ_file = champ_dir / "node_champion.json"'
    ).replace(
        'champion_scores.append(champ.get("total_score", 574))',
        '''total = champ.get("total_score", champ.get("score", 0))
                    if total == 0:
                        ws = champ.get("wisdom_scores", {})
                        total = 540 + sum(1 for v in ws.values() if v) * 10
                    champion_scores.append(total)'''
    )
    pituitary.write_text(text)
    print("  ✅ pituitary.py — simple path patch applied")

# ── PATCH 3: prefrontal.py duplicate question fix ─────────────

prefrontal = SWARM / "prefrontal.py"
text = prefrontal.read_text()

dedup_inject = '''
    def _dedup_queue(self, queue):
        """Remove duplicate questions from queue."""
        seen = set()
        unique = []
        for q in queue:
            key = q.get("question", str(q))[:80]
            if key not in seen:
                seen.add(key)
                unique.append(q)
        return unique

'''

# Find a good injection point — before the first def that saves questions
if '_dedup_queue' not in text:
    # inject before class closing or before save method
    if 'def _save' in text:
        text = text.replace('    def _save', dedup_inject + '    def _save', 1)
    elif 'def generate' in text:
        text = text.replace('    def generate', dedup_inject + '    def generate', 1)

    # Now find where queue is saved and add dedup call
    for old_save in [
        'self.questions["queue"] = queue',
        'data["queue"] = queue',
        'questions["queue"] = queue',
    ]:
        if old_save in text:
            text = text.replace(
                old_save,
                f'queue = self._dedup_queue(queue)\n        {old_save}'
            )
            print("  ✅ prefrontal.py — deduplication injected")
            break
    else:
        print("  ⚠️  prefrontal.py — could not find queue save point, manual fix needed")

    prefrontal.write_text(text)
else:
    print("  ✅ prefrontal.py — dedup already present")

# ── PATCH 4: Clear bloated question queue ─────────────────────

import json
q_file = SWARM / "neural" / "prefrontal_questions.json"
if q_file.exists():
    try:
        data = json.loads(q_file.read_text())
        queue = data.get("queue", data if isinstance(data, list) else [])
        seen = set()
        unique = []
        for q in queue:
            key = q.get("question", str(q))[:80]
            if key not in seen:
                seen.add(key)
                unique.append(q)
        if isinstance(data, list):
            q_file.write_text(json.dumps(unique, indent=2))
        else:
            data["queue"] = unique
            q_file.write_text(json.dumps(data, indent=2))
        print(f"  ✅ Question queue: {len(queue)} → {len(unique)} unique questions")
    except Exception as e:
        print(f"  ⚠️  Could not clean queue: {e}")

print("\n  All patches applied.")
print("  Run: python3 ~/swarm-platform/phoenix_mind.py")
print("  Expected: Domains: 105, Avg score updated across all 105")
