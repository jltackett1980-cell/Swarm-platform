#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  PHOENIX FORGE — NEURAL ARCHITECTURE                             ║
║  Component 3 of 9: HIPPOCAMPUS                                   ║
║  Long-term memory. Stores WHY things worked, not just scores.    ║
║                                                                  ║
║  Install: cp hippocampus.py ~/swarm-platform/                    ║
║  Run:     python3 ~/swarm-platform/hippocampus.py                ║
║  Requires: hormone_bus.py, amygdala.py installed                 ║
╚══════════════════════════════════════════════════════════════════╝

The hippocampus converts short-term observations into long-term patterns.
Every time an app scores high, the hippocampus asks WHY and stores it.
Every time an app fails, it stores what went wrong.

Over time it builds a library of:
  - Patterns that reliably produce high scores
  - Patterns that reliably produce low scores  
  - Cross-domain correlations ("salon's approach works in healthcare too")
  - Evolution of patterns across generations

Emits:
  Dopamine — when a successful pattern is recognized again
  
Reads:
  Cortisol  — stores painful patterns with higher priority
  Melatonin — consolidation cycle, write to long-term memory
"""

import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ─────────────────────────────────────────────────────────────────
# ABSOLUTE PATHS
# ─────────────────────────────────────────────────────────────────
HOME            = Path("/data/data/com.termux/files/home")
SWARM           = HOME / "swarm-platform"
NEURAL_DIR      = SWARM / "neural"
CHAMPIONS       = HOME / "ORGANISM_ARMY/champions"
FEDERATION      = SWARM / "federation"
MEMORY_FILE     = NEURAL_DIR / "hippocampus_memory.json"
PATTERNS_FILE   = NEURAL_DIR / "hippocampus_patterns.json"
HIPPO_LOG       = NEURAL_DIR / "hippocampus.log"

NEURAL_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SWARM))

from hormone_bus import HormoneBus, OrganismState

# ─────────────────────────────────────────────────────────────────
# PATTERN EXTRACTORS
# What the hippocampus looks for to explain WHY a score is high/low
# ─────────────────────────────────────────────────────────────────
PATTERN_EXTRACTORS = {
    # HIGH-SCORE PATTERNS — things that reliably appear in top apps
    "wu_wei_flow": {
        "signals":     ["onclick", "toast", "no appointments yet", "no items yet"],
        "meaning":     "Effortless flow — app gets out of user's way",
        "score_boost": "+25 wisdom (wu_wei)",
        "type":        "positive",
    },
    "offline_first": {
        "signals":     ["localstorage.setitem", "localstorage.getitem", "offline"],
        "meaning":     "Offline-first design — works without internet",
        "score_boost": "+15 human (offline) +5 wisdom (isolation relief)",
        "type":        "positive",
    },
    "human_greeting": {
        "signals":     ["welcome", "good morning", "hello", "hey "],
        "meaning":     "Acknowledges the human using it",
        "score_boost": "+5 human (acknowledges_user)",
        "type":        "positive",
    },
    "today_focus": {
        "signals":     ["today", "this morning", "right now", "current"],
        "meaning":     "Focuses on what matters now, not everything",
        "score_boost": "+10 human (today_focused) +8 wisdom (leads_with_relief)",
        "type":        "positive",
    },
    "domain_color": {
        "signals":     ["#7c3aed", "#2563eb", "#dc2626", "#2d6a4f", "#f59e0b"],
        "meaning":     "Domain-specific color — not generic blue",
        "score_boost": "+10 human (domain_color)",
        "type":        "positive",
    },
    "no_login_wall": {
        "signals_absent": ["login-screen", "must login", "please sign in"],
        "meaning":        "No barrier — value delivered immediately",
        "score_boost":    "+20 human (no_login_wall)",
        "type":           "positive",
    },

    # LOW-SCORE PATTERNS — things that reliably appear in failing apps
    "generic_title": {
        "signals":     ["item management", "record management", "data manager"],
        "meaning":     "Generic naming — not built for real people",
        "score_cost":  "-8 human (generic_title)",
        "type":        "negative",
    },
    "tech_jargon": {
        "signals":     ["boolean", "null", "undefined", "entity", "crud"],
        "meaning":     "Technical language leaking into user interface",
        "score_cost":  "-5 human (human_language)",
        "type":        "negative",
    },
    "no_empty_state": {
        "signals_absent": ["no ", "yet", "empty", "first one", "get started"],
        "meaning":        "No guidance when data is empty",
        "score_cost":     "-10 human (clear_empty_states)",
        "type":           "negative",
    },
    "horizontal_scroll": {
        "signals_absent": ["overflow-x"],
        "meaning":        "No overflow control — may cause horizontal scroll on mobile",
        "score_cost":     "-5 human (no_horizontal_scroll)",
        "type":           "negative",
    },
}


class Hippocampus:
    def __init__(self):
        self.bus      = HormoneBus()
        self.state    = OrganismState()
        self.memory   = self._load_memory()
        self.patterns = self._load_patterns()
        self._log("Hippocampus initialized")

    def _load_memory(self):
        if MEMORY_FILE.exists():
            try:
                return json.loads(MEMORY_FILE.read_text())
            except:
                pass
        return {
            "observations":   [],   # every scored app observation
            "long_term":      {},   # domain -> distilled knowledge
            "cross_domain":   [],   # patterns seen in multiple domains
            "generation":     0,
        }

    def _load_patterns(self):
        if PATTERNS_FILE.exists():
            try:
                return json.loads(PATTERNS_FILE.read_text())
            except:
                pass
        return {
            "positive": {},   # pattern_name -> {count, domains, avg_score_when_present}
            "negative": {},   # pattern_name -> {count, domains, avg_score_when_absent}
            "cross_domain_insights": [],
        }

    def _save(self):
        MEMORY_FILE.write_text(json.dumps(self.memory, indent=2))
        PATTERNS_FILE.write_text(json.dumps(self.patterns, indent=2))

    def observe(self, verbose=True):
        """
        Observe all federation apps. Extract WHY they scored high or low.
        Store observations. Emit dopamine when successful patterns found.
        """
        if verbose:
            print("╔══════════════════════════════════════════════════════╗")
            print("║  HIPPOCAMPUS — EXTRACTING WHY                        ║")
            print("╚══════════════════════════════════════════════════════╝\n")

        observations    = []
        dopamine_count  = 0
        pattern_counts  = defaultdict(lambda: {"count": 0, "domains": [], "scores": []})

        for domain_dir in sorted(FEDERATION.iterdir()):
            if not domain_dir.is_dir():
                continue
            domain_id  = domain_dir.name
            html_file  = domain_dir / "frontend" / "index.html"
            champ_file = CHAMPIONS / domain_id / "champion.json"

            if not html_file.exists():
                continue

            html       = html_file.read_text(errors="ignore")
            html_lower = html.lower()

            # Load scores
            total_score  = 574
            human_score  = 214
            wisdom_score = 85
            tech_score   = 275
            if champ_file.exists():
                try:
                    champ        = json.loads(champ_file.read_text())
                    total_score  = champ.get("total_score", 574)
                    human_score  = champ.get("human_score", 214)
                    wisdom_score = champ.get("wisdom_score", 85)
                    tech_score   = champ.get("score", 275)
                except:
                    pass

            # Extract patterns present in this app
            present_patterns  = []
            absent_patterns   = []

            for pat_name, pat in PATTERN_EXTRACTORS.items():
                if "signals" in pat:
                    found = any(s in html_lower for s in pat["signals"])
                elif "signals_absent" in pat:
                    found = not any(s in html_lower for s in pat["signals_absent"])
                else:
                    found = False

                if found:
                    present_patterns.append(pat_name)
                    pattern_counts[pat_name]["count"] += 1
                    pattern_counts[pat_name]["domains"].append(domain_id)
                    pattern_counts[pat_name]["scores"].append(total_score)
                else:
                    absent_patterns.append(pat_name)

            # Build WHY explanation
            why_high = [p for p in present_patterns
                        if PATTERN_EXTRACTORS[p]["type"] == "positive"]
            why_low  = [p for p in absent_patterns
                        if PATTERN_EXTRACTORS[p]["type"] == "positive"]

            observation = {
                "domain":           domain_id,
                "total_score":      total_score,
                "human_score":      human_score,
                "wisdom_score":     wisdom_score,
                "tech_score":       tech_score,
                "why_high":         why_high,
                "why_low":          why_low,
                "present_patterns": present_patterns,
                "observed_at":      datetime.now().isoformat(),
            }
            observations.append(observation)

            # Emit dopamine when strong positive pattern cluster found
            if len(why_high) >= 4 and total_score >= 580:
                dopamine_count += 1
                self.bus.emit(
                    "dopamine",
                    source="hippocampus",
                    intensity=min(1.0, len(why_high) / 6),
                    context={
                        "domain":       domain_id,
                        "score":        total_score,
                        "why_it_works": why_high,
                        "key_pattern":  why_high[0] if why_high else "unknown",
                        "action":       f"Replicate {domain_id} pattern cluster in lower-scoring domains",
                    }
                )

            if verbose and total_score >= 580:
                print(f"  🧠 {domain_id:25} {total_score}/600")
                for p in why_high[:3]:
                    print(f"    ✅ {p}: {PATTERN_EXTRACTORS[p]['meaning']}")
                if why_low:
                    print(f"    ❓ Missing: {why_low[0]}")

        # Update long-term memory
        self.memory["observations"].extend(observations)
        self.memory["observations"] = self.memory["observations"][-1000:]
        self.memory["generation"]  += 1

        # Distill per-domain knowledge
        for obs in observations:
            domain = obs["domain"]
            if domain not in self.memory["long_term"]:
                self.memory["long_term"][domain] = {
                    "best_score":     0,
                    "best_patterns":  [],
                    "observations":   0,
                    "improvement":    [],
                }
            lt = self.memory["long_term"][domain]
            lt["observations"] += 1
            if obs["total_score"] > lt["best_score"]:
                lt["best_score"]    = obs["total_score"]
                lt["best_patterns"] = obs["why_high"]

        # Find cross-domain patterns (appear in 10+ domains at high scores)
        cross_domain = []
        for pat_name, data in pattern_counts.items():
            if data["count"] >= 10:
                avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
                cross_domain.append({
                    "pattern":    pat_name,
                    "meaning":    PATTERN_EXTRACTORS[pat_name]["meaning"],
                    "domain_count": data["count"],
                    "avg_score":  round(avg_score, 1),
                    "domains":    data["domains"][:5],
                })

        self.memory["cross_domain"] = cross_domain

        # Store pattern stats
        for pat_name, data in pattern_counts.items():
            avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            pat_type = PATTERN_EXTRACTORS[pat_name]["type"]
            self.patterns[pat_type][pat_name] = {
                "count":    data["count"],
                "domains":  data["domains"],
                "avg_score_when_present": round(avg, 1),
                "meaning":  PATTERN_EXTRACTORS[pat_name]["meaning"],
            }

        self._save()

        report = {
            "observations":        len(observations),
            "dopamine_emitted":    dopamine_count,
            "cross_domain_found":  len(cross_domain),
            "long_term_domains":   len(self.memory["long_term"]),
            "top_patterns":        cross_domain[:3],
        }

        if verbose:
            print(f"\n{'═'*60}")
            print(f"  HIPPOCAMPUS COMPLETE")
            print(f"{'═'*60}")
            print(f"  Domains observed:    {len(observations)}")
            print(f"  Dopamine fired:      {dopamine_count}x")
            print(f"  Cross-domain found:  {len(cross_domain)} universal patterns")
            if cross_domain:
                print(f"\n  Universal patterns (in 10+ domains):")
                for cd in cross_domain[:5]:
                    print(f"    🧠 {cd['pattern']:20} "
                          f"domains={cd['domain_count']} "
                          f"avg_score={cd['avg_score']}")
                    print(f"       {cd['meaning']}")
            print(f"\n  Files written:")
            print(f"    {MEMORY_FILE}")
            print(f"    {PATTERNS_FILE}")
            print(f"\n  Next: python3 ~/swarm-platform/corpus_callosum.py")

        self._log(f"Observed {len(observations)} domains, {len(cross_domain)} cross-domain patterns")
        return report

    def recall(self, domain_id):
        """Recall everything known about a domain"""
        lt = self.memory["long_term"].get(domain_id, {})
        recent = [o for o in self.memory["observations"]
                  if o["domain"] == domain_id][-5:]
        return {
            "domain":      domain_id,
            "long_term":   lt,
            "recent":      recent,
            "cross_domain": [cd for cd in self.memory["cross_domain"]
                             if domain_id in cd.get("domains", [])],
        }

    def _log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(HIPPO_LOG, "a") as f:
            f.write(f"[{timestamp}] {msg}\n")


if __name__ == "__main__":
    hippo  = Hippocampus()
    report = hippo.observe(verbose=True)

    print(f"\n  Sample recall for 'salon':")
    recall = hippo.recall("salon")
    print(f"    Best score:    {recall['long_term'].get('best_score', 'unknown')}")
    print(f"    Best patterns: {recall['long_term'].get('best_patterns', [])}")
