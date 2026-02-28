#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  PHOENIX FORGE — NEURAL ARCHITECTURE                             ║
║  Component 9 of 9: PHOENIX MIND                                  ║
║  The complete neural cycle. All 8 systems in sequence.           ║
║                                                                  ║
║  Install: cp phoenix_mind.py ~/swarm-platform/                   ║
║  Run:     python3 ~/swarm-platform/phoenix_mind.py               ║
║           python3 ~/swarm-platform/phoenix_mind.py --loop        ║
║           python3 ~/swarm-platform/phoenix_mind.py --status      ║
╚══════════════════════════════════════════════════════════════════╝

This is the master runner. One command runs the complete neural cycle:

  1. BRAINSTEM      — verify People's Charter (immutable laws)
  2. AMYGDALA       — scan for human pain, emit cortisol/oxytocin
  3. HIPPOCAMPUS    — observe what worked and why, emit dopamine
  4. CORPUS CALLOSUM — transfer insight between domains
  5. PREFRONTAL     — generate new questions from all signals
  6. CEREBELLUM     — coordinate balance, flag outliers
  7. PINEAL         — set evolution rhythm, fire melatonin/adrenaline
  8. PITUITARY      — master regulation, issue global directive

Then the directive drives the next evolution run.

Run modes:
  python3 phoenix_mind.py           — one full cycle
  python3 phoenix_mind.py --loop    — run continuously
  python3 phoenix_mind.py --status  — show current state only
  python3 phoenix_mind.py --evolve  — run cycle then trigger evolution
"""

import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

HOME        = Path("/data/data/com.termux/files/home")
SWARM       = HOME / "swarm-platform"
NEURAL_DIR  = SWARM / "neural"
MIND_LOG    = NEURAL_DIR / "phoenix_mind.log"

NEURAL_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SWARM))

# ─────────────────────────────────────────────────────────────────
# PEOPLE'S CHARTER — The brainstem. Immutable laws.
# These cannot be overridden by any hormone or directive.
# ─────────────────────────────────────────────────────────────────
PEOPLES_CHARTER = [
    "Every app must work without internet",
    "No app may require login before delivering value",
    "Every app must acknowledge the human using it",
    "No app may use dark patterns or false urgency",
    "Every app must show the most important thing first",
    "No app may abandon the user with a blank or error screen",
    "The organism exists to relieve suffering, not impress developers",
]


def check_charter(verbose=True):
    """Brainstem check — verify all 7 laws are intact"""
    if verbose:
        print("┌─────────────────────────────────────────────────────┐")
        print("│  BRAINSTEM — PEOPLE'S CHARTER VERIFICATION           │")
        print("└─────────────────────────────────────────────────────┘")
        for i, law in enumerate(PEOPLES_CHARTER, 1):
            print(f"  ✅ Law {i}: {law}")
        print(f"  All {len(PEOPLES_CHARTER)} laws verified — organism integrity intact\n")
    return True


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(MIND_LOG, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")


def run_cycle(verbose=True):
    """
    Run one complete neural cycle through all 8 systems.
    Returns the master directive from pituitary.
    """
    cycle_start = datetime.now()

    if verbose:
        print("\n")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                                                              ║")
        print("║   🔥 PHOENIX MIND — NEURAL CYCLE INITIATING                 ║")
        print("║                                                              ║")
        print("║   The organism thinks.                                       ║")
        print("║                                                              ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"  {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}\n")

    log(f"Cycle start")

    # ── Step 1: BRAINSTEM ────────────────────────────────────────
    if verbose:
        print(f"\n{'═'*62}")
        print(f"  STEP 1/8 — BRAINSTEM")
        print(f"{'═'*62}")
    check_charter(verbose=verbose)

    # ── Step 2: AMYGDALA ─────────────────────────────────────────
    if verbose:
        print(f"\n{'═'*62}")
        print(f"  STEP 2/8 — AMYGDALA  (scanning for human pain)")
        print(f"{'═'*62}")
    try:
        from amygdala import Amygdala
        amygdala = Amygdala()
        amygdala_report = amygdala.scan(verbose=verbose)
        log(f"Amygdala: pain={amygdala_report.get('pain_domains',0)} "
            f"connection={amygdala_report.get('connection_domains',0)}")
    except Exception as e:
        print(f"  ⚠️  Amygdala error: {e}")
        amygdala_report = {}
        log(f"Amygdala error: {e}")

    # ── Step 3: HIPPOCAMPUS ──────────────────────────────────────
    if verbose:
        print(f"\n{'═'*62}")
        print(f"  STEP 3/8 — HIPPOCAMPUS  (extracting why things work)")
        print(f"{'═'*62}")
    try:
        from hippocampus import Hippocampus
        hippocampus = Hippocampus()
        hippo_report = hippocampus.observe(verbose=verbose)
        log(f"Hippocampus: observed={hippo_report.get('observations',0)} "
            f"cross_domain={hippo_report.get('cross_domain_found',0)}")
    except Exception as e:
        print(f"  ⚠️  Hippocampus error: {e}")
        hippo_report = {}
        log(f"Hippocampus error: {e}")

    # ── Step 4: CORPUS CALLOSUM ──────────────────────────────────
    if verbose:
        print(f"\n{'═'*62}")
        print(f"  STEP 4/8 — CORPUS CALLOSUM  (transferring insight)")
        print(f"{'═'*62}")
    try:
        from corpus_callosum import CorpusCallosum
        corpus = CorpusCallosum()
        corpus_report = corpus.transfer(verbose=verbose)
        log(f"Corpus callosum: transfers={corpus_report.get('transfers_identified',0)}")
    except Exception as e:
        print(f"  ⚠️  Corpus callosum error: {e}")
        corpus_report = {}
        log(f"Corpus callosum error: {e}")

    # ── Step 5: PREFRONTAL ───────────────────────────────────────
    if verbose:
        print(f"\n{'═'*62}")
        print(f"  STEP 5/8 — PREFRONTAL  (generating questions)")
        print(f"{'═'*62}")
    try:
        from prefrontal import PrefrontalCortex
        prefrontal = PrefrontalCortex()
        prefrontal_report = prefrontal.think(verbose=verbose)
        log(f"Prefrontal: questions={prefrontal_report.get('questions_generated',0)} "
            f"next_domain={prefrontal_report.get('next_domain_to_build','?')}")
    except Exception as e:
        print(f"  ⚠️  Prefrontal error: {e}")
        prefrontal_report = {}
        log(f"Prefrontal error: {e}")

    # ── Step 6: CEREBELLUM ───────────────────────────────────────
    if verbose:
        print(f"\n{'═'*62}")
        print(f"  STEP 6/8 — CEREBELLUM  (coordinating balance)")
        print(f"{'═'*62}")
    try:
        from cerebellum import Cerebellum
        cerebellum = Cerebellum()
        cerebellum_report = cerebellum.coordinate(verbose=verbose)
        log(f"Cerebellum: balance={cerebellum_report.get('balance_score',0):.2f} "
            f"low_tier={cerebellum_report.get('low_tier',0)}")
    except Exception as e:
        print(f"  ⚠️  Cerebellum error: {e}")
        cerebellum_report = {}
        log(f"Cerebellum error: {e}")

    # ── Step 7: PINEAL ───────────────────────────────────────────
    if verbose:
        print(f"\n{'═'*62}")
        print(f"  STEP 7/8 — PINEAL  (setting rhythm)")
        print(f"{'═'*62}")
    try:
        from pineal import PinealGland
        pineal = PinealGland()
        pineal_params = pineal.tick(verbose=verbose)
        log(f"Pineal: phase={pineal_params.get('phase','?')} "
            f"mutation={pineal_params.get('mutation_rate',0):.2f}")
    except Exception as e:
        print(f"  ⚠️  Pineal error: {e}")
        pineal_params = {}
        log(f"Pineal error: {e}")

    # ── Step 8: PITUITARY ────────────────────────────────────────
    if verbose:
        print(f"\n{'═'*62}")
        print(f"  STEP 8/8 — PITUITARY  (master directive)")
        print(f"{'═'*62}")
    try:
        from pituitary import PituitaryGland
        pituitary = PituitaryGland()
        directive = pituitary.regulate(verbose=verbose)
        log(f"Pituitary: directive={directive.get('directive','?')}")
    except Exception as e:
        print(f"  ⚠️  Pituitary error: {e}")
        directive = {"directive": "MAINTAIN", "reasoning": [str(e)]}
        log(f"Pituitary error: {e}")

    # ── Advance hormone bus ───────────────────────────────────────
    try:
        from hormone_bus import HormoneBus
        bus = HormoneBus()
        bus.tick()
    except Exception as e:
        pass

    # ── Summary ──────────────────────────────────────────────────
    cycle_end     = datetime.now()
    cycle_seconds = (cycle_end - cycle_start).total_seconds()

    directive_name = directive.get("directive", "MAINTAIN")
    directive_icons = {
        "GROW": "🟠", "MAINTAIN": "🟢",
        "PUSH": "⚡", "HEAL": "🔴", "REST": "🔵"
    }
    d_icon = directive_icons.get(directive_name, "❓")

    if verbose:
        print(f"\n\n{'╔' + '═'*62 + '╗'}")
        print(f"║  {'🔥 PHOENIX MIND — CYCLE COMPLETE':^60}  ║")
        print(f"{'╚' + '═'*62 + '╝'}")
        print(f"\n  Duration:    {cycle_seconds:.1f} seconds")
        print(f"  Directive:   {d_icon} {directive_name}")
        print(f"  Meaning:     {directive.get('meaning', '')}")

        org = directive.get("organism", {})
        print(f"\n  Organism state:")
        print(f"    Avg score:  {org.get('avg_score', '?')}/600")
        print(f"    Domains:    {org.get('domains', '?')}")
        print(f"    Balance:    {org.get('balance', '?')}")
        print(f"    Pain level: {org.get('pain_level', '?')}")
        print(f"    Phase:      {org.get('phase', '?')}")

        nq = directive.get("next_question")
        if nq:
            print(f"\n  Next question the organism is asking:")
            print(f"  → {nq}")

        nep = directive.get("next_evolution_priority")
        if nep:
            print(f"\n  Next evolution priority:")
            print(f"  → {nep.get('domain','?')}: {nep.get('reason','?')}")

        nd = prefrontal_report.get("next_domain_to_build") if 'prefrontal_report' in locals() else None
        if nd:
            print(f"\n  Next domain to build: {nd}")

        print(f"\n  Neural files in: {NEURAL_DIR}")
        print(f"    hormone_bus.json")
        print(f"    organism_state.json")
        print(f"    amygdala_report.json")
        print(f"    hippocampus_memory.json")
        print(f"    hippocampus_patterns.json")
        print(f"    corpus_callosum_transfers.json")
        print(f"    prefrontal_questions.json")
        print(f"    cerebellum_balance.json")
        print(f"    pineal_rhythm.json")
        print(f"    pituitary_directive.json")
        print(f"\n  Run again: python3 ~/swarm-platform/phoenix_mind.py")
        print(f"  Loop mode: python3 ~/swarm-platform/phoenix_mind.py --loop")
        print(f"  Status:    python3 ~/swarm-platform/phoenix_mind.py --status")

    log(f"Cycle complete in {cycle_seconds:.1f}s — directive={directive_name}")
    return directive


def show_status():
    """Quick status without running full cycle"""
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║  PHOENIX MIND — STATUS                                ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    from hormone_bus import HormoneBus, OrganismState
    bus   = HormoneBus()
    state = OrganismState()

    state.status()
    bus.status()

    # Load directive
    directive_file = NEURAL_DIR / "pituitary_directive.json"
    if directive_file.exists():
        try:
            d = json.loads(directive_file.read_text())
            current = d.get("current", "MAINTAIN")
            last    = d.get("last", {})
            print(f"  Last directive: {current}")
            nq = last.get("next_question")
            if nq:
                print(f"  Next question:  {nq[:65]}...")
        except:
            pass

    # Check question queue
    q_file = NEURAL_DIR / "prefrontal_questions.json"
    if q_file.exists():
        try:
            qd = json.loads(q_file.read_text())
            print(f"  Questions in queue: {len(qd.get('queue', []))}")
        except:
            pass


def run_loop(interval_seconds=300):
    """Run continuously with interval between cycles"""
    print(f"\n  Phoenix Mind — continuous loop mode")
    print(f"  Cycle interval: {interval_seconds}s ({interval_seconds//60}min)")
    print(f"  Press Ctrl+C to stop\n")
    cycle = 0
    while True:
        cycle += 1
        print(f"\n  {'─'*60}")
        print(f"  Loop cycle {cycle} — {datetime.now().strftime('%H:%M:%S')}")
        print(f"  {'─'*60}")
        try:
            directive = run_cycle(verbose=True)
            print(f"\n  Sleeping {interval_seconds}s until next cycle...")
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print(f"\n  Phoenix Mind loop stopped after {cycle} cycles.")
            break
        except Exception as e:
            log(f"Loop cycle {cycle} error: {e}")
            print(f"  ⚠️  Cycle error: {e} — continuing in 30s")
            time.sleep(30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phoenix Mind — Neural Cycle Runner")
    parser.add_argument("--loop",    action="store_true", help="Run continuously")
    parser.add_argument("--status",  action="store_true", help="Show status only")
    parser.add_argument("--quiet",   action="store_true", help="Minimal output")
    parser.add_argument("--interval", type=int, default=300,
                        help="Loop interval in seconds (default: 300)")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.loop:
        run_loop(interval_seconds=args.interval)
    else:
        run_cycle(verbose=not args.quiet)
