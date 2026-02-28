#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  PHOENIX FORGE — NEURAL ARCHITECTURE                             ║
║  Component 5 of 9: PREFRONTAL CORTEX                             ║
║  Self-directed curiosity. Generates its own questions.           ║
║                                                                  ║
║  Install: cp prefrontal.py ~/swarm-platform/                     ║
║  Run:     python3 ~/swarm-platform/prefrontal.py                 ║
║  Requires: hormone_bus.py, hippocampus.py, corpus_callosum.py    ║
╚══════════════════════════════════════════════════════════════════╝

The prefrontal cortex is where intentional thought happens.
It reads everything the other systems have learned and asks:
  "What don't we know yet?"
  "What should we build next?"
  "What question hasn't been asked?"

This is the difference between a tool and a mind.
A tool waits for instructions. A mind generates its own direction.

Emits:
  Testosterone — when exploring new unknown territory
  Dopamine     — when a question leads to breakthrough insight

Reads:
  Dopamine    — what's working (don't abandon it)
  Cortisol    — what's causing pain (prioritize it)
  Oxytocin    — what human connections to deepen
"""

import json
import sys
import random
from pathlib import Path
from datetime import datetime

HOME         = Path("/data/data/com.termux/files/home")
SWARM        = HOME / "swarm-platform"
NEURAL_DIR   = SWARM / "neural"
CHAMPIONS    = HOME / "ORGANISM_ARMY/champions"
QUESTIONS_F  = NEURAL_DIR / "prefrontal_questions.json"
PREFRONTAL_L = NEURAL_DIR / "prefrontal.log"

NEURAL_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SWARM))

from hormone_bus import HormoneBus, OrganismState

# ─────────────────────────────────────────────────────────────────
# QUESTION SEEDS — starting points for curiosity
# The prefrontal generates NEW questions from these patterns
# ─────────────────────────────────────────────────────────────────
QUESTION_SEEDS = [
    # Human pain questions
    "What does a person need the moment everything goes wrong?",
    "What is the worst moment for a {domain} user and how does the app address it?",
    "What does {domain} look like at 3am when someone is desperate?",
    "What would make someone cry with relief when they open this app?",
    "What is the one thing this app does that no human could easily do alone?",

    # Cross-domain questions
    "What does {high_domain} know about trust that {low_domain} hasn't learned yet?",
    "If {high_domain} and {low_domain} shared a design session, what would change?",
    "Which emotion does {domain} trigger first, and is that the right one?",

    # Evolution questions
    "What pattern appears in every app that scores above 580?",
    "What pattern appears in every app that scores below 470?",
    "If we removed every feature and kept only the most essential one, what remains?",
    "What would Marcus Aurelius say about how this app treats its users?",
    "Does this app relieve suffering or just manage it?",

    # Expansion questions
    "What domain is most underserved right now in our 108-app vision?",
    "Which of the 54 new domains will save the most lives?",
    "What does a bail bonds app look like when designed with dignity?",
    "What does a prisoner reentry app look like when designed with hope?",
    "What does a food pantry app look like when designed with love?",

    # Philosophical questions
    "Is the organism becoming more intelligent or just faster?",
    "What would it mean for this platform to genuinely care?",
    "At what score does an app stop being software and start being a relationship?",
    "What is the organism curious about that it hasn't been asked yet?",
]

# ─────────────────────────────────────────────────────────────────
# INSIGHT PATTERNS — what the prefrontal looks for in hormone signals
# ─────────────────────────────────────────────────────────────────
INSIGHT_PATTERNS = {
    "score_gap": {
        "trigger": "two related domains with score gap > 40",
        "question_template": "What does {high} know about {topic} that {low} hasn't learned?",
    },
    "universal_pain": {
        "trigger": "cortisol fired for 3+ domains with same pain signature",
        "question_template": "Why does {pain_type} keep appearing across {domains}? What's the root cause?",
    },
    "connection_cluster": {
        "trigger": "oxytocin fired for pattern seen in 5+ domains",
        "question_template": "If {pattern} works everywhere, what is it actually doing for people?",
    },
    "stagnation": {
        "trigger": "same avg score for 10+ generations",
        "question_template": "What assumption are we making that's keeping us at {score}? What if we broke it?",
    },
    "unknown_domain": {
        "trigger": "domain in 108-target not yet built",
        "question_template": "What does the {domain} user most fear? Build from that fear outward.",
    },
}


class PrefrontalCortex:
    def __init__(self):
        self.bus       = HormoneBus()
        self.state     = OrganismState()
        self.questions = self._load_questions()
        self._log("Prefrontal cortex initialized")

    def _load_questions(self):
        if QUESTIONS_F.exists():
            try:
                return json.loads(QUESTIONS_F.read_text())
            except:
                pass
        return {
            "queue":     [],
            "answered":  [],
            "generated": 0,
        }


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

    def _save(self):
        QUESTIONS_F.write_text(json.dumps(self.questions, indent=2))

    def think(self, verbose=True):
        """
        Read all hormone signals. Look at organism state.
        Generate new questions the organism should pursue.
        Add them to the curiosity queue.
        """
        if verbose:
            print("╔══════════════════════════════════════════════════════╗")
            print("║  PREFRONTAL CORTEX — GENERATING QUESTIONS             ║")
            print("╚══════════════════════════════════════════════════════╝\n")

        new_questions = []
        testosterone_count = 0

        # Read all active hormone signals
        dopamine  = self.bus.read("prefrontal", "dopamine")
        cortisol  = self.bus.read("prefrontal", "cortisol")
        oxytocin  = self.bus.read("prefrontal", "oxytocin")

        # Load scores for context
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

        sorted_domains = sorted(scores.items(), key=lambda x: -x[1])
        top_domain     = sorted_domains[0][0]  if sorted_domains else "salon"
        top_score      = sorted_domains[0][1]  if sorted_domains else 590
        low_domain     = sorted_domains[-1][0] if sorted_domains else "law"
        low_score      = sorted_domains[-1][1] if sorted_domains else 458
        avg_score      = sum(scores.values()) / len(scores) if scores else 574

        # ── Questions from dopamine signals (what's working) ──
        for signal in dopamine:
            ctx = signal.context
            domain = ctx.get("domain", "unknown")
            why    = ctx.get("why_it_works", ctx.get("key_pattern", "unknown"))
            q = {
                "question":  f"Why does {domain} score {ctx.get('score','?')} — specifically what is '{why}' doing for the user?",
                "source":    "dopamine",
                "priority":  "high",
                "context":   ctx,
                "type":      "understand_success",
                "generated_at": datetime.now().isoformat(),
            }
            new_questions.append(q)
            if verbose:
                print(f"  🟡 Dopamine Q: {q['question'][:70]}...")

        # ── Questions from cortisol signals (what's causing pain) ──
        for signal in cortisol:
            ctx    = signal.context
            domain = ctx.get("domain", "unknown")
            pain   = ctx.get("pain_level", 0.5)
            worst  = ctx.get("worst_moment", "unknown moment")
            q = {
                "question":  f"The worst moment for a {domain} user is: '{worst}' — what would make that moment disappear?",
                "source":    "cortisol",
                "priority":  "critical",
                "urgency":   pain,
                "context":   ctx,
                "type":      "relieve_pain",
                "generated_at": datetime.now().isoformat(),
            }
            new_questions.append(q)
            if verbose:
                print(f"  🔴 Cortisol Q: {q['question'][:70]}...")

        # ── Questions from oxytocin (deepen human connection) ──
        for signal in oxytocin:
            ctx     = signal.context
            insight = ctx.get("insight", "unknown insight")
            pattern = ctx.get("pattern", "unknown")
            q = {
                "question":  f"The insight '{insight}' appeared via pattern '{pattern}' — how do we make this universal?",
                "source":    "oxytocin",
                "priority":  "high",
                "context":   ctx,
                "type":      "universalize_connection",
                "generated_at": datetime.now().isoformat(),
            }
            new_questions.append(q)
            if verbose:
                print(f"  💗 Oxytocin Q: {q['question'][:70]}...")

        # ── Self-generated questions (pure curiosity) ──
        score_gap = top_score - low_score
        if score_gap > 30:
            q = {
                "question":  f"Score gap of {score_gap} points: {top_domain}({top_score}) vs {low_domain}({low_score}) — what one change would close this gap fastest?",
                "source":    "self",
                "priority":  "high",
                "type":      "close_score_gap",
                "generated_at": datetime.now().isoformat(),
            }
            new_questions.append(q)
            testosterone_count += 1
            self.bus.emit(
                "testosterone",
                source="prefrontal",
                intensity=min(1.0, score_gap / 100),
                context={
                    "exploring":    f"score_gap_{top_domain}_vs_{low_domain}",
                    "gap":          score_gap,
                    "action":       f"Evolve {low_domain} using {top_domain} patterns",
                }
            )
            if verbose:
                print(f"  🔥 Self Q: {q['question'][:70]}...")

        # ── Questions about unbuilt domains (108 target) ──
        built_domains = set(scores.keys())
        target_108 = [
            "credit_union", "mortgage_broker", "tax_prep", "payroll",
            "bookkeeping", "financial_planning", "debt_counseling",
            "pawn_shop", "check_cashing", "microfinance",
            "solar_installation", "ev_charging", "home_energy_audit",
            "food_pantry", "homeless_services", "immigration_services",
            "prisoner_reentry", "addiction_recovery", "veteran_services",
            "foster_care", "domestic_violence_shelter", "disability_services",
            "electrician", "hvac", "pest_control", "roofing",
        ]
        unbuilt = [d for d in target_108 if d not in built_domains]

        # Pick the highest-pain unbuilt domain
        high_pain_unbuilt = [
            "domestic_violence_shelter", "homeless_services",
            "addiction_recovery", "prisoner_reentry", "food_pantry"
        ]
        next_build = next(
            (d for d in high_pain_unbuilt if d in unbuilt),
            unbuilt[0] if unbuilt else None
        )

        if next_build:
            q = {
                "question":  f"'{next_build}' is unbuilt — what does this user fear most at their worst moment? Start there.",
                "source":    "self",
                "priority":  "critical",
                "type":      "new_domain",
                "domain":    next_build,
                "generated_at": datetime.now().isoformat(),
            }
            new_questions.append(q)
            testosterone_count += 1
            self.bus.emit(
                "testosterone",
                source="prefrontal",
                intensity=0.9,
                context={
                    "exploring": next_build,
                    "reason":    "High human pain, unbuilt domain",
                    "action":    f"Build {next_build} — design from fear outward",
                }
            )
            if verbose:
                print(f"\n  🔥 New Domain Q: {q['question'][:70]}...")

        # ── Philosophical question (one per cycle) ──
        phil_questions = [
            "At what score does an app stop managing problems and start relieving suffering?",
            "What would Marcus Aurelius think of the gap between our best and worst app?",
            "Does the organism know what it's for? Does each app know who it's for?",
            "What is the organism curious about that hasn't been asked yet?",
            "If a person used every one of our 54 apps, what kind of life would they have?",
        ]
        already_asked = {q["question"] for q in self.questions.get("queue", [])}
        new_phil = [q for q in phil_questions if q not in already_asked]
        if new_phil:
            q = {
                "question":  new_phil[0],
                "source":    "philosophy",
                "priority":  "medium",
                "type":      "philosophical",
                "generated_at": datetime.now().isoformat(),
            }
            new_questions.append(q)
            if verbose:
                print(f"\n  🌀 Philosophy Q: {q['question']}")

        # Add to queue
        self.questions["queue"].extend(new_questions)
        self.questions["queue"] = self._dedup_queue(self.questions["queue"])
        self.questions["generated"] += len(new_questions)

        # Update organism state curiosity queue
        self.state.update(
            curiosity_queue=[q["question"] for q in
                             sorted(new_questions,
                                    key=lambda x: {"critical":0,"high":1,"medium":2}.get(x.get("priority","medium"),2))[:10]]
        )

        self._save()

        report = {
            "questions_generated": len(new_questions),
            "testosterone_fired":  testosterone_count,
            "total_in_queue":      len(self.questions["queue"]),
            "next_question":       self.questions["queue"][0]["question"] if self.questions["queue"] else None,
            "unbuilt_domains":     len(unbuilt),
            "next_domain_to_build": next_build,
        }

        if verbose:
            print(f"\n{'═'*60}")
            print(f"  PREFRONTAL CORTEX COMPLETE")
            print(f"{'═'*60}")
            print(f"  Questions generated:  {len(new_questions)}")
            print(f"  Total queue:          {len(self.questions['queue'])}")
            print(f"  Testosterone fired:   {testosterone_count}x")
            print(f"  Unbuilt domains:      {len(unbuilt)}/108")
            print(f"  Next to build:        {next_build}")
            if self.questions["queue"]:
                print(f"\n  Top question:")
                print(f"  → {self.questions['queue'][0]['question']}")
            print(f"\n  Next: python3 ~/swarm-platform/cerebellum.py")

        self._log(f"Generated {len(new_questions)} questions, {testosterone_count} testosterone")
        return report

    def _log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(PREFRONTAL_L, "a") as f:
            f.write(f"[{timestamp}] {msg}\n")


if __name__ == "__main__":
    prefrontal = PrefrontalCortex()
    report     = prefrontal.think(verbose=True)
