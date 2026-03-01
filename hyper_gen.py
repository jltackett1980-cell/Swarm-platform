#!/usr/bin/env python3
"""
PHOENIX HYPER GEN — 50,000 Generation Overnight Run
Runs apps + devices + neural mind simultaneously.
Let it run while you sleep.
"""
import json, subprocess, time, sys
from pathlib import Path
from datetime import datetime

SWARM = Path("/data/data/com.termux/files/home/swarm-platform")
LOG   = SWARM / "hyper_gen.log"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def run_py(script, args=""):
    cmd = f"python3 {SWARM}/{script} {args}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    return result.returncode == 0

def count_devices():
    reg = SWARM / "devices" / "device_registry.json"
    if reg.exists():
        try: return len(json.loads(reg.read_text()))
        except: pass
    return 0

def count_apps():
    fed = SWARM / "federation"
    if fed.exists():
        return len([d for d in fed.iterdir() if d.is_dir()])
    return 0

TOTAL_GENS   = 50000
DEVICE_BATCH = 10   # devices per cycle
MIND_EVERY   = 50   # run phoenix_mind every N cycles

log("╔══════════════════════════════════════════════════════════════╗")
log("║  PHOENIX HYPER GEN — 50,000 GENERATIONS                      ║")
log("╚══════════════════════════════════════════════════════════════╝")
log(f"Starting devices: {count_devices()}")
log(f"Starting apps:    {count_apps()}")
log(f"Target:           {TOTAL_GENS} generations")
log(f"Log:              {LOG}")
log("Running while you sleep. God's got the watch.")
log("")

start_time = time.time()
gen = 0

while gen < TOTAL_GENS:
    try:
        # Device evolution — primary loop
        ok = run_py("device_forge.py", f"--cycles={DEVICE_BATCH}")
        gen += DEVICE_BATCH

        # Neural mind check every 50 cycles
        if gen % MIND_EVERY == 0:
            run_py("phoenix_mind.py")
            elapsed = (time.time() - start_time) / 3600
            devices = count_devices()
            rate = devices / elapsed if elapsed > 0 else 0
            eta_h = (TOTAL_GENS - gen) / DEVICE_BATCH / (60 / 10)
            log(f"Gen {gen:6d}/{TOTAL_GENS} | Devices: {devices:6d} | {rate:.0f}/hr | ETA: {eta_h:.1f}h")

        # Checkpoint every 1000
        if gen % 1000 == 0:
            log(f"CHECKPOINT {gen} — committing to git")
            subprocess.run(f'cd {SWARM} && git add -A && git commit -m "HyperGen checkpoint gen {gen} — {count_devices()} devices"', shell=True, capture_output=True)

        time.sleep(0.1)

    except KeyboardInterrupt:
        log(f"Stopped at gen {gen}")
        break
    except Exception as e:
        log(f"Error at gen {gen}: {e}")
        time.sleep(5)
        continue

elapsed = (time.time() - start_time) / 3600
log("")
log(f"HYPER GEN COMPLETE")
log(f"Generations run:  {gen}")
log(f"Total devices:    {count_devices()}")
log(f"Time elapsed:     {elapsed:.1f} hours")

subprocess.run(f'cd {SWARM} && git add -A && git commit -m "HyperGen complete — {gen} generations — {count_devices()} devices"', shell=True, capture_output=True)
log("Final commit pushed. Phoenix Forge slept well.")
