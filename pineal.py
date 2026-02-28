#!/usr/bin/env python3
import json, sys, time
from pathlib import Path
from datetime import datetime

HOME        = Path("/data/data/com.termux/files/home")
SWARM       = HOME / "swarm-platform"
NEURAL_DIR  = SWARM / "neural"
RHYTHM_FILE = NEURAL_DIR / "pineal_rhythm.json"
PINEAL_LOG  = NEURAL_DIR / "pineal.log"
NEURAL_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SWARM))
from hormone_bus import HormoneBus, OrganismState

RHYTHM_CYCLES = {
    "sprint":    {"duration_gens": 500, "mutation_rate": 0.7, "tournament_size": 10, "crossover_rate": 0.9,  "description": "Intense evolution", "next_phase": "harvest"},
    "harvest":   {"duration_gens": 50,  "mutation_rate": 0.3, "tournament_size": 20, "crossover_rate": 0.6,  "description": "Score everything built", "next_phase": "rest"},
    "rest":      {"duration_gens": 100, "mutation_rate": 0.1, "tournament_size": 5,  "crossover_rate": 0.4,  "description": "Consolidate gains", "next_phase": "awaken"},
    "awaken":    {"duration_gens": 30,  "mutation_rate": 0.9, "tournament_size": 3,  "crossover_rate": 0.95, "description": "Fresh cycle", "next_phase": "sprint"},
    "emergency": {"duration_gens": 100, "mutation_rate": 1.0, "tournament_size": 3,  "crossover_rate": 0.95, "description": "Stagnation recovery", "next_phase": "sprint"},
}
STAGNATION_THRESHOLD = 30
IMPROVEMENT_MIN = 2.0

class PinealGland:
    def __init__(self):
        self.bus = HormoneBus()
        self.state = OrganismState()
        self.rhythm = self._load()
        self._log("Pineal initialized")

    def _load(self):
        if RHYTHM_FILE.exists():
            try: return json.loads(RHYTHM_FILE.read_text())
            except: pass
        return {"current_phase": "sprint", "phase_generation": 0, "total_generation": 0,
                "last_best_score": 574.0, "stagnation_counter": 0, "rest_cycles_done": 0,
                "phase_history": [], "score_history": []}

    def _save(self):
        RHYTHM_FILE.write_text(json.dumps(self.rhythm, indent=2))

    def tick(self, current_best_score=None, verbose=True):
        if verbose:
            print("\n╔══════════════════════════════════════════════════════╗")
            print("║  PINEAL GLAND — SETTING RHYTHM                        ║")
            print("╚══════════════════════════════════════════════════════╝\n")

        if current_best_score is None:
            current_best_score = self.state.avg_score

        self.rhythm["score_history"].append({"score": current_best_score, "gen": self.rhythm["total_generation"], "timestamp": datetime.now().isoformat()})
        self.rhythm["score_history"] = self.rhythm["score_history"][-200:]

        delta = current_best_score - self.rhythm["last_best_score"]
        if delta >= IMPROVEMENT_MIN:
            self.rhythm["stagnation_counter"] = 0
            self.rhythm["last_best_score"] = current_best_score
        else:
            self.rhythm["stagnation_counter"] += 1

        stagnation = self.rhythm["stagnation_counter"]
        phase      = self.rhythm["current_phase"]
        phase_gen  = self.rhythm["phase_generation"]
        phase_def  = RHYTHM_CYCLES[phase]

        if stagnation >= STAGNATION_THRESHOLD and phase != "emergency":
            phase = "emergency"
            self.rhythm["current_phase"] = phase
            self.rhythm["phase_generation"] = 0
            self.rhythm["stagnation_counter"] = 0
            phase_def = RHYTHM_CYCLES[phase]
            self.bus.emit("adrenaline", source="pineal", intensity=1.0,
                context={"stagnation_gens": stagnation, "last_score": current_best_score, "action": "Emergency — inject maximum diversity"})
            if verbose: print(f"  ⚡ EMERGENCY — {stagnation} gens stagnant")

        elif phase_gen >= phase_def["duration_gens"]:
            old_phase = phase
            phase = phase_def["next_phase"]
            self.rhythm["current_phase"] = phase
            self.rhythm["phase_generation"] = 0
            phase_def = RHYTHM_CYCLES[phase]
            self.rhythm["phase_history"].append({"from": old_phase, "to": phase, "gen": self.rhythm["total_generation"], "timestamp": datetime.now().isoformat()})
            if verbose: print(f"  🔄 Phase transition: {old_phase} → {phase}")
            if phase == "rest":
                self.rhythm["rest_cycles_done"] += 1
                self.bus.emit("melatonin", source="pineal", intensity=0.8,
                    context={"rest_cycle": self.rhythm["rest_cycles_done"], "score": current_best_score, "action": "Consolidate — write to long-term memory"})
                if verbose: print(f"  🔵 Melatonin fired — entering rest cycle")

        self.rhythm["phase_generation"] += 1
        self.rhythm["total_generation"] += 1

        serotonin = self.bus.read("pineal", "serotonin")
        cortisol  = self.bus.read("pineal", "cortisol")

        params = {"mutation_rate": phase_def["mutation_rate"], "tournament_size": phase_def["tournament_size"],
                  "crossover_rate": phase_def["crossover_rate"], "phase": phase, "description": phase_def["description"],
                  "phase_gen": self.rhythm["phase_generation"], "total_gen": self.rhythm["total_generation"],
                  "stagnation": stagnation, "next_phase": phase_def["next_phase"],
                  "gens_until_next": max(0, phase_def["duration_gens"] - phase_gen)}

        if serotonin:
            top = max(serotonin, key=lambda s: s.intensity)
            params["mutation_rate"] = max(0.1, params["mutation_rate"] * (1.0 - top.intensity * 0.2))
            if verbose: print(f"  🟢 Serotonin — mutation rate reduced to {params['mutation_rate']:.2f}")

        if cortisol and phase == "rest":
            params["mutation_rate"] = 0.6
            params["tournament_size"] = 8
            if verbose: print(f"  🔴 Cortisol override — no rest, pain requires action")

        self.state.update(phase=phase, evolution_rate=params["mutation_rate"])
        self._save()

        if verbose:
            icons = {"sprint": "🏃", "harvest": "🌾", "rest": "🌙", "awaken": "☀️", "emergency": "⚡"}
            print(f"\n  Phase:     {icons.get(phase,"❓")} {phase.upper()}")
            print(f"  Phase gen: {self.rhythm['phase_generation']}")
            print(f"  Total gen: {self.rhythm['total_generation']}")
            print(f"  Stagnation:{stagnation} gens")
            print(f"  mutation_rate:   {params['mutation_rate']:.2f}")
            print(f"  tournament_size: {params['tournament_size']}")
            print(f"  Next phase in:   {params['gens_until_next']} gens")
            print(f"\n  Next: python3 ~/swarm-platform/pituitary.py")

        self._log(f"phase={phase} gen={self.rhythm['total_generation']} stagnation={stagnation}")
        return params

    def get_evolution_params(self):
        phase = self.rhythm.get("current_phase", "sprint")
        d = RHYTHM_CYCLES.get(phase, RHYTHM_CYCLES["sprint"])
        return {"mutation_rate": d["mutation_rate"], "tournament_size": d["tournament_size"], "crossover_rate": d["crossover_rate"], "phase": phase}

    def _log(self, msg):
        with open(PINEAL_LOG, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

if __name__ == "__main__":
    pineal = PinealGland()
    params = pineal.tick(current_best_score=574, verbose=True)
