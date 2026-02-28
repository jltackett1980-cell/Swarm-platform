#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  PHOENIX FORGE — NEURAL ARCHITECTURE                             ║
║  Component 4 of 9: CORPUS CALLOSUM                               ║
║  Transfers insight between domains. The bridge.                  ║
║                                                                  ║
║  Install: cp corpus_callosum.py ~/swarm-platform/                ║
║  Run:     python3 ~/swarm-platform/corpus_callosum.py            ║
║  Requires: hormone_bus.py, hippocampus.py installed              ║
╚══════════════════════════════════════════════════════════════════╝

The corpus callosum connects the left and right hemispheres of the brain.
Here it connects high-scoring domains to lower-scoring ones.

When salon scores 590, the corpus callosum asks:
  "What does salon know that law doesn't?"
  "Can frictionless trust work in a legal context?"
  "How would we adapt salon's greeting pattern for a courtroom?"

Then it writes domain-specific upgrade instructions so the next
evolution run benefits from what the best domains already know.

Reads:
  Dopamine  — which patterns to transfer (hippocampus saw something good)
  Oxytocin  — which human connections to amplify across domains

Emits:
  Dopamine  — when a successful cross-domain transfer is identified
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
# ABSOLUTE PATHS
# ─────────────────────────────────────────────────────────────────
HOME           = Path("/data/data/com.termux/files/home")
SWARM          = HOME / "swarm-platform"
NEURAL_DIR     = SWARM / "neural"
CHAMPIONS      = HOME / "ORGANISM_ARMY/champions"
FEDERATION     = SWARM / "federation"
TRANSFER_FILE  = NEURAL_DIR / "corpus_callosum_transfers.json"
CORPUS_LOG     = NEURAL_DIR / "corpus_callosum.log"

NEURAL_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SWARM))

from hormone_bus import HormoneBus, OrganismState

# ─────────────────────────────────────────────────────────────────
# DOMAIN AFFINITY MAP
# Which domains naturally share insight with each other
# ─────────────────────────────────────────────────────────────────
DOMAIN_AFFINITY = {
    "salon":       ["spa", "beauty", "yoga", "gym", "fitness"],
    "healthcare":  ["pharmacy", "dental", "mental_health", "mental_wellness",
                    "telehealth", "rural_health_clinic"],
    "restaurant":  ["bakery", "catering", "nutrition_center"],
    "law":         ["insurance", "realestate", "freelancer", "accounting"],
    "daycare":     ["school", "tutoring", "education", "ministry", "church"],
    "gym":         ["yoga", "fitness", "spa", "salon"],
    "plumber":     ["construction", "autorepair", "cleaning", "electrician",
                    "hvac", "roofing"],
    "smart_farm":  ["drone_delivery", "rf_sensing", "robotics",
                    "autonomous_vehicle"],
    "nonprofit":   ["church", "ministry", "homeless_services", "food_pantry",
                    "domestic_violence_shelter", "foster_care"],
    "mental_health": ["addiction_recovery", "mental_wellness", "telehealth",
                      "domestic_violence_shelter"],
    "credit_union": ["mortgage_broker", "small_business_lending",
                     "budget_coaching", "debt_counseling"],
    "solar_installation": ["home_energy_audit", "energy_cooperative",
                           "off_grid_living", "green_building"],
}

# ─────────────────────────────────────────────────────────────────
# TRANSFER TEMPLATES
# How to adapt a pattern from one domain to another
# ─────────────────────────────────────────────────────────────────
TRANSFER_TEMPLATES = {
    "wu_wei_flow": {
        "what":      "Effortless flow — app gets out of user's way",
        "from_example": {
            "salon":      "Add appointment in under 10 seconds",
            "gym":        "Log workout in 3 taps",
            "restaurant": "Table seated, order placed, done",
        },
        "adapt_for": {
            "law":        "File a note on a client in under 10 seconds",
            "healthcare": "Add patient record with 3 fields max first",
            "accounting": "Record a transaction in one tap",
            "insurance":  "File a claim start to finish in under 60 seconds",
        },
    },
    "today_focus": {
        "what":      "Lead with what matters right now, not everything",
        "from_example": {
            "salon":      "Today's appointments — big, clear, impossible to miss",
            "healthcare": "Today's patients — who's arriving next",
            "restaurant": "Today's orders — what's up next",
        },
        "adapt_for": {
            "law":         "Today's deadlines and client calls",
            "daycare":     "Today's children, allergies, who's been picked up",
            "nonprofit":   "Today's volunteers, today's need",
            "mental_health": "Today's sessions, risk flags since last visit",
        },
    },
    "human_greeting": {
        "what":      "Acknowledge the person — don't just show data",
        "from_example": {
            "salon":   "Welcome back — you have 3 appointments today",
            "gym":     "Ready to crush it? Your next session is at 2pm",
            "daycare": "Good morning! 12 children checked in so far",
        },
        "adapt_for": {
            "law":          "Good morning — 2 deadlines this week, 1 client waiting",
            "accounting":   "Morning — your books are balanced. 3 invoices pending.",
            "construction": "Morning — 4 jobs active today. Weather looks clear.",
            "plumber":      "You have 3 calls today. Next one is in 45 minutes.",
        },
    },
    "offline_first": {
        "what":      "Works without internet — data survives connection loss",
        "from_example": {
            "all": "localStorage — data persists across sessions, no server needed",
        },
        "adapt_for": {
            "rural_health_clinic":  "Rural clinic — must work with spotty signal",
            "smart_farm":           "Farm field — no wifi, data must sync later",
            "drone_delivery":       "Remote delivery — offline maps and manifest",
            "construction":         "Job site — no reliable internet",
        },
    },
}


class CorpusCallosum:
    def __init__(self):
        self.bus      = HormoneBus()
        self.state    = OrganismState()
        self.transfers = self._load_transfers()
        self._log("Corpus callosum initialized")

    def _load_transfers(self):
        if TRANSFER_FILE.exists():
            try:
                return json.loads(TRANSFER_FILE.read_text())
            except:
                pass
        return {"transfers": [], "generation": 0}

    def _save(self):
        TRANSFER_FILE.write_text(json.dumps(self.transfers, indent=2))

    def transfer(self, verbose=True):
        """
        Read hormone signals, find cross-domain insight opportunities,
        and write transfer instructions for the evolution engine.
        """
        if verbose:
            print("╔══════════════════════════════════════════════════════╗")
            print("║  CORPUS CALLOSUM — TRANSFERRING INSIGHT               ║")
            print("╚══════════════════════════════════════════════════════╝\n")

        # Read dopamine signals — what patterns worked
        dopamine_signals = self.bus.read("corpus_callosum", "dopamine")
        oxytocin_signals = self.bus.read("corpus_callosum", "oxytocin")

        # Load all champion scores
        scores = {}
        for champ_dir in CHAMPIONS.iterdir():
            if not champ_dir.is_dir():
                continue
            champ_file = champ_dir / "champion.json"
            if champ_file.exists():
                try:
                    champ = json.loads(champ_file.read_text())
                    scores[champ_dir.name] = champ.get("total_score", 574)
                except:
                    pass

        if not scores:
            for fed_dir in FEDERATION.iterdir():
                if fed_dir.is_dir():
                    scores[fed_dir.name] = 574

        # Sort by score
        sorted_domains = sorted(scores.items(), key=lambda x: -x[1])
        top_domains    = [d for d, s in sorted_domains if s >= 580]
        low_domains    = [d for d, s in sorted_domains if s < 475]

        if verbose:
            print(f"  Top performers (≥580): {top_domains}")
            print(f"  Needs help (<475):     {low_domains}\n")

        transfer_instructions = []
        dopamine_count = 0

        # For each top domain, find related lower domains and write transfers
        for top_domain in top_domains:
            top_score  = scores.get(top_domain, 580)
            related    = DOMAIN_AFFINITY.get(top_domain, [])

            for target_domain in related:
                target_score = scores.get(target_domain, 574)
                if target_score >= top_score:
                    continue  # already as good or better

                score_gap = top_score - target_score

                # Find applicable transfer templates
                applicable = []
                for template_name, template in TRANSFER_TEMPLATES.items():
                    adapt = template.get("adapt_for", {})
                    if target_domain in adapt:
                        applicable.append({
                            "template":    template_name,
                            "what":        template["what"],
                            "example_from": template["from_example"].get(
                                top_domain,
                                list(template["from_example"].values())[0]
                            ),
                            "apply_as":    adapt[target_domain],
                        })

                if not applicable:
                    # Generic transfer
                    applicable.append({
                        "template":    "score_pattern",
                        "what":        f"{top_domain} scores {top_score} — study its approach",
                        "example_from": f"See {FEDERATION}/{top_domain}/frontend/index.html",
                        "apply_as":    f"Apply {top_domain} patterns to {target_domain}",
                    })

                instruction = {
                    "from_domain":   top_domain,
                    "to_domain":     target_domain,
                    "score_gap":     score_gap,
                    "from_score":    top_score,
                    "to_score":      target_score,
                    "transfers":     applicable,
                    "priority":      "high" if score_gap > 30 else "medium",
                    "created_at":    datetime.now().isoformat(),
                }
                transfer_instructions.append(instruction)

                if verbose:
                    print(f"  📡 {top_domain:20} → {target_domain:20} "
                          f"(gap: {score_gap})")
                    for a in applicable[:1]:
                        print(f"     Transfer: {a['what']}")
                        print(f"     Apply as: {a['apply_as']}")

                # Emit dopamine for successful transfer identification
                if score_gap > 20:
                    dopamine_count += 1
                    self.bus.emit(
                        "dopamine",
                        source="corpus_callosum",
                        intensity=min(1.0, score_gap / 100),
                        context={
                            "transfer_from":  top_domain,
                            "transfer_to":    target_domain,
                            "score_gap":      score_gap,
                            "key_transfer":   applicable[0]["what"] if applicable else "score pattern",
                            "action":         f"Apply {top_domain} insight to {target_domain} in next evolution",
                        }
                    )

        # Also process oxytocin signals — deep human connections to spread
        for signal in oxytocin_signals:
            ctx = signal.context
            if "domains" in ctx:
                insight = ctx.get("insight", "")
                pattern = ctx.get("pattern", "")
                if verbose and insight:
                    print(f"\n  💗 Oxytocin signal: {insight}")
                    print(f"     Pattern: {pattern}")
                    print(f"     Spreading to all domains...")

                # Create universal transfer from this insight
                transfer_instructions.append({
                    "from_domain":  ctx.get("domains", ["unknown"])[0],
                    "to_domain":    "ALL",
                    "score_gap":    0,
                    "transfers": [{
                        "template":   "oxytocin_insight",
                        "what":       insight,
                        "example_from": pattern,
                        "apply_as":   f"Wire this into all domains: {insight}",
                    }],
                    "priority":    "critical",
                    "source":      "oxytocin",
                    "created_at":  datetime.now().isoformat(),
                })

        # Save transfers
        self.transfers["transfers"].extend(transfer_instructions)
        self.transfers["transfers"] = self.transfers["transfers"][-200:]
        self.transfers["generation"] += 1
        self.transfers["last_run"] = datetime.now().isoformat()
        self.transfers["pending_count"] = len(
            [t for t in transfer_instructions if t.get("priority") == "high"]
        )
        self._save()

        report = {
            "transfers_identified": len(transfer_instructions),
            "high_priority":        len([t for t in transfer_instructions
                                         if t.get("priority") == "high"]),
            "dopamine_emitted":     dopamine_count,
            "top_domains":          top_domains,
            "domains_need_help":    low_domains,
        }

        if verbose:
            print(f"\n{'═'*60}")
            print(f"  CORPUS CALLOSUM COMPLETE")
            print(f"{'═'*60}")
            print(f"  Transfers identified: {len(transfer_instructions)}")
            print(f"  High priority:        {report['high_priority']}")
            print(f"  Dopamine emitted:     {dopamine_count}x")
            print(f"  Saved to:             {TRANSFER_FILE}")
            print(f"\n  Next: python3 ~/swarm-platform/prefrontal.py")

        self._log(f"Transfer complete — {len(transfer_instructions)} transfers, "
                  f"{dopamine_count} dopamine")
        return report

    def get_instructions_for(self, domain_id):
        """Get pending transfer instructions for a specific domain"""
        return [
            t for t in self.transfers.get("transfers", [])
            if t.get("to_domain") == domain_id or t.get("to_domain") == "ALL"
        ]

    def _log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(CORPUS_LOG, "a") as f:
            f.write(f"[{timestamp}] {msg}\n")


if __name__ == "__main__":
    cc     = CorpusCallosum()
    report = cc.transfer(verbose=True)

    print(f"\n  Sample: instructions for 'law':")
    law_instructions = cc.get_instructions_for("law")
    for inst in law_instructions[:2]:
        print(f"    From: {inst['from_domain']} (score {inst.get('from_score','?')})")
        for t in inst["transfers"][:1]:
            print(f"    Apply: {t['apply_as']}")
