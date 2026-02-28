#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  PHOENIX FORGE — NEURAL ARCHITECTURE                             ║
║  Component 8 of 9: PITUITARY GLAND                               ║
║  Master regulator. Reads all hormones. Controls everything.      ║
║                                                                  ║
║  Install: cp pituitary.py ~/swarm-platform/                      ║
║  Run:     python3 ~/swarm-platform/pituitary.py                  ║
║  Requires: ALL other neural components installed                  ║
╚══════════════════════════════════════════════════════════════════╝

The pituitary gland is the master endocrine regulator.
It reads the state of all other systems and makes global decisions:
  — Is the organism ready to expand to 108 domains?
  — Is evolution too aggressive or too conservative?
  — Should we fire adrenaline to break stagnation?
  — Should we fire growth hormone to expand?

It reads ALL hormones and outputs a master directive:
  GROW     — expand domains, increase scope
  MAINTAIN — hold current course, refine quality
  PUSH     — stagnation detected, break through
  HEAL     — critical pain detected, prioritize relief
  REST     — consolidate, write memory, slow down

Emits:
  Growth Hormone — organism ready, expand domains
  Adrenaline     — global stagnation, push harder

Reads:
  All hormones — synthesizes global state
"""

import json
import sys
from pathlib import Path
from datetime import datetime

HOME           = Path("/data/data/com.termux/files/home")
SWARM          = HOME / "swarm-platform"
NEURAL_DIR     = SWARM / "neural"
CHAMPIONS      = HOME / "ORGANISM_ARMY/champions"
DIRECTIVE_FILE = NEURAL_DIR / "pituitary_directive.json"
PITUITARY_LOG  = NEURAL_DIR / "pituitary.log"

NEURAL_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SWARM))

from hormone_bus import HormoneBus, OrganismState

# ─────────────────────────────────────────────────────────────────
# GROWTH READINESS CRITERIA
# When ALL of these are met, fire growth hormone
# ─────────────────────────────────────────────────────────────────
GROWTH_CRITERIA = {
    "min_avg_score":      560,    # platform avg must be above this
    "min_balance_score":  0.75,   # cerebellum balance score
    "max_pain_level":     0.3,    # amygdala pain must be below this
    "min_domains":        50,     # must have at least this many champions
    "no_critical_stag":   True,   # no emergency stagnation active
}

# Directive decision matrix
DIRECTIVE_MATRIX = {
    "GROW":     "Platform mature — expand to new domains, increase scope",
    "MAINTAIN": "Platform healthy — refine quality, deepen existing domains",
    "PUSH":     "Stagnation detected — inject diversity, break patterns",
    "HEAL":     "Human pain critical — prioritize relief over everything",
    "REST":     "Consolidation needed — write memory, slow evolution",
}


class PituitaryGland:
    def __init__(self):
        self.bus       = HormoneBus()
        self.state     = OrganismState()
        self.directive = self._load_directive()
        self._log("Pituitary gland initialized")

    def _load_directive(self):
        if DIRECTIVE_FILE.exists():
            try:
                return json.loads(DIRECTIVE_FILE.read_text())
            except:
                pass
        return {
            "current":   "MAINTAIN",
            "history":   [],
            "generation": 0,
        }

    def _save(self):
        DIRECTIVE_FILE.write_text(json.dumps(self.directive, indent=2))

    def regulate(self, verbose=True):
        """
        Master regulation cycle. Reads everything. Decides direction.
        Emits appropriate hormones. Returns master directive.
        """
        if verbose:
            print("╔══════════════════════════════════════════════════════╗")
            print("║  PITUITARY — MASTER REGULATION CYCLE                  ║")
            print("╚══════════════════════════════════════════════════════╝\n")

        # Read all hormone levels
        all_hormones = {}
        for h_type in ["dopamine", "cortisol", "serotonin", "adrenaline",
                        "melatonin", "oxytocin", "growth_hormone", "testosterone"]:
            signals = self.bus.read("pituitary", h_type)
            if signals:
                avg_intensity = sum(s.intensity for s in signals) / len(signals)
                all_hormones[h_type] = {
                    "count":         len(signals),
                    "avg_intensity": round(avg_intensity, 2),
                    "top_context":   signals[0].context if signals else {},
                }

        # Load current organism metrics
        avg_score     = self.state.avg_score
        balance_score = self.state.balance_score
        pain_level    = self.state.pain_level
        stagnation    = self.state.stagnation_counter
        domains_count = self.state.domains_active
        phase         = self.state.phase

        # Count champion scores
        champion_scores = []
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
                    pass

        if champion_scores:
            avg_score     = sum(champion_scores) / len(champion_scores)
            domains_count = len(champion_scores)

        if verbose:
            print(f"  Organism metrics:")
            print(f"    Avg score:     {avg_score:.1f}/600")
            print(f"    Domains:       {domains_count}")
            print(f"    Balance:       {balance_score:.2f}")
            print(f"    Pain level:    {pain_level:.2f}")
            print(f"    Stagnation:    {stagnation} gens")
            print(f"    Current phase: {phase}")
            print(f"\n  Active hormones:")
            for h, data in all_hormones.items():
                from hormone_bus import HORMONES
                color = HORMONES.get(h, {}).get("color", "⚪")
                print(f"    {color} {h:15} count={data['count']} "
                      f"intensity={data['avg_intensity']:.2f}")

        # ── Decide directive ──
        directive = "MAINTAIN"
        reasoning = []
        hormone_to_emit = None
        growth_score = 0

        # Check HEAL condition (highest priority)
        if pain_level > 0.6 or "cortisol" in all_hormones:
            cortisol_intensity = all_hormones.get("cortisol", {}).get("avg_intensity", 0)
            if pain_level > 0.6 or cortisol_intensity > 0.7:
                directive = "HEAL"
                reasoning.append(f"Critical human pain: {pain_level:.2f}")
                if "cortisol" in all_hormones:
                    ctx = all_hormones["cortisol"]["top_context"]
                    reasoning.append(f"Cortisol source: {ctx.get('domain','unknown')}")

        # Check PUSH condition
        elif stagnation >= 20 or "adrenaline" in all_hormones:
            directive = "PUSH"
            reasoning.append(f"Stagnation: {stagnation} gens")
            hormone_to_emit = "adrenaline"

        # Check REST condition
        elif "melatonin" in all_hormones or phase == "rest":
            directive = "REST"
            reasoning.append("Melatonin active — consolidation cycle")

        # Check GROW condition
        else:
            grow_checks = {
                "avg_score_sufficient":  avg_score >= GROWTH_CRITERIA["min_avg_score"],
                "platform_balanced":     balance_score >= GROWTH_CRITERIA["min_balance_score"],
                "pain_acceptable":       pain_level <= GROWTH_CRITERIA["max_pain_level"],
                "enough_domains":        domains_count >= GROWTH_CRITERIA["min_domains"],
                "no_emergency":          stagnation < 20,
            }
            growth_score = sum(1 for v in grow_checks.values() if v)
            grow_pct     = growth_score / len(grow_checks)

            if grow_pct >= 0.8:
                directive = "GROW"
                reasoning.append(f"Growth criteria met: {growth_score}/{len(grow_checks)}")
                hormone_to_emit = "growth_hormone"
            else:
                directive = "MAINTAIN"
                failing = [k for k, v in grow_checks.items() if not v]
                reasoning.append(f"Not ready to grow — failing: {failing}")

        if verbose:
            print(f"\n  Decision: {directive}")
            for r in reasoning:
                print(f"    → {r}")
            print(f"  Meaning: {DIRECTIVE_MATRIX[directive]}")

        # Emit hormones based on directive
        if hormone_to_emit == "adrenaline":
            self.bus.emit(
                "adrenaline",
                source="pituitary",
                intensity=0.9,
                context={
                    "directive":  directive,
                    "reason":     reasoning[0] if reasoning else "stagnation",
                    "action":     "Global push — increase mutation, inject diversity",
                }
            )
            if verbose:
                print(f"\n  ⚡ Adrenaline emitted — PUSH directive")

        elif hormone_to_emit == "growth_hormone":
            self.bus.emit(
                "growth_hormone",
                source="pituitary",
                intensity=0.7,
                context={
                    "directive":      directive,
                    "current_domains": domains_count,
                    "target_domains":  108,
                    "growth_score":    f"{growth_score}/5",
                    "action":         f"Expand platform — build next high-pain domain",
                }
            )
            if verbose:
                print(f"\n  🟠 Growth hormone emitted — GROW directive")
                print(f"     Current: {domains_count} domains → Target: 108")

        # Build master directive output
        questions_file = NEURAL_DIR / "prefrontal_questions.json"
        next_question  = None
        if questions_file.exists():
            try:
                qdata = json.loads(questions_file.read_text())
                queue = qdata.get("queue", [])
                if queue:
                    next_question = queue[0]["question"]
            except:
                pass

        transfers_file = NEURAL_DIR / "corpus_callosum_transfers.json"
        next_transfer  = None
        if transfers_file.exists():
            try:
                tdata = json.loads(transfers_file.read_text())
                transfers = tdata.get("transfers", [])
                high = [t for t in transfers if t.get("priority") == "high"]
                if high:
                    next_transfer = high[0]
            except:
                pass

        balance_file = NEURAL_DIR / "cerebellum_balance.json"
        next_priority = None
        if balance_file.exists():
            try:
                bdata = json.loads(balance_file.read_text())
                priorities = bdata.get("evolution_priorities", [])
                if priorities:
                    next_priority = priorities[0]
            except:
                pass

        master_directive = {
            "directive":       directive,
            "meaning":         DIRECTIVE_MATRIX[directive],
            "reasoning":       reasoning,
            "hormone_emitted": hormone_to_emit,
            "organism": {
                "avg_score":     round(avg_score, 1),
                "domains":       domains_count,
                "balance":       balance_score,
                "pain_level":    pain_level,
                "stagnation":    stagnation,
                "phase":         phase,
            },
            "active_hormones":    all_hormones,
            "next_question":      next_question,
            "next_transfer":      next_transfer,
            "next_evolution_priority": next_priority,
            "generated_at":       datetime.now().isoformat(),
        }

        # Save
        self.directive["current"]   = directive
        self.directive["last"]      = master_directive
        self.directive["generation"] += 1
        self.directive["history"].append({
            "directive": directive,
            "avg_score": round(avg_score, 1),
            "timestamp": datetime.now().isoformat(),
        })
        self.directive["history"] = self.directive["history"][-100:]
        self._save()

        if verbose:
            print(f"\n{'═'*60}")
            print(f"  PITUITARY DIRECTIVE: {directive}")
            print(f"{'═'*60}")
            if next_question:
                print(f"  Next question:  {next_question[:65]}...")
            if next_transfer:
                print(f"  Next transfer:  {next_transfer.get('from_domain','?')} → "
                      f"{next_transfer.get('to_domain','?')}")
            if next_priority:
                print(f"  Next evolution: {next_priority.get('domain','?')} "
                      f"({next_priority.get('score','?')}/600) — "
                      f"{next_priority.get('reason','?')[:40]}")
            print(f"\n  Master directive saved: {DIRECTIVE_FILE}")
            print(f"\n  Next: python3 ~/swarm-platform/phoenix_mind.py")

        self._log(f"Directive={directive} avg={avg_score:.1f} "
                  f"hormone={hormone_to_emit}")
        return master_directive

    def _log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(PITUITARY_LOG, "a") as f:
            f.write(f"[{timestamp}] {msg}\n")


if __name__ == "__main__":
    pituitary  = PituitaryGland()
    directive  = pituitary.regulate(verbose=True)
