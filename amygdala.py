#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  PHOENIX FORGE — NEURAL ARCHITECTURE                             ║
║  Component 2 of 9: AMYGDALA                                      ║
║  Detects human pain. Weights what matters. Fires urgency.        ║
║                                                                  ║
║  Install: cp amygdala.py ~/swarm-platform/                       ║
║  Run:     python3 ~/swarm-platform/amygdala.py                   ║
║  Requires: hormone_bus.py already installed                      ║
╚══════════════════════════════════════════════════════════════════╝

The amygdala is the emotional core. It reads app scores and human
signals, detects where real pain exists, and fires cortisol (urgency)
or oxytocin (deep connection found) onto the hormone bus.

Without the amygdala, the system optimizes metrics.
With it, the system feels what matters.

Emits:
  Cortisol  — when human pain is unaddressed (score < threshold)
  Oxytocin  — when deep human connection pattern is found
  
Reads:
  Champion scores, human_score breakdowns, wisdom breakdowns
  Looks for: fear, friction, abandonment, confusion, loneliness
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
# ABSOLUTE PATHS
# ─────────────────────────────────────────────────────────────────
HOME         = Path("/data/data/com.termux/files/home")
SWARM        = HOME / "swarm-platform"
NEURAL_DIR   = SWARM / "neural"
CHAMPIONS    = HOME / "ORGANISM_ARMY/champions"
FEDERATION   = SWARM / "federation"
AMYGDALA_LOG = NEURAL_DIR / "amygdala.log"

NEURAL_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SWARM))

from hormone_bus import HormoneBus, OrganismState

# ─────────────────────────────────────────────────────────────────
# PAIN SIGNATURES — what the amygdala looks for
# These are patterns that signal human suffering in an app
# ─────────────────────────────────────────────────────────────────
PAIN_SIGNATURES = {
    "fear_barrier": {
        "description": "Login wall blocks user before any value delivered",
        "signals":     ["login-screen", "must login", "create account first"],
        "pain_weight": 0.9,
        "emotion":     "fear — I don't know if I can trust this",
    },
    "abandonment": {
        "description": "No empty state — app shows nothing when there's no data",
        "signals":     ["undefined", "null", "NaN", "cannot read"],
        "pain_weight": 0.8,
        "emotion":     "abandonment — the app left me alone with an error",
    },
    "confusion": {
        "description": "Technical jargon in user-facing copy",
        "signals":     ["boolean", "null value", "undefined", "crud", "entity id"],
        "pain_weight": 0.7,
        "emotion":     "confusion — I don't understand what this wants from me",
    },
    "friction": {
        "description": "Too many required fields before user can act",
        "signals":     ["required", "must fill", "cannot be empty", "invalid input"],
        "pain_weight": 0.75,
        "emotion":     "friction — this is harder than it needs to be",
    },
    "invisibility": {
        "description": "App doesn't acknowledge the person using it",
        "signals_absent": ["welcome", "hello", "hi ", "good morning", "good afternoon"],
        "pain_weight": 0.6,
        "emotion":     "invisibility — the app doesn't know I exist",
    },
    "isolation": {
        "description": "No offline support — app fails without internet",
        "signals_absent": ["localstorage", "offline", "cache"],
        "pain_weight": 0.85,
        "emotion":     "isolation — the app abandoned me when I lost connection",
    },
}

# ─────────────────────────────────────────────────────────────────
# CONNECTION SIGNATURES — what triggers oxytocin
# These are patterns that signal genuine human connection
# ─────────────────────────────────────────────────────────────────
CONNECTION_SIGNATURES = {
    "immediate_relief": {
        "description": "First screen shows what matters most right now",
        "signals":     ["today", "right now", "most important", "next appointment"],
        "connection_weight": 0.9,
        "feeling":     "relief — it knew what I needed before I asked",
    },
    "forgiveness": {
        "description": "Easy to undo mistakes",
        "signals":     ["undo", "edit", "cancel", "go back", "delete"],
        "connection_weight": 0.7,
        "feeling":     "safety — it won't punish me for trying",
    },
    "dignity": {
        "description": "Plain human language throughout",
        "signals":     ["you", "your", "we", "let's", "here's"],
        "connection_weight": 0.8,
        "feeling":     "dignity — it speaks to me like a person",
    },
    "presence": {
        "description": "App knows what day/time/context it is",
        "signals":     ["today", "this week", "upcoming", "recent", "now"],
        "connection_weight": 0.75,
        "feeling":     "presence — it's here with me, not in a vacuum",
    },
}

# ─────────────────────────────────────────────────────────────────
# DOMAIN PAIN PROFILES — known suffering per domain
# What is the worst moment for a user of this app?
# ─────────────────────────────────────────────────────────────────
DOMAIN_PAIN_PROFILES = {
    "law": {
        "worst_moment": "Client calls in crisis — can't find their file fast enough",
        "fear":         "Missing a deadline that destroys someone's case",
        "relief":       "Everything surfaced, nothing hidden, one tap to respond",
        "pain_threshold": 470,
    },
    "healthcare": {
        "worst_moment": "Patient arrives, system is down or slow",
        "fear":         "Wrong medication, wrong patient, wrong dose",
        "relief":       "Patient name, condition, and next step visible immediately",
        "pain_threshold": 480,
    },
    "mental_health": {
        "worst_moment": "Client in crisis, therapist can't access their notes",
        "fear":         "Missing warning signs that were in the record",
        "relief":       "Full history, current risk level, last session — one screen",
        "pain_threshold": 490,
    },
    "daycare": {
        "worst_moment": "Parent at pickup — can't find child's daily report",
        "fear":         "Did something happen today? Why won't anyone tell me?",
        "relief":       "Parent opens app, sees child's day at a glance",
        "pain_threshold": 480,
    },
    "domestic_violence_shelter": {
        "worst_moment": "Person arrives in crisis, no time for onboarding",
        "fear":         "System asks for information they don't have / aren't safe to give",
        "relief":       "Immediate help, no login, no questions that can wait",
        "pain_threshold": 500,
    },
    "homeless_services": {
        "worst_moment": "Person needs shelter tonight — app requires registration",
        "fear":         "Turned away because of a form",
        "relief":       "Available beds, directions, open now — no barrier",
        "pain_threshold": 500,
    },
    "addiction_recovery": {
        "worst_moment": "3am craving — person alone, about to relapse",
        "fear":         "No one to call, no resource visible, darkness wins",
        "relief":       "Immediate human connection or grounding exercise — one tap",
        "pain_threshold": 495,
    },
    "rural_health_clinic": {
        "worst_moment": "Patient drove 40 miles, doctor running late, no communication",
        "fear":         "Wasted the trip, took the day off work for nothing",
        "relief":       "Real-time wait time, ability to reschedule, clear communication",
        "pain_threshold": 480,
    },
}

DEFAULT_PAIN_THRESHOLD = 460

# ─────────────────────────────────────────────────────────────────
# AMYGDALA
# ─────────────────────────────────────────────────────────────────
class Amygdala:
    def __init__(self):
        self.bus   = HormoneBus()
        self.state = OrganismState()
        self._log("Amygdala initialized")

    def scan(self, verbose=True):
        """
        Scan all champions for pain signals and connection signals.
        Emits cortisol for pain, oxytocin for deep connection.
        Returns full emotional report.
        """
        if verbose:
            print("╔══════════════════════════════════════════════════════╗")
            print("║  AMYGDALA — SCANNING FOR HUMAN PAIN                  ║")
            print("╚══════════════════════════════════════════════════════╝\n")

        pain_found    = []
        connection_found = []
        total_pain    = 0.0
        total_connection = 0.0

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

            # Load champion score
            total_score = 574  # default avg
            if champ_file.exists():
                try:
                    champ = json.loads(champ_file.read_text())
                    total_score = champ.get("total_score", 574)
                except:
                    pass

            # Get domain pain profile
            profile   = DOMAIN_PAIN_PROFILES.get(domain_id, {})
            threshold = profile.get("pain_threshold", DEFAULT_PAIN_THRESHOLD)

            # Scan for pain signatures
            domain_pain = 0.0
            pain_signals = []
            for sig_name, sig in PAIN_SIGNATURES.items():
                detected = False
                if "signals" in sig:
                    detected = any(s in html_lower for s in sig["signals"])
                elif "signals_absent" in sig:
                    detected = not any(s in html_lower for s in sig["signals_absent"])

                if detected:
                    domain_pain += sig["pain_weight"]
                    pain_signals.append({
                        "signature": sig_name,
                        "emotion":   sig["emotion"],
                        "weight":    sig["pain_weight"],
                    })

            # Normalize pain 0-1
            domain_pain = min(1.0, domain_pain / len(PAIN_SIGNATURES))

            # Scan for connection signatures
            domain_connection = 0.0
            conn_signals = []
            for sig_name, sig in CONNECTION_SIGNATURES.items():
                if any(s in html_lower for s in sig["signals"]):
                    domain_connection += sig["connection_weight"]
                    conn_signals.append({
                        "signature": sig_name,
                        "feeling":   sig["feeling"],
                        "weight":    sig["connection_weight"],
                    })
            domain_connection = min(1.0, domain_connection / len(CONNECTION_SIGNATURES))

            total_pain       += domain_pain
            total_connection += domain_connection

            # Score below threshold = pain
            score_pain = max(0, (threshold - total_score) / threshold)
            combined_pain = (domain_pain * 0.6 + score_pain * 0.4)

            if verbose and (combined_pain > 0.3 or domain_connection > 0.6):
                pain_bar = "🔴" * int(combined_pain * 5)
                conn_bar = "💗" * int(domain_connection * 5)
                print(f"  {domain_id:25} score={total_score} "
                      f"pain={combined_pain:.2f} {pain_bar} "
                      f"conn={domain_connection:.2f} {conn_bar}")
                if profile.get("worst_moment"):
                    print(f"    Worst moment: {profile['worst_moment']}")
                if pain_signals:
                    for ps in pain_signals[:2]:
                        print(f"    ⚠️  {ps['emotion']}")
                if conn_signals:
                    for cs in conn_signals[:1]:
                        print(f"    💗 {cs['feeling']}")

            if combined_pain > 0.4:
                pain_found.append({
                    "domain":      domain_id,
                    "pain_level":  combined_pain,
                    "score":       total_score,
                    "signals":     pain_signals,
                    "worst_moment": profile.get("worst_moment", "Unknown"),
                })

            if domain_connection > 0.6:
                connection_found.append({
                    "domain":      domain_id,
                    "connection":  domain_connection,
                    "score":       total_score,
                    "signals":     conn_signals,
                })

        # Emit hormones based on findings
        avg_pain = total_pain / max(len(list(FEDERATION.iterdir())), 1)
        self.state.update(pain_level=avg_pain)

        # Fire cortisol for top pain domains
        if pain_found:
            top_pain = sorted(pain_found, key=lambda x: -x["pain_level"])[:3]
            for p in top_pain:
                self.bus.emit(
                    "cortisol",
                    source="amygdala",
                    intensity=p["pain_level"],
                    context={
                        "domain":      p["domain"],
                        "pain_level":  p["pain_level"],
                        "score":       p["score"],
                        "worst_moment": p["worst_moment"],
                        "action":      f"Evolve {p['domain']} — address the human pain first",
                    }
                )

        # Fire oxytocin for deep connection patterns
        if connection_found:
            top_conn = sorted(connection_found, key=lambda x: -x["connection"])[:2]
            for c in top_conn:
                self.bus.emit(
                    "oxytocin",
                    source="amygdala",
                    intensity=c["connection"],
                    context={
                        "domain":   c["domain"],
                        "pattern":  c["signals"][0]["signature"] if c["signals"] else "unknown",
                        "feeling":  c["signals"][0]["feeling"] if c["signals"] else "unknown",
                        "insight":  f"{c['domain']} knows how to make people feel safe",
                        "action":   f"Transfer {c['domain']} connection pattern to struggling domains",
                    }
                )

        report = {
            "scanned_at":        datetime.now().isoformat(),
            "domains_scanned":   len(pain_found) + len(connection_found),
            "pain_domains":      len(pain_found),
            "connection_domains": len(connection_found),
            "avg_pain_level":    round(avg_pain, 3),
            "cortisol_fired":    len(pain_found) > 0,
            "oxytocin_fired":    len(connection_found) > 0,
            "top_pain":          pain_found[:5],
            "top_connection":    connection_found[:5],
        }

        # Save report
        report_file = NEURAL_DIR / "amygdala_report.json"
        report_file.write_text(json.dumps(report, indent=2))

        if verbose:
            print(f"\n{'═'*60}")
            print(f"  AMYGDALA SCAN COMPLETE")
            print(f"{'═'*60}")
            print(f"  Pain domains:       {len(pain_found)}")
            print(f"  Connection domains: {len(connection_found)}")
            print(f"  Avg pain level:     {avg_pain:.3f}")
            print(f"  Cortisol fired:     {'YES 🔴' if pain_found else 'no'}")
            print(f"  Oxytocin fired:     {'YES 💗' if connection_found else 'no'}")
            print(f"\n  Bus status after scan:")
            self.bus.status()

        self._log(f"Scan complete — pain={len(pain_found)} conn={len(connection_found)}")
        return report

    def _log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(AMYGDALA_LOG, "a") as f:
            f.write(f"[{timestamp}] {msg}\n")


# ─────────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    amygdala = Amygdala()
    report   = amygdala.scan(verbose=True)

    print(f"\n  Files written:")
    print(f"  Amygdala report: {NEURAL_DIR}/amygdala_report.json")
    print(f"  Amygdala log:    {AMYGDALA_LOG}")
    print(f"\n  Next: python3 ~/swarm-platform/hippocampus.py")
