#!/usr/bin/env python3
"""
PHOENIX DEVICE FORGE — Autonomous Device Designer
Reads chip architecture + app patterns to design healing devices.
Math must work. Solves real problems. Starts simple, evolves complexity.
"""
import json, math, random, uuid
from datetime import datetime
from pathlib import Path

SWARM   = Path("/data/data/com.termux/files/home/swarm-platform")
NEURAL  = SWARM / "neural"
DEVICES = SWARM / "devices"
NEURAL.mkdir(parents=True, exist_ok=True)
DEVICES.mkdir(parents=True, exist_ok=True)

# Load chip architecture
def load_chip():
    f = SWARM / "chip_evolution_final.json"
    if f.exists():
        try:
            d = json.loads(f.read_text())
            return d.get("final_chip", {})
        except: pass
    return {"matrix_size":131072,"aru_cores":8192,"clock_ghz":20.0,"precision":"optical","interconnect":"neuromorphic","chiplets":256,"edge_deployable":True}

# Load app patterns from hippocampus
def load_app_patterns():
    f = NEURAL / "hippocampus_patterns.json"
    if f.exists():
        try: return json.loads(f.read_text())
        except: pass
    return {}

# Load existing apps from federation
def load_apps():
    apps = []
    fed = SWARM / "federation"
    if fed.exists():
        for d in fed.iterdir():
            champ = d / "node_champion.json"
            if champ.exists():
                try:
                    c = json.loads(champ.read_text())
                    apps.append({"domain":d.name,"name":c.get("name",""),"user":c.get("user",""),"worst_moment":c.get("worst_moment",""),"human_greeting":c.get("human_greeting",""),"wisdom":c.get("wisdom","")})
                except: pass
    return apps

HUMAN_PAIN = [
    {"pain":"chronic_pain","population":50000000,"description":"50M Americans in daily pain with no affordable relief","domain":"chronic_pain"},
    {"pain":"hearing_loss","population":48000000,"description":"48M with hearing loss — aids cost $3,000-$7,000","domain":"healthcare"},
    {"pain":"mobility_impairment","population":26000000,"description":"26M with mobility limitations can't access basic environments","domain":"healthcare"},
    {"pain":"traumatic_brain","population":5300000,"description":"5.3M living with TBI — limited affordable recovery tools","domain":"healthcare"},
    {"pain":"sleep_disorder","population":70000000,"description":"70M with sleep disorders — existing devices expensive or ineffective","domain":"sleep_better"},
    {"pain":"diabetes_monitoring","population":37000000,"description":"37M diabetics need glucose monitoring — devices cost $300+/month","domain":"healthcare"},
    {"pain":"vision_impairment","population":12000000,"description":"12M with vision impairment lack affordable assistive tech","domain":"healthcare"},
    {"pain":"wound_healing","population":8700000,"description":"8.7M with chronic wounds — slow healing costs billions","domain":"healthcare"},
    {"pain":"anxiety_crisis","population":40000000,"description":"40M with anxiety — panic attacks have no real-time wearable intervention","domain":"mental_wellness"},
    {"pain":"ptsd","population":12000000,"description":"12M with PTSD — nightmares disrupt sleep nightly with no passive intervention","domain":"veteran_support"},
    {"pain":"depression","population":21000000,"description":"21M with major depression — no passive monitoring or early warning device","domain":"mental_wellness"},
    {"pain":"addiction_craving","population":21000000,"description":"21M with substance disorders — craving triggers go undetected","domain":"addiction_support"},
    {"pain":"autism_sensory","population":5400000,"description":"5.4M autistic adults — sensory overload has no wearable intervention","domain":"healthcare"},
    {"pain":"paralysis","population":5400000,"description":"5.4M paralyzed — neural interfaces cost $50,000+","domain":"healthcare"},
    {"pain":"limb_loss","population":2100000,"description":"2.1M with limb loss — prosthetics with sensation cost $100,000+","domain":"healthcare"},
    {"pain":"speech_impairment","population":7500000,"description":"7.5M with speech disorders — AAC devices cost $8,000+","domain":"healthcare"},
    {"pain":"tremor","population":10000000,"description":"10M with essential tremor can't hold a pen or eat without spilling","domain":"healthcare"},
    {"pain":"rural_no_doctor","population":60000000,"description":"60M in rural areas — no nearby physician, diagnosis delayed","domain":"telehealth"},
    {"pain":"food_insecurity","population":44000000,"description":"44M food insecure — soil quality unknown to small farmers","domain":"food_stamps_helper"},
    {"pain":"clean_water","population":2200000,"description":"2.2M Americans lack access to safe drinking water","domain":"healthcare"},
    {"pain":"air_quality","population":137000000,"description":"137M in areas with unhealthy air — no affordable personal monitor","domain":"healthcare"},
    {"pain":"domestic_violence","population":10000000,"description":"10M DV victims yearly — no discreet wearable alert system","domain":"domestic_violence_shelter"},
    {"pain":"elderly_fall","population":36000000,"description":"36M elderly fall each year — current alerts require pressing a button","domain":"elder_care"},
    {"pain":"loneliness","population":61000000,"description":"61M with severe loneliness — linked to early death, no device addresses this","domain":"grief_support"},
]

PHYSICS = {
    "electromagnetic":     {"desc":"Pulsed electric/magnetic fields","proven":True,"examples":["TENS units","PEMF therapy","FDA bone healing devices"],"power":(0.001,50),"size":(1,100)},
    "photobiomodulation":  {"desc":"Specific light wavelengths stimulate cell function","proven":True,"examples":["Red light therapy","Laser therapy","SAD lamps"],"power":(0.005,5),"size":(2,30)},
    "acoustic_ultrasound": {"desc":"Sound waves above 20kHz for tissue effects","proven":True,"examples":["Therapeutic ultrasound","HIFU","Lithotripsy"],"power":(0.1,1000),"size":(2,50)},
    "biofeedback_neural":  {"desc":"Reads body signals, responds in real time","proven":True,"examples":["Neurofeedback","Vagus nerve stimulation","Deep brain stimulation"],"power":(0.001,10),"size":(1,20)},
    "mechanical_haptic":   {"desc":"Vibration, pressure, mechanical force","proven":True,"examples":["Haptic feedback","Vibrotactile devices","Exoskeletons"],"power":(0.1,500),"size":(5,200)},
    "electrochemical":     {"desc":"Electrochemical reactions for sensing and delivery","proven":True,"examples":["Continuous glucose monitors","Insulin pumps","Water sensors"],"power":(0.001,20),"size":(1,30)},
    "thermal":             {"desc":"Controlled heat and cold for therapeutic effect","proven":True,"examples":["Targeted thermal therapy","Cryotherapy","Heating pads"],"power":(1,200),"size":(5,50)},
    "magnetic_resonance":  {"desc":"Pulsed magnetic fields stimulate tissue","proven":True,"examples":["rTMS","PEMF","Magnetic bone healing"],"power":(0.001,100),"size":(5,100)},
    "rf_sensing":          {"desc":"Radio frequency for non-contact sensing","proven":True,"examples":["Radar vital signs","Through-wall sensing","Contactless sleep tracking"],"power":(0.001,1),"size":(5,30)},
    "electrostatic":       {"desc":"Static fields for air/water purification and drug delivery","proven":True,"examples":["Air purifiers","Electrospray","Electrostatic wound healing"],"power":(0.001,50),"size":(5,100)},
}

PAIN_PHYSICS = {
    "chronic_pain":       ["electromagnetic","photobiomodulation","magnetic_resonance","acoustic_ultrasound"],
    "hearing_loss":       ["mechanical_haptic","electromagnetic"],
    "mobility_impairment":["mechanical_haptic","biofeedback_neural","electromagnetic"],
    "traumatic_brain":    ["photobiomodulation","biofeedback_neural","electromagnetic"],
    "sleep_disorder":     ["photobiomodulation","biofeedback_neural","rf_sensing"],
    "diabetes_monitoring":["electrochemical","rf_sensing"],
    "vision_impairment":  ["mechanical_haptic","biofeedback_neural"],
    "wound_healing":      ["electromagnetic","photobiomodulation","acoustic_ultrasound"],
    "anxiety_crisis":     ["biofeedback_neural","mechanical_haptic","thermal"],
    "ptsd":               ["biofeedback_neural","rf_sensing","photobiomodulation"],
    "depression":         ["photobiomodulation","magnetic_resonance","biofeedback_neural"],
    "addiction_craving":  ["biofeedback_neural","electromagnetic"],
    "autism_sensory":     ["mechanical_haptic","thermal","biofeedback_neural"],
    "paralysis":          ["electromagnetic","biofeedback_neural","mechanical_haptic"],
    "limb_loss":          ["mechanical_haptic","electromagnetic","biofeedback_neural"],
    "speech_impairment":  ["mechanical_haptic","electromagnetic","biofeedback_neural"],
    "tremor":             ["mechanical_haptic","electromagnetic","biofeedback_neural"],
    "rural_no_doctor":    ["electrochemical","rf_sensing","acoustic_ultrasound"],
    "food_insecurity":    ["electrochemical","rf_sensing"],
    "clean_water":        ["electrochemical","electrostatic","electromagnetic"],
    "air_quality":        ["electrostatic","electrochemical"],
    "domestic_violence":  ["rf_sensing","biofeedback_neural","mechanical_haptic"],
    "elderly_fall":       ["rf_sensing","mechanical_haptic"],
    "loneliness":         ["biofeedback_neural","mechanical_haptic"],
}

FORM_FACTORS = {
    "chronic_pain":"wearable patch","hearing_loss":"behind-ear module","mobility_impairment":"wrist band",
    "traumatic_brain":"headband","sleep_disorder":"sleep headband","diabetes_monitoring":"wrist sensor",
    "vision_impairment":"glasses attachment","wound_healing":"adhesive patch","anxiety_crisis":"wrist band",
    "ptsd":"chest patch","depression":"light therapy glasses","addiction_craving":"wrist band",
    "autism_sensory":"compression vest","paralysis":"surface electrode patch","limb_loss":"socket sensor",
    "speech_impairment":"throat patch","tremor":"wrist stabilizer","rural_no_doctor":"handheld diagnostic",
    "food_insecurity":"soil probe","clean_water":"inline sensor","air_quality":"clip-on sensor",
    "domestic_violence":"discreet wearable clip","elderly_fall":"room sensor","loneliness":"wrist band",
}

NAMES = {
    "chronic_pain":"Relief","hearing_loss":"Sound","mobility_impairment":"Motion","traumatic_brain":"Restore",
    "sleep_disorder":"Sleep","diabetes_monitoring":"Glucose","vision_impairment":"Vision","wound_healing":"Heal",
    "anxiety_crisis":"Calm","ptsd":"Safe","depression":"Light","addiction_craving":"Hold",
    "autism_sensory":"Steady","paralysis":"Bridge","limb_loss":"Reach","speech_impairment":"Voice",
    "tremor":"Still","rural_no_doctor":"Diagnose","food_insecurity":"Grow","clean_water":"Pure",
    "air_quality":"Air","domestic_violence":"Signal","elderly_fall":"Guard","loneliness":"Connect",
}

PREFIXES = ["Phoenix","Forge","Ember","Solace","Clarity","Pulse","Haven","Nexus","Lumen","Accord"]

def load_registry():
    f = DEVICES / "device_registry.json"
    if f.exists():
        try: return json.loads(f.read_text())
        except: pass
    return []

def save_registry(reg):
    (DEVICES / "device_registry.json").write_text(json.dumps(reg, indent=2))

def select_pain(generation, registry):
    addressed = {d.get("pain") for d in registry}
    candidates = [p for p in HUMAN_PAIN if p["pain"] not in addressed]
    if not candidates: candidates = HUMAN_PAIN
    weights = [math.log10(p["population"]) for p in candidates]
    total = sum(weights)
    r = random.uniform(0, total)
    cum = 0
    for i,w in enumerate(weights):
        cum += w
        if r <= cum: return candidates[i]
    return candidates[0]

def generate_device(pain_entry, generation, chip, apps, patterns):
    pain = pain_entry["pain"]
    options = PAIN_PHYSICS.get(pain, list(PHYSICS.keys()))
    phys_key = options[min(generation // 3, len(options)-1)] if generation < 15 else random.choice(options)
    phys = PHYSICS[phys_key]

    prefix = PREFIXES[generation % len(PREFIXES)]
    name = prefix + NAMES.get(pain, "Device")
    complexity = min(10, 1 + generation // 5)

    pw_min, pw_max = phys["power"]
    power_w = round(random.uniform(pw_min, min(pw_max, pw_min*(1+complexity))), 4)
    sz_min, sz_max = phys["size"]
    size_cm = round(random.uniform(sz_min, min(sz_max, sz_min*(1+complexity*0.5))), 1)
    cost = round(random.uniform(20, 80) * (1 + complexity * 0.25), 2)
    battery_h = round(min(168, random.uniform(8,72) / (power_w+0.1) * 0.5), 1)

    # Cross-reference: find matching app
    matching_app = next((a for a in apps if pain.replace("_","") in a["domain"].replace("_","") or a["domain"] in pain_entry.get("domain","")), None)

    # Cross-reference chip: does this device benefit from Phoenix chip?
    chip_enhanced = chip.get("edge_deployable", False) and cost < 300
    chip_note = ""
    if chip_enhanced:
        chip_note = f"Phoenix chip ({chip.get('matrix_size',131072)}x{chip.get('matrix_size',131072)}, {chip.get('interconnect','neuromorphic')}) enables on-device AI inference at {chip.get('clock_ghz',20)}GHz. No cloud. Fully private."

    # Wisdom score
    ws = 0
    wc = {}
    wc["proven_physics"] = phys["proven"]; ws += 20 if phys["proven"] else 0
    wc["affordable"] = cost < 500; ws += 20 if cost < 500 else 0
    wc["reaches_millions"] = pain_entry["population"] > 1000000; ws += 15 if pain_entry["population"] > 1000000 else 0
    wc["edge_deployable"] = power_w < 10 and cost < 500; ws += 15 if wc["edge_deployable"] else 0
    wc["has_companion_app"] = matching_app is not None; ws += 15 if matching_app else 0
    wc["chip_enhanced"] = chip_enhanced; ws += 15 if chip_enhanced else 0

    device = {
        "id": uuid.uuid4().hex[:8],
        "name": name,
        "generation": generation,
        "created_at": datetime.now().isoformat(),
        "pain": pain,
        "population": pain_entry["population"],
        "problem": pain_entry["description"],
        "physics": phys_key,
        "physics_desc": phys["desc"],
        "physics_proven": phys["proven"],
        "comparable_devices": phys["examples"][:2],
        "form_factor": FORM_FACTORS.get(pain, "wearable"),
        "complexity": complexity,
        "specs": {
            "power_watts": power_w,
            "size_cm": size_cm,
            "cost_usd": cost,
            "battery_hours": battery_h,
        },
        "edge_deployable": wc["edge_deployable"],
        "chip_note": chip_note,
        "companion_app": matching_app["name"] if matching_app else None,
        "companion_domain": matching_app["domain"] if matching_app else None,
        "wisdom_score": ws,
        "wisdom_criteria": wc,
        "total_score": ws,
        "peoples_charter": True,
    }
    return device

def run(cycles=1):
    chip = load_chip()
    apps = load_apps()
    patterns = load_app_patterns()
    registry = load_registry()
    generation = len(registry)

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  PHOENIX DEVICE FORGE — Cross-Referenced Autonomous Designer  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"\n  Chip loaded:    {chip.get('matrix_size',0):,}x{chip.get('matrix_size',0):,} {chip.get('interconnect','neuromorphic')} @ {chip.get('clock_ghz',20)}GHz")
    print(f"  Apps loaded:    {len(apps)} federation apps")
    print(f"  Pain catalog:   {len(HUMAN_PAIN)} conditions")
    print(f"  Generation:     {generation}")
    print(f"  Devices built:  {len(registry)}\n")

    built = []
    for c in range(cycles):
        gen = generation + c
        pain_entry = select_pain(gen, registry)
        device = generate_device(pain_entry, gen, chip, apps, patterns)

        domain_dir = DEVICES / device["pain"]
        domain_dir.mkdir(exist_ok=True)
        path = domain_dir / f"gen_{gen:04d}_{device['id']}.json"
        path.write_text(json.dumps(device, indent=2))

        s = device["specs"]
        ws = device["wisdom_score"]
        bar = "█" * (ws // 10)

        print(f"  ╔══════════════════════════════════════════════════════╗")
        print(f"  ║  DEVICE: {device['name']:44s}║")
        print(f"  ╚══════════════════════════════════════════════════════╝")
        print(f"  Problem:    {device['problem']}")
        print(f"  People:     {device['population']:,}")
        print(f"  Physics:    {device['physics']} — {device['physics_desc']}")
        print(f"  Form:       {device['form_factor']}")
        print(f"  Specs:      {s['power_watts']}W  |  {s['size_cm']}cm  |  ${s['cost_usd']:.2f}  |  {s['battery_hours']}h battery")
        print(f"  Based on:   {', '.join(device['comparable_devices'])}")
        if device["companion_app"]:
            print(f"  App link:   {device['companion_app']} ({device['companion_domain']})")
        if device["chip_note"]:
            print(f"  Chip:       {device['chip_note'][:80]}")
        print(f"  Score:      {ws}/100  {bar}")
        wc = device["wisdom_criteria"]
        for k,v in wc.items():
            print(f"    {'✅' if v else '❌'} {k}")
        print(f"  Saved:  devices/{device['pain']}/gen_{gen:04d}_{device['id']}.json\n")

        registry.append({"id":device["id"],"name":device["name"],"generation":gen,"pain":device["pain"],"physics":device["physics"],"score":ws,"cost":s["cost_usd"],"population":device["population"],"companion_app":device["companion_app"],"created_at":device["created_at"]})
        built.append(device)

    save_registry(registry)
    print(f"  Total devices: {len(registry)}  |  Registry: devices/device_registry.json")
    print(f"  Run more:  python3 ~/swarm-platform/device_forge.py --cycles=10")

import sys
if __name__ == "__main__":
    c = 1
    for i,a in enumerate(sys.argv[1:]):
        if a.startswith("--cycles="):
            c = int(a.split("=")[1])
        elif a == "--cycles" and i+2 < len(sys.argv):
            c = int(sys.argv[i+2])
    run(cycles=c)
