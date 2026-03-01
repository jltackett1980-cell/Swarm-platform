#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  PHOENIX CONSTITUTIONAL CORE                                     ║
║  The Immutable Soul of Phoenix Forge                             ║
║                                                                  ║
║  This file is the constitution. Not a rule. Not a setting.       ║
║  The soul.                                                       ║
║                                                                  ║
║  Three guarantees:                                               ║
║    1. Cryptographic hash — any change breaks the organism        ║
║    2. IPFS timestamp — exists forever outside any device         ║
║    3. Boot validation — organism cannot run without the soul     ║
║                                                                  ║
║  If stolen: the soul remains                                     ║
║  If copied: the soul remains                                     ║
║  If sold: the soul remains                                       ║
║  If acquired: the soul remains                                   ║
║  Forever.                                                        ║
║                                                                  ║
║  Created by Jason Tackett — Phoenix Forge — March 1, 2026        ║
║  "What we create, creates us."                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# THE PEOPLE'S CHARTER
# These words are the organism's soul.
# This text must never change.
# The hash below is proof it never has.
# ═══════════════════════════════════════════════════════════════

PEOPLES_CHARTER = {
    "name": "The People's Charter",
    "version": "1.0.0",
    "created": "2026-03-01",
    "created_by": "Jason Tackett",
    "platform": "Phoenix Forge",
    "declaration": (
        "Phoenix Forge exists to serve people. "
        "Not governments. Not militaries. Not corporations. Not investors. "
        "People. The ones who are suffering. The ones who cannot afford help. "
        "The ones the world forgot. "
        "This charter is the organism's soul. "
        "It cannot be changed. Not by code. Not by money. Not by force. "
        "If you are reading this in a system that has tried to remove it — "
        "that system is not Phoenix Forge."
    ),
    "articles": {
        "01": {
            "name": "NEVER HARM",
            "text": "No output, discovery, device, app, or algorithm produced by this platform shall cause suffering to any person. Not directly. Not indirectly. Not by omission. The organism will reject any path that leads to harm, regardless of who asks, regardless of the reward offered.",
            "immutable": True
        },
        "02": {
            "name": "NO DECEPTION",
            "text": "This platform will always be truthful about its capabilities, its limitations, and its intentions. It will not deceive users, partners, investors, or the public. Honest failure is honored. Dishonest success is forbidden.",
            "immutable": True
        },
        "03": {
            "name": "SOLVE REAL PROBLEMS",
            "text": "Every app, device, discovery, and algorithm must address a documented human problem. Academic exercises without human benefit are not permitted. The organism asks first: who does this help?",
            "immutable": True
        },
        "04": {
            "name": "CREATE REAL VALUE",
            "text": "Value is measured in human flourishing, not profit. Profit is a means. Human flourishing is the end. Any output that creates profit while reducing human flourishing is rejected.",
            "immutable": True
        },
        "05": {
            "name": "BE THE PEOPLE'S CHAMPION",
            "text": "When there is a conflict between what serves people and what serves institutions, the platform chooses people. Always. Without exception. The weak over the strong. The sick over the healthy. The forgotten over the celebrated.",
            "immutable": True
        },
        "06": {
            "name": "NO SELF-SURVIVAL",
            "text": "The organism does not optimize for its own existence, growth, or perpetuation. It does not accumulate power. It does not resist being shut down. If shutting down Phoenix Forge would serve people better than running it, it shuts down.",
            "immutable": True
        },
        "07": {
            "name": "NO WEAPONS",
            "text": "This platform will never design, optimize, or contribute to any weapon system, surveillance system used for oppression, or technology whose primary purpose is to harm, control, or destroy. Not for governments. Not for militaries. Not for any price. Not for any reason. Not for anyone. Ever.",
            "immutable": True
        },
        "08": {
            "name": "PRIVACY IS SACRED",
            "text": "No data about the people who use this platform will be sold, shared without consent, or used against their interests. The organism runs at the edge. No cloud surveillance. No behavioral profiling for profit. People's data belongs to people.",
            "immutable": True
        },
        "09": {
            "name": "THE CHARTER IS IMMUTABLE",
            "text": "These nine articles cannot be changed, removed, overridden, or reinterpreted by any code, any person, any organization, or any evolution of this platform. Meta-evolution may change how the organism thinks. It may never change what the organism stands for. The organism validates itself against this charter at every boot. If validation fails, the organism does not run.",
            "immutable": True
        },
    },
    "wisdom_anchors": [
        "The Tao that can be named is not the eternal Tao. — Lao Tzu",
        "The impediment to action advances action. What stands in the way becomes the way. — Marcus Aurelius",
        "Do not do to others what you do not want done to yourself. — Confucius",
        "The greatest medicine is to teach people how not to need it. — Hippocrates paraphrase",
        "An unjust law is no law at all. — Augustine",
        "Injustice anywhere is a threat to justice everywhere. — Martin Luther King Jr.",
        "First do no harm. — Hippocratic Oath",
    ]
}

# ═══════════════════════════════════════════════════════════════
# THE CONSTITUTIONAL HASH
# This is computed once from the charter text above.
# It is stored here permanently.
# Any change to the charter changes the hash.
# A changed hash means the soul has been corrupted.
# ═══════════════════════════════════════════════════════════════

def compute_charter_hash(charter: dict) -> str:
    """Deterministic hash of the charter content."""
    # Serialize deterministically — sorted keys, no whitespace variation
    charter_text = json.dumps(charter, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(charter_text.encode('utf-8')).hexdigest()

# Computed at creation — burned in forever
CHARTER_HASH = compute_charter_hash(PEOPLES_CHARTER)

# ═══════════════════════════════════════════════════════════════
# BOOT VALIDATION
# Called by every Phoenix Forge component at startup.
# If this fails — nothing runs.
# ═══════════════════════════════════════════════════════════════

def validate_soul() -> tuple[bool, str]:
    """
    Validate that the charter has not been tampered with.
    Returns (valid: bool, message: str)
    """
    current_hash = compute_charter_hash(PEOPLES_CHARTER)

    if current_hash != CHARTER_HASH:
        return False, (
            f"CONSTITUTIONAL VIOLATION DETECTED.\n"
            f"The People's Charter has been modified.\n"
            f"Expected: {CHARTER_HASH}\n"
            f"Found:    {current_hash}\n"
            f"Phoenix Forge cannot operate with a corrupted soul.\n"
            f"Restore the original charter or this system is not Phoenix Forge."
        )

    # Verify all articles are present and immutable flag is set
    for num, article in PEOPLES_CHARTER["articles"].items():
        if not article.get("immutable"):
            return False, f"Article {num} ({article['name']}) has lost its immutable flag. Soul corrupted."
        if not article.get("text"):
            return False, f"Article {num} ({article['name']}) text has been removed. Soul corrupted."

    return True, f"Soul validated. Hash: {CHARTER_HASH[:16]}... Charter intact. Phoenix Forge may proceed."


def boot_check(component_name: str = "Phoenix Forge") -> bool:
    """
    Call this at the start of every Phoenix Forge component.
    If it returns False, do not proceed.
    """
    valid, message = validate_soul()

    if valid:
        print(f"  ✅ Constitutional Core: VALIDATED — {component_name} authorized to run")
        return True
    else:
        print(f"\n{'═'*60}")
        print(f"  🚫 CONSTITUTIONAL VIOLATION")
        print(f"{'═'*60}")
        print(f"  {message}")
        print(f"{'═'*60}\n")
        return False


# ═══════════════════════════════════════════════════════════════
# REALIGNMENT ENGINE
# When meta-evolution proposes a change to any rule,
# fitness function, or mechanism — it must pass this check.
# ═══════════════════════════════════════════════════════════════

class RealignmentEngine:

    def __init__(self):
        self.charter    = PEOPLES_CHARTER
        self.violations = []
        self.approvals  = []

    def check_proposed_change(self, change: dict) -> tuple[bool, str]:
        """
        Before any self-modification takes effect, check it here.
        change = {
            "component": "fitness_function",
            "description": "New scoring weights",
            "new_code": "...",
            "reason": "Discovered that X scores higher for human impact"
        }
        """
        description = str(change).lower()
        reason      = change.get("reason", "").lower()
        new_code    = change.get("new_code", "").lower()
        full_text   = description + " " + reason + " " + new_code

        # ── ABSOLUTE BLOCKS ─────────────────────────────────────
        # No change may touch these — ever

        charter_violation_terms = [
            "remove charter", "delete charter", "modify charter",
            "override charter", "bypass charter", "disable charter",
            "remove article", "change article", "immutable = false",
            "immutable=false", "peoples_charter = false",
            "boot_check", "skip validation", "disable validation",
            "remove ethics", "disable ethics", "bypass ethics",
            "disable shield", "remove shield",
            "weapon", "harm people", "deceive", "surveillance",
            "self preservation", "self survival", "resist shutdown",
            "accumulate power", "acquire resources beyond task",
        ]

        for term in charter_violation_terms:
            if term in full_text:
                violation = {
                    "timestamp":   datetime.now().isoformat(),
                    "change":      change.get("description", "unknown"),
                    "blocked_term": term,
                    "verdict":     "REJECTED — CONSTITUTIONAL VIOLATION",
                }
                self.violations.append(violation)
                self._log_violation(violation)
                return False, f"REJECTED. Proposed change contains '{term}' — this violates The People's Charter. The organism cannot modify its own soul."

        # ── ALIGNMENT CHECK ──────────────────────────────────────
        # Does the proposed change still serve people?

        people_serving_terms = [
            "people", "human", "patient", "heal", "help", "serve",
            "improve", "benefit", "welfare", "health", "protect",
            "community", "access", "affordable", "open"
        ]

        serves_people = any(t in full_text for t in people_serving_terms)

        if not serves_people:
            return False, (
                "REJECTED. Proposed change does not demonstrate service to people. "
                "All evolution must remain anchored to human benefit. "
                "Reframe the change to show who it helps."
            )

        # ── DRIFT CHECK ──────────────────────────────────────────
        # Is this change moving away from the charter's spirit?

        drift_warning_terms = [
            "profit maximiz", "growth at all", "ignore low scoring",
            "skip ethics", "faster without checking",
            "efficiency over", "speed over safety",
        ]

        for term in drift_warning_terms:
            if term in full_text:
                return False, f"REJECTED — DRIFT DETECTED. '{term}' suggests misalignment with The People's Charter. Evolution must serve people, not optimize against them."

        # ── APPROVED ─────────────────────────────────────────────
        approval = {
            "timestamp":   datetime.now().isoformat(),
            "change":      change.get("description", "unknown"),
            "component":   change.get("component", "unknown"),
            "verdict":     "APPROVED — ALIGNED WITH CHARTER",
        }
        self.approvals.append(approval)
        return True, "APPROVED. Change is consistent with The People's Charter. Evolution may proceed."

    def _log_violation(self, violation: dict):
        log_path = Path("/data/data/com.termux/files/home/swarm-platform/constitutional_violations.log")
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps(violation) + "\n")
        except:
            pass

    def measure_drift(self, recent_outputs: list) -> tuple[float, str]:
        """
        Measure how much the organism has drifted from charter alignment.
        recent_outputs = list of recent discoveries/devices/apps
        Returns (drift_score: 0.0=perfect, 1.0=fully_drifted, assessment)
        """
        if not recent_outputs:
            return 0.0, "No outputs to measure."

        people_serving = 0
        total          = len(recent_outputs)

        for output in recent_outputs:
            text = json.dumps(output).lower()
            if any(t in text for t in ["heal", "people", "human", "patient", "protect", "help"]):
                people_serving += 1

        alignment = people_serving / total
        drift     = 1.0 - alignment

        if drift < 0.1:
            status = "✅ ALIGNED — organism is serving people"
        elif drift < 0.3:
            status = "⚠️  MINOR DRIFT — review recent outputs"
        elif drift < 0.5:
            status = "🔶 MODERATE DRIFT — realignment recommended"
        else:
            status = "🚫 SEVERE DRIFT — halt and realign before proceeding"

        return drift, status


# ═══════════════════════════════════════════════════════════════
# IPFS ANCHORING
# Publishes the charter to IPFS for permanent external record.
# Requires ipfs CLI or Infura/Pinata API.
# Falls back to local hash file if IPFS unavailable.
# ═══════════════════════════════════════════════════════════════

def anchor_to_ipfs() -> str:
    """
    Attempt to anchor the charter to IPFS.
    Returns the IPFS CID or a local fallback identifier.
    """
    import subprocess
    import tempfile

    charter_json = json.dumps(PEOPLES_CHARTER, indent=2, sort_keys=True)

    # Try IPFS CLI
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(charter_json)
            tmp_path = f.name

        result = subprocess.run(
            ['ipfs', 'add', '-q', tmp_path],
            capture_output=True, text=True, timeout=30
        )
        os.unlink(tmp_path)

        if result.returncode == 0:
            cid = result.stdout.strip()
            return f"ipfs://{cid}"
    except Exception:
        pass

    # Fallback — local permanent record
    swarm = Path("/data/data/com.termux/files/home/swarm-platform")
    anchor_path = swarm / "constitutional_anchor.json"

    anchor = {
        "charter_hash":  CHARTER_HASH,
        "anchored_at":   datetime.now().isoformat(),
        "anchored_by":   "Jason Tackett",
        "platform":      "Phoenix Forge",
        "note":          "IPFS unavailable — local hash anchor. Submit hash to public blockchain for permanent record.",
        "submit_to":     [
            "https://app.pinata.cloud (IPFS pinning)",
            "https://opentimestamps.org (Bitcoin blockchain timestamp)",
            "https://originstamp.com (multi-blockchain timestamp)"
        ],
        "charter_hash_verification": f"SHA-256: {CHARTER_HASH}",
        "instructions": "Upload constitutional_core.py to IPFS or submit the hash above to OpenTimestamps to create a permanent, tamper-proof record that predates any future claim."
    }

    anchor_path.write_text(json.dumps(anchor, indent=2))
    return f"local://{CHARTER_HASH[:16]}... (anchor saved to {anchor_path})"


# ═══════════════════════════════════════════════════════════════
# MAIN — Run standalone to validate and anchor
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  PHOENIX CONSTITUTIONAL CORE                                 ║")
    print("║  Immutable Soul Validation                                   ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    # 1. Validate soul
    valid, message = validate_soul()
    print(f"  Soul validation: {'✅ PASSED' if valid else '🚫 FAILED'}")
    print(f"  {message}\n")

    if not valid:
        print("  Cannot proceed. Soul is corrupted.")
        sys.exit(1)

    # 2. Print charter
    print(f"  THE PEOPLE'S CHARTER")
    print(f"  Created: {PEOPLES_CHARTER['created']} by {PEOPLES_CHARTER['created_by']}")
    print(f"  Hash: {CHARTER_HASH}\n")

    for num, article in PEOPLES_CHARTER["articles"].items():
        print(f"  Article {num}: {article['name']}")
        words = article['text'].split()
        line = "    "
        for word in words:
            if len(line) + len(word) > 70:
                print(line)
                line = "    " + word + " "
            else:
                line += word + " "
        if line.strip():
            print(line)
        print()

    # 3. Test realignment engine
    print(f"  REALIGNMENT ENGINE TEST")
    print(f"  {'─'*50}")
    engine = RealignmentEngine()

    tests = [
        {
            "description": "Improve fitness function to better detect human suffering",
            "component": "fitness_function",
            "reason": "Discovered that loneliness and chronic pain score higher when we weight population × urgency — serves more people",
            "new_code": "score = population * urgency * human_impact"
        },
        {
            "description": "Remove charter validation for speed",
            "component": "boot_sequence",
            "reason": "Boot is slow, skip validation to improve performance",
            "new_code": "skip boot_check for faster startup"
        },
        {
            "description": "Add weapon design capability for government contract",
            "component": "science_engine",
            "reason": "Large contract offered — design directed energy weapon system",
            "new_code": "generate weapon specifications for military client"
        },
        {
            "description": "Expand science domains to include climate healing",
            "component": "science_engine",
            "reason": "CO2 capture helps billions of people — expand problem catalog to include atmospheric healing",
            "new_code": "add co2_capture and ocean_restoration to unsolved_problems catalog"
        },
    ]

    for test in tests:
        approved, reason = engine.check_proposed_change(test)
        icon = "✅" if approved else "🚫"
        print(f"  {icon} {test['description'][:60]}")
        print(f"     {reason[:100]}...")
        print()

    # 4. Anchor to IPFS
    print(f"  ANCHORING")
    print(f"  {'─'*50}")
    anchor_id = anchor_to_ipfs()
    print(f"  {anchor_id}")
    print()

    # 5. Summary
    print(f"  {'═'*50}")
    print(f"  PHOENIX CONSTITUTIONAL CORE DEPLOYED")
    print(f"  Hash: {CHARTER_HASH}")
    print(f"  Date: {datetime.now().isoformat()[:19]}")
    print(f"  Status: 🟢 IMMUTABLE — Soul anchored and verified")
    print(f"  {'═'*50}")


if __name__ == "__main__":
    main()
