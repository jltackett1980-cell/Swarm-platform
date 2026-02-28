#!/usr/bin/env python3
"""
Phoenix Forge — Turbo Evolution Patch
Wires HumanScoreEngine into turbo_evolve_enhanced_fixed.py
"""

import os
import sys
import shutil
import re
from pathlib import Path
from datetime import datetime

HOME = Path.home()
SWARM = HOME / "swarm-platform"
TARGET = SWARM / "turbo_evolve_enhanced_fixed.py"
BACKUP = SWARM / f"turbo_evolve_enhanced_fixed.BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"

if not TARGET.exists():
    print(f"❌ Target not found: {TARGET}")
    sys.exit(1)

if not (SWARM / "human_score_engine.py").exists():
    print(f"❌ human_score_engine.py not found in {SWARM}")
    sys.exit(1)

shutil.copy2(TARGET, BACKUP)
print(f"✅ Backup created: {BACKUP.name}")

code = TARGET.read_text()
original_lines = len(code.splitlines())
print(f"📄 Read {TARGET.name} — {original_lines} lines")

HUMAN_IMPORT = '''
# ── Phoenix Forge Patch: Human Scoring ──────────────────────
import sys as _sys
_sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
try:
    from human_score_engine import HumanScoreEngine as _HumanScoreEngine
    _human_engine = _HumanScoreEngine()
    _human_scoring_available = True
    print("✅ HumanScoreEngine loaded — scoring 500pt system active")
except Exception as _e:
    _human_scoring_available = False
    print(f"⚠️  HumanScoreEngine not available: {_e} — using 275pt fallback")

try:
    from pathlib import Path as _Path
    import json as _json
    _domain_configs_path = _Path.home() / "organism_templates" / "domain_configs.json"
    _domain_configs = _json.loads(_domain_configs_path.read_text()) if _domain_configs_path.exists() else {}
except:
    _domain_configs = {}

def _get_human_score(app_path, domain_id):
    """Get human score for an app. Returns (human_score, grade)"""
    if not _human_scoring_available:
        return 0, "N/A"
    try:
        cfg = _domain_configs.get(domain_id, {})
        result = _human_engine.score(_Path(app_path), domain_id, cfg)
        return result["human_score"], result["grade"]
    except Exception as e:
        return 0, "N/A"

CROWN_THRESHOLD = 400
CROWN_THRESHOLD_TECH_ONLY = 250
# ────────────────────────────────────────────────────────────
'''

import_pattern = re.compile(r'^(import |from )', re.MULTILINE)
import_matches = list(import_pattern.finditer(code))

if import_matches:
    last_import_end = 0
    for m in import_matches:
        line_end = code.find('\n', m.start())
        if line_end > last_import_end:
            last_import_end = line_end
    code = code[:last_import_end + 1] + HUMAN_IMPORT + code[last_import_end + 1:]
    print("✅ Patch 1: HumanScoreEngine import added")
else:
    code = HUMAN_IMPORT + code
    print("✅ Patch 1: HumanScoreEngine import added (top of file)")

crown_patterns = [
    (r'if\s+score\s*>\s*best_score\b', 'if score > best_score  # Phoenix Patch: now 500pt scale'),
    (r'score\s*>=\s*275\b', 'score >= CROWN_THRESHOLD'),
    (r'score\s*==\s*275\b', 'score >= CROWN_THRESHOLD'),
]

patches_applied = 0
for pattern, replacement in crown_patterns:
    new_code = re.sub(pattern, replacement, code)
    if new_code != code:
        code = new_code
        patches_applied += 1
        print(f"✅ Patch 2.{patches_applied}: Crown threshold updated")

WISDOM_HOOK = '''
# ── Phoenix Forge: Wisdom Score Hook (Phase 2) ──────────────
# When wisdom_engine.py is ready, import it here:
# from wisdom_engine import WisdomEngine
# _wisdom_engine = WisdomEngine()
# wisdom_score = _wisdom_engine.score(app_path, domain_id)
# Total will become: tech(275) + human(225) + wisdom(100) = 600pt
# ─────────────────────────────────────────────────────────────
'''

code = code.replace(
    "CROWN_THRESHOLD_TECH_ONLY = 250  # fallback if human engine unavailable\n# ────────────────────────────────────────────────────────────",
    "CROWN_THRESHOLD_TECH_ONLY = 250  # fallback if human engine unavailable\n" + WISDOM_HOOK + "# ────────────────────────────────────────────────────────────"
)
print("✅ Patch 3: Wisdom score hook added")

TARGET.write_text(code)
new_lines = len(code.splitlines())
print(f"\n✅ Patched file written: {TARGET.name}")
print(f"   Lines: {original_lines} → {new_lines} (+{new_lines - original_lines})")

print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)

verify_code = TARGET.read_text()
checks = [
    ("HumanScoreEngine import", "HumanScoreEngine" in verify_code),
    ("_get_human_score function", "_get_human_score" in verify_code),
    ("CROWN_THRESHOLD = 400", "CROWN_THRESHOLD = 400" in verify_code),
    ("Wisdom hook present", "WisdomEngine" in verify_code),
]

all_pass = True
for name, result in checks:
    status = "✅" if result else "❌"
    print(f"  {status} {name}")
    if not result:
        all_pass = False

print("\n" + "=" * 60)
if all_pass:
    print("🔥 ALL PATCHES APPLIED SUCCESSFULLY")
    print("\nNext steps:")
    print("  1. Run: python3 turbo_evolve_enhanced_fixed.py")
    print("  2. Watch for apps scoring 400+")
else:
    print("⚠️  SOME PATCHES NEED MANUAL REVIEW")
    print(f"   Backup is safe at: {BACKUP.name}")

print("=" * 60)
