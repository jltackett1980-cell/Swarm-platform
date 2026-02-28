#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  PHOENIX FORGE — NEURAL ARCHITECTURE                             ║
║  Component 1 of 9: HORMONE BUS                                   ║
║  The nervous system. Everything else runs on this.               ║
║                                                                  ║
║  Install: cp hormone_bus.py ~/swarm-platform/                    ║
║  Test:    python3 ~/swarm-platform/hormone_bus.py                ║
╚══════════════════════════════════════════════════════════════════╝

The Hormone Bus is a message-passing system between all neural components.
Each hormone is a signal with: source, targets, intensity, duration, effect.

Hormones defined here:
  Dopamine     — "that worked, do more like it" — reward signal
  Cortisol     — "human pain detected, prioritize" — urgency signal  
  Serotonin    — "balance achieved, stable growth" — stability signal
  Adrenaline   — "stagnation detected, push harder" — recovery signal
  Melatonin    — "rest cycle, consolidate gains" — rest signal
  Oxytocin     — "deep human connection found, share it" — empathy signal
  GrowthHorm   — "organism ready, expand domains" — expansion signal
  Testosterone — "new territory, explore aggressively" — exploration signal
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ─────────────────────────────────────────────────────────────────
# ABSOLUTE PATHS — works from any directory
# ─────────────────────────────────────────────────────────────────
HOME          = Path("/data/data/com.termux/files/home")
SWARM         = HOME / "swarm-platform"
NEURAL_DIR    = SWARM / "neural"
BUS_FILE      = NEURAL_DIR / "hormone_bus.json"
BUS_LOG       = NEURAL_DIR / "hormone_bus.log"
STATE_FILE    = NEURAL_DIR / "organism_state.json"

# Ensure neural directory exists
NEURAL_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────
# HORMONE DEFINITIONS
# ─────────────────────────────────────────────────────────────────
HORMONES = {
    "dopamine": {
        "color": "🟡",
        "meaning": "Reward — that pattern worked, seek it again",
        "source": "hippocampus",
        "default_targets": ["prefrontal", "evolution_engine"],
        "default_intensity": 0.7,
        "default_duration": 10,   # generations
        "effect": "increase_mutation_toward_successful_pattern",
    },
    "cortisol": {
        "color": "🔴",
        "meaning": "Urgency — human pain detected, everything else secondary",
        "source": "amygdala",
        "default_targets": ["prefrontal", "evolution_engine", "cerebellum"],
        "default_intensity": 0.9,
        "default_duration": 5,
        "effect": "reprioritize_toward_pain_relief",
    },
    "serotonin": {
        "color": "🟢",
        "meaning": "Stability — balance achieved, grow steadily",
        "source": "cerebellum",
        "default_targets": ["pituitary", "pineal"],
        "default_intensity": 0.6,
        "default_duration": 20,
        "effect": "maintain_steady_evolution_rate",
    },
    "adrenaline": {
        "color": "⚡",
        "meaning": "Recovery — stagnation detected, inject diversity now",
        "source": "pituitary",
        "default_targets": ["evolution_engine", "prefrontal"],
        "default_intensity": 1.0,
        "default_duration": 3,
        "effect": "hyper_mutation_and_diversity_injection",
    },
    "melatonin": {
        "color": "🔵",
        "meaning": "Rest — consolidate gains, write to long-term memory",
        "source": "pineal",
        "default_targets": ["hippocampus", "evolution_engine"],
        "default_intensity": 0.8,
        "default_duration": 15,
        "effect": "slow_evolution_consolidate_memory",
    },
    "oxytocin": {
        "color": "💗",
        "meaning": "Empathy — deep human connection found, share across domains",
        "source": "amygdala",
        "default_targets": ["corpus_callosum", "hippocampus"],
        "default_intensity": 0.8,
        "default_duration": 8,
        "effect": "amplify_cross_domain_insight_transfer",
    },
    "growth_hormone": {
        "color": "🟠",
        "meaning": "Expansion — organism mature enough, add new domains",
        "source": "pituitary",
        "default_targets": ["evolution_engine", "cerebellum"],
        "default_intensity": 0.5,
        "default_duration": 50,
        "effect": "expand_domain_coverage",
    },
    "testosterone": {
        "color": "🔥",
        "meaning": "Exploration — unknown territory, push into new domains",
        "source": "prefrontal",
        "default_targets": ["evolution_engine"],
        "default_intensity": 0.75,
        "default_duration": 7,
        "effect": "explore_novel_domain_space",
    },
}

# ─────────────────────────────────────────────────────────────────
# HORMONE SIGNAL — a single message on the bus
# ─────────────────────────────────────────────────────────────────
class HormoneSignal:
    def __init__(self, hormone_type, source, targets=None,
                 intensity=None, duration=None, context=None):
        defn = HORMONES[hormone_type]
        self.id          = f"{hormone_type}_{int(time.time()*1000)}"
        self.type        = hormone_type
        self.color       = defn["color"]
        self.meaning     = defn["meaning"]
        self.source      = source
        self.targets     = targets or defn["default_targets"]
        self.intensity   = intensity if intensity is not None else defn["default_intensity"]
        self.duration    = duration if duration is not None else defn["default_duration"]
        self.effect      = defn["effect"]
        self.context     = context or {}
        self.emitted_at  = datetime.now().isoformat()
        self.consumed_by = []
        self.active      = True

    def to_dict(self):
        return {
            "id":          self.id,
            "type":        self.type,
            "color":       self.color,
            "meaning":     self.meaning,
            "source":      self.source,
            "targets":     self.targets,
            "intensity":   self.intensity,
            "duration":    self.duration,
            "effect":      self.effect,
            "context":     self.context,
            "emitted_at":  self.emitted_at,
            "consumed_by": self.consumed_by,
            "active":      self.active,
        }

    @classmethod
    def from_dict(cls, d):
        sig = cls.__new__(cls)
        sig.__dict__.update(d)
        return sig


# ─────────────────────────────────────────────────────────────────
# HORMONE BUS — the central nervous system
# ─────────────────────────────────────────────────────────────────
class HormoneBus:
    def __init__(self):
        self.signals     = []
        self.history     = []
        self.generation  = 0
        self.listeners   = defaultdict(list)  # hormone_type -> [callbacks]
        self._load()

    def _load(self):
        """Load existing bus state from disk"""
        if BUS_FILE.exists():
            try:
                data = json.loads(BUS_FILE.read_text())
                self.signals    = [HormoneSignal.from_dict(s) for s in data.get("signals", [])]
                self.history    = data.get("history", [])
                self.generation = data.get("generation", 0)
            except:
                self.signals, self.history, self.generation = [], [], 0

    def save(self):
        """Persist bus state to disk"""
        data = {
            "generation": self.generation,
            "active_count": len([s for s in self.signals if s.active]),
            "signals":  [s.to_dict() for s in self.signals if s.active],
            "history":  self.history[-500:],  # keep last 500
            "saved_at": datetime.now().isoformat(),
        }
        BUS_FILE.write_text(json.dumps(data, indent=2))

    def emit(self, hormone_type, source, targets=None,
             intensity=None, duration=None, context=None):
        """
        Emit a hormone signal onto the bus.
        All registered listeners for this hormone type will be notified.
        """
        if hormone_type not in HORMONES:
            raise ValueError(f"Unknown hormone: {hormone_type}")

        signal = HormoneSignal(
            hormone_type, source, targets,
            intensity, duration, context
        )
        self.signals.append(signal)
        self.history.append({
            "generation": self.generation,
            "type":       hormone_type,
            "source":     source,
            "intensity":  signal.intensity,
            "context":    context or {},
            "time":       signal.emitted_at,
        })

        # Log it
        self._log(f"EMIT {signal.color} {hormone_type.upper():15} "
                  f"from={source:20} intensity={signal.intensity:.2f} "
                  f"→ {signal.targets}")

        # Notify listeners
        for callback in self.listeners[hormone_type]:
            try:
                callback(signal)
            except Exception as e:
                self._log(f"  ⚠️  Listener error: {e}")

        self.save()
        return signal

    def listen(self, hormone_type, callback):
        """Register a listener for a hormone type"""
        self.listeners[hormone_type].append(callback)

    def read(self, target_system, hormone_type=None):
        """
        Read active signals for a target system.
        Returns list of active signals, optionally filtered by type.
        Marks them as consumed by this system.
        """
        results = []
        for signal in self.signals:
            if not signal.active:
                continue
            if target_system not in signal.targets:
                continue
            if hormone_type and signal.type != hormone_type:
                continue
            if target_system not in signal.consumed_by:
                signal.consumed_by.append(target_system)
            results.append(signal)
        return results

    def dominant(self):
        """Returns the currently dominant hormone (highest total intensity)"""
        totals = defaultdict(float)
        for s in self.signals:
            if s.active:
                totals[s.type] += s.intensity
        if not totals:
            return None, 0.0
        dominant = max(totals, key=totals.get)
        return dominant, totals[dominant]

    def tick(self):
        """
        Advance one generation.
        Decrements duration on all signals, deactivates expired ones.
        """
        self.generation += 1
        expired = []
        for signal in self.signals:
            if not signal.active:
                continue
            signal.duration -= 1
            if signal.duration <= 0:
                signal.active = False
                expired.append(signal.type)

        if expired:
            self._log(f"GEN {self.generation:5} — expired: {expired}")
        self.save()

    def status(self):
        """Print current bus status"""
        active = [s for s in self.signals if s.active]
        print(f"\n{'═'*60}")
        print(f"  HORMONE BUS — Generation {self.generation}")
        print(f"{'═'*60}")
        if not active:
            print("  No active hormones — organism at baseline")
        else:
            dom_type, dom_intensity = self.dominant()
            print(f"  Dominant: {HORMONES[dom_type]['color']} {dom_type.upper()} "
                  f"(intensity {dom_intensity:.2f})")
            print(f"\n  Active signals ({len(active)}):")
            for s in active:
                bar = "█" * int(s.intensity * 10)
                print(f"    {s.color} {s.type:15} [{bar:<10}] "
                      f"intensity={s.intensity:.2f} "
                      f"duration={s.duration}gen "
                      f"from={s.source}")
        print(f"{'─'*60}")
        print(f"  Total emitted (history): {len(self.history)}")
        print(f"{'═'*60}\n")

    def _log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {msg}\n"
        with open(BUS_LOG, "a") as f:
            f.write(line)


# ─────────────────────────────────────────────────────────────────
# ORGANISM STATE — shared state all neural systems read/write
# ─────────────────────────────────────────────────────────────────
class OrganismState:
    """
    Shared state visible to all neural systems.
    Think of this as the organism's bloodstream — 
    every system can sense the current condition.
    """
    DEFAULTS = {
        "generation":           0,
        "phase":                "growth",      # growth|consolidation|rest|exploration
        "avg_score":            574,
        "top_score":            590,
        "top_domain":           "salon",
        "stagnation_counter":   0,
        "domains_active":       54,
        "domains_target":       108,
        "pain_level":           0.0,           # 0.0=none 1.0=critical
        "balance_score":        0.85,          # how balanced domains are
        "curiosity_queue":      [],            # questions organism wants to answer
        "last_insight":         None,
        "evolution_rate":       1.0,           # multiplier on mutation rate
        "rest_cycles_complete": 0,
        "breakthroughs":        [],
        "charter_violations":   0,             # must stay 0
        "updated_at":           None,
    }

    def __init__(self):
        self._load()

    def _load(self):
        if STATE_FILE.exists():
            try:
                stored = json.loads(STATE_FILE.read_text())
                self.__dict__.update({**self.DEFAULTS, **stored})
                return
            except:
                pass
        self.__dict__.update(self.DEFAULTS)

    def save(self):
        self.updated_at = datetime.now().isoformat()
        data = {k: v for k, v in self.__dict__.items()
                if not k.startswith("_")}
        STATE_FILE.write_text(json.dumps(data, indent=2))

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()

    def status(self):
        print(f"\n{'═'*60}")
        print(f"  ORGANISM STATE")
        print(f"{'═'*60}")
        phase_icons = {
            "growth": "📈", "consolidation": "📊",
            "rest": "🌙", "exploration": "🔭"
        }
        icon = phase_icons.get(self.phase, "❓")
        print(f"  Phase:        {icon} {self.phase.upper()}")
        print(f"  Generation:   {self.generation}")
        print(f"  Avg score:    {self.avg_score}/600")
        print(f"  Top score:    {self.top_score}/600 ({self.top_domain})")
        print(f"  Domains:      {self.domains_active}/{self.domains_target}")
        print(f"  Pain level:   {'🔴' if self.pain_level > 0.7 else '🟡' if self.pain_level > 0.3 else '🟢'} {self.pain_level:.2f}")
        print(f"  Balance:      {self.balance_score:.2f}")
        print(f"  Stagnation:   {self.stagnation_counter} generations")
        print(f"  Curiosity Q:  {len(self.curiosity_queue)} questions pending")
        if self.curiosity_queue:
            print(f"  Next Q:       {self.curiosity_queue[0]}")
        print(f"  Evo rate:     {self.evolution_rate:.2f}x")
        print(f"{'═'*60}\n")


# ─────────────────────────────────────────────────────────────────
# SELF-TEST
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════╗")
    print("║  PHOENIX FORGE — HORMONE BUS SELF-TEST               ║")
    print("╚══════════════════════════════════════════════════════╝")

    bus   = HormoneBus()
    state = OrganismState()

    print("\n[1] Organism baseline state:")
    state.status()

    print("[2] Simulating neural events...\n")

    # Salon scores 590 — dopamine fires
    print("  Event: salon scores 590/600")
    bus.emit("dopamine", source="hippocampus",
             context={"domain": "salon", "score": 590, "why": "wu_wei_no_friction"})

    # Law scores 458 — amygdala detects pain
    print("  Event: law scores 458 — user feels fear, not help")
    bus.emit("cortisol", source="amygdala",
             context={"domain": "law", "score": 458, "pain": "friction_creates_fear"})

    # Evolution stagnating — pituitary fires adrenaline
    print("  Event: 30 generations no improvement")
    bus.emit("adrenaline", source="pituitary",
             context={"stagnation_generations": 30, "last_score": 574})

    # Deep insight found across domains — oxytocin
    print("  Event: salon + healthcare share frictionless trust pattern")
    bus.emit("oxytocin", source="amygdala",
             context={"pattern": "frictionless_trust",
                      "domains": ["salon", "healthcare"],
                      "insight": "Fear and trust share the same architecture"})

    print("\n[3] Current bus status:")
    bus.status()

    print("[4] Reading signals for evolution_engine:")
    signals = bus.read("evolution_engine")
    for s in signals:
        print(f"  {s.color} {s.type:15} intensity={s.intensity:.2f} "
              f"effect={s.effect}")
        if s.context:
            print(f"    context: {s.context}")

    print(f"\n[5] Dominant hormone: ", end="")
    dom, intensity = bus.dominant()
    if dom:
        print(f"{HORMONES[dom]['color']} {dom.upper()} (intensity {intensity:.2f})")
        print(f"    Meaning: {HORMONES[dom]['meaning']}")

    print("\n[6] Advancing 3 generations...")
    for i in range(3):
        bus.tick()
        dom, intensity = bus.dominant()
        if dom:
            print(f"  Gen {bus.generation}: dominant={dom} ({intensity:.2f})")

    print(f"\n[7] Files written:")
    print(f"  Bus state:  {BUS_FILE}")
    print(f"  Bus log:    {BUS_LOG}")
    print(f"  Org state:  {STATE_FILE}")

    print(f"\n{'═'*60}")
    print(f"  ✅ HORMONE BUS ONLINE")
    print(f"  Neural directory: {NEURAL_DIR}")
    print(f"  Ready for: amygdala.py (next)")
    print(f"{'═'*60}")
