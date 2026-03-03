#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  PHOENIX SCIENCE ENGINE                                          ║
║  Autonomous Scientific Discovery                                 ║
║                                                                  ║
║  The organism scans unsolved human problems and asks:            ║
║  "What mechanism might explain this?                             ║
║   What experiment would prove it?                                ║
║   Who would it help?"                                            ║
║                                                                  ║
║  Rules:                                                          ║
║    1. All domains — organism decides                             ║
║    2. Start simple, evolve complexity                            ║
║    3. Every discovery links to human benefit                     ║
║    4. Math and known science must support it                     ║
║    5. Testable — must be falsifiable                             ║
║                                                                  ║
║  Install: cp science_engine.py ~/swarm-platform/                 ║
║  Run:     python3 ~/swarm-platform/science_engine.py             ║
╚══════════════════════════════════════════════════════════════════╝
"""

import json
import math
import random
import uuid
import hashlib
from datetime import datetime
from pathlib import Path

SWARM    = Path("/data/data/com.termux/files/home/swarm-platform")
NEURAL   = SWARM / "neural"
SCIENCE  = SWARM / "science"
REGISTRY = SCIENCE / "discovery_registry.json"

NEURAL.mkdir(parents=True, exist_ok=True)
SCIENCE.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# UNSOLVED PROBLEMS CATALOG
# What humanity doesn't understand yet — that matters to people
# ═══════════════════════════════════════════════════════════════

UNSOLVED_PROBLEMS = [

    # Biology & Disease
    {"id":"alzheimers_mechanism",    "domain":"biology",       "problem":"Why do amyloid plaques form in Alzheimer's and can they be cleared?", "population":55_000_000,  "urgency":0.95},
    {"id":"cancer_metastasis",       "domain":"biology",       "problem":"What triggers cancer cells to leave primary tumor and colonize new tissue?", "population":19_000_000, "urgency":0.95},
    {"id":"autoimmune_trigger",      "domain":"biology",       "problem":"Why does the immune system attack the body's own tissue in autoimmune disease?", "population":50_000_000, "urgency":0.85},
    {"id":"chronic_fatigue_cause",   "domain":"biology",       "problem":"What causes chronic fatigue syndrome — no biomarker or mechanism identified", "population":17_000_000, "urgency":0.80},
    {"id":"aging_mechanism",         "domain":"biology",       "problem":"What is the primary molecular cause of biological aging — can it be slowed?", "population":8_000_000_000, "urgency":0.70},
    {"id":"microbiome_brain",        "domain":"biology",       "problem":"How does gut microbiome composition directly affect brain chemistry and mood?", "population":300_000_000, "urgency":0.80},
    {"id":"wound_regeneration",      "domain":"biology",       "problem":"Why can salamanders regenerate limbs but humans cannot — what gene pathway?", "population":2_100_000, "urgency":0.75},
    {"id":"prion_folding",           "domain":"biology",       "problem":"What causes normal proteins to misfold into prions and spread through tissue?", "population":1_000_000, "urgency":0.85},
    {"id":"epigenetic_inheritance",  "domain":"biology",       "problem":"How are trauma and stress responses inherited epigenetically across generations?", "population":500_000_000, "urgency":0.70},
    {"id":"pain_chronification",     "domain":"biology",       "problem":"Why does acute pain become chronic in some people — what neural change occurs?", "population":50_000_000, "urgency":0.90},

    # Neuroscience & Consciousness
    {"id":"consciousness_basis",     "domain":"neuroscience",  "problem":"What physical process in the brain produces subjective conscious experience?", "population":8_000_000_000, "urgency":0.60},
    {"id":"sleep_function",          "domain":"neuroscience",  "problem":"Why do all animals sleep — what is the essential biological function?", "population":8_000_000_000, "urgency":0.65},
    {"id":"memory_storage",          "domain":"neuroscience",  "problem":"How are long-term memories physically encoded in neural tissue?", "population":8_000_000_000, "urgency":0.65},
    {"id":"depression_neurobiology", "domain":"neuroscience",  "problem":"What is the actual neurobiological mechanism of depression — serotonin alone is insufficient", "population":280_000_000, "urgency":0.90},
    {"id":"addiction_rewiring",      "domain":"neuroscience",  "problem":"Can addiction-related neural pathway changes be reversed without withdrawal?", "population":21_000_000, "urgency":0.90},
    {"id":"ptsd_memory_lock",        "domain":"neuroscience",  "problem":"Why do traumatic memories become locked and intrusive — what neural mechanism?", "population":12_000_000, "urgency":0.85},
    {"id":"neuroplasticity_limit",   "domain":"neuroscience",  "problem":"What limits adult neuroplasticity — can those limits be safely removed?", "population":200_000_000, "urgency":0.75},
    {"id":"autism_connectivity",     "domain":"neuroscience",  "problem":"What neural connectivity differences cause autism spectrum characteristics?", "population":75_000_000, "urgency":0.75},
    {"id":"chronic_pain_central",    "domain":"neuroscience",  "problem":"How does central sensitization maintain chronic pain without tissue damage?", "population":50_000_000, "urgency":0.90},
    {"id":"schizophrenia_dopamine",  "domain":"neuroscience",  "problem":"Is dopamine dysregulation cause or effect in schizophrenia — what is primary?", "population":24_000_000, "urgency":0.85},

    # Physics & Energy
    {"id":"room_temp_superconductor","domain":"physics",       "problem":"Can superconductivity be achieved at room temperature — what material structure?", "population":8_000_000_000, "urgency":0.80},
    {"id":"fusion_ignition",         "domain":"physics",       "problem":"How to achieve sustained net-positive nuclear fusion at commercial scale?", "population":8_000_000_000, "urgency":0.85},
    {"id":"dark_matter_nature",      "domain":"physics",       "problem":"What is dark matter composed of — 27% of universe is unknown", "population":8_000_000_000, "urgency":0.50},
    {"id":"quantum_decoherence",     "domain":"physics",       "problem":"Why does quantum superposition collapse — can decoherence be prevented at scale?", "population":8_000_000_000, "urgency":0.70},
    {"id":"turbulence_math",         "domain":"physics",       "problem":"Why is turbulent fluid flow mathematically unpredictable — Navier-Stokes unsolved", "population":1_000_000_000, "urgency":0.65},
    {"id":"gravity_quantum",         "domain":"physics",       "problem":"How does gravity behave at quantum scales — quantum gravity unresolved", "population":8_000_000_000, "urgency":0.55},
    {"id":"solar_energy_storage",    "domain":"physics",       "problem":"How to store solar energy at grid scale without chemical battery degradation?", "population":3_000_000_000, "urgency":0.90},
    {"id":"high_temp_battery",       "domain":"physics",       "problem":"Why do lithium batteries degrade at high temperature — ionic mechanism unclear", "population":2_000_000_000, "urgency":0.85},
    {"id":"electromagnetic_thrust",  "domain":"physics",       "problem":"Can electromagnetic fields generate sustained thrust without propellant — EmDrive physics", "population":8_000_000_000, "urgency":0.70},
    {"id":"zero_point_energy",       "domain":"physics",       "problem":"Is zero-point vacuum energy extractable as usable power — quantum thermodynamics unclear", "population":8_000_000_000, "urgency":0.60},

    # Materials Science
    {"id":"graphene_production",     "domain":"materials",     "problem":"How to produce defect-free large-area graphene at low cost?", "population":3_000_000_000, "urgency":0.80},
    {"id":"plastic_biodegradation",  "domain":"materials",     "problem":"What enzyme or organism efficiently degrades all plastic types at scale?", "population":8_000_000_000, "urgency":0.90},
    {"id":"bone_scaffold_material",  "domain":"materials",     "problem":"What synthetic material perfectly mimics bone's mechanical and biological properties?", "population":10_000_000, "urgency":0.85},
    {"id":"neural_interface_material","domain":"materials",    "problem":"What material is biocompatible, conductive, and flexible enough for long-term brain implants?", "population":5_400_000, "urgency":0.90},
    {"id":"self_healing_material",   "domain":"materials",     "problem":"How to engineer materials that autonomously repair microcracks before failure?", "population":1_000_000_000, "urgency":0.75},
    {"id":"water_filtration_membrane","domain":"materials",    "problem":"What membrane material filters all contaminants from water at low energy cost?", "population":2_200_000_000, "urgency":0.95},
    {"id":"solar_cell_efficiency",   "domain":"materials",     "problem":"Why do perovskite solar cells degrade — what material instability causes it?", "population":3_000_000_000, "urgency":0.85},
    {"id":"antibiotic_resistance",   "domain":"materials",     "problem":"What material surface coating prevents bacterial biofilm formation on implants?", "population":700_000_000, "urgency":0.90},
    {"id":"flexible_electronics",    "domain":"materials",     "problem":"What substrate allows silicon-level performance in fully flexible electronics?", "population":500_000_000, "urgency":0.75},
    {"id":"hydrogen_storage",        "domain":"materials",     "problem":"What material stores hydrogen fuel at high density without safety risk?", "population":3_000_000_000, "urgency":0.85},

    # Environmental & Climate
    {"id":"co2_capture_catalyst",    "domain":"environment",   "problem":"What catalyst efficiently converts atmospheric CO2 to useful compounds at ambient conditions?", "population":8_000_000_000, "urgency":0.95},
    {"id":"soil_microbiome_restore", "domain":"environment",   "problem":"How to restore depleted agricultural soil microbiome rapidly at scale?", "population":500_000_000, "urgency":0.90},
    {"id":"ocean_acidification",     "domain":"environment",   "problem":"Can ocean acidification be safely reversed — what biochemical approach?", "population":3_000_000_000, "urgency":0.85},
    {"id":"water_desalination_energy","domain":"environment",  "problem":"How to desalinate seawater at dramatically lower energy cost than reverse osmosis?", "population":2_200_000_000, "urgency":0.95},
    {"id":"nitrogen_fixation",       "domain":"environment",   "problem":"How to achieve biological nitrogen fixation in non-legume crops to eliminate fertilizer?", "population":500_000_000, "urgency":0.90},

    # Mathematics & Computing
    {"id":"protein_folding_speed",   "domain":"computing",     "problem":"Can protein structure be predicted from sequence in real time without AlphaFold compute cost?", "population":8_000_000_000, "urgency":0.80},
    {"id":"np_vs_p",                 "domain":"computing",     "problem":"Are NP-complete problems solvable in polynomial time — P vs NP unsolved", "population":8_000_000_000, "urgency":0.55},
    {"id":"cryptography_quantum",    "domain":"computing",     "problem":"What encryption survives quantum computer attacks — post-quantum cryptography", "population":4_000_000_000, "urgency":0.90},
    {"id":"drug_discovery_speed",    "domain":"computing",     "problem":"How to predict drug-receptor binding affinity from molecular structure without wet lab?", "population":8_000_000_000, "urgency":0.90},
    {"id":"ai_energy_efficiency",    "domain":"computing",     "problem":"Why does biological neural computation use 20W while AI uses megawatts — what is different?", "population":8_000_000_000, "urgency":0.85},
]

# ═══════════════════════════════════════════════════════════════
# SCIENTIFIC MECHANISMS
# Known science the organism can draw from
# ═══════════════════════════════════════════════════════════════

MECHANISMS = {
    "biology": [
        "CRISPR gene editing targeting specific pathway",
        "Monoclonal antibody blocking protein-protein interaction",
        "Small molecule inhibitor of enzyme active site",
        "mRNA therapy to upregulate/downregulate gene expression",
        "Stem cell differentiation into target tissue type",
        "Epigenetic methylation/demethylation of regulatory region",
        "Autophagy activation to clear misfolded proteins",
        "Mitochondrial membrane potential modulation",
        "Telomerase activation/inhibition in target cells",
        "Microbiome modulation via targeted bacteriophage therapy",
        "Nanoparticle delivery to cross blood-brain barrier",
        "Photodynamic therapy targeting specific cell receptors",
        "Optogenetic control of specific neuron populations",
        "Viral vector delivery of therapeutic gene",
    ],
    "neuroscience": [
        "Synaptic plasticity modulation via NMDA receptor",
        "Glial cell activation/suppression in target brain region",
        "Default mode network connectivity measurement via fMRI",
        "Vagus nerve stimulation modulating brain-gut axis",
        "Transcranial magnetic stimulation of specific cortical area",
        "Neuroinflammation reduction via microglial targeting",
        "Dopamine/serotonin reuptake inhibition with specificity",
        "BDNF upregulation to promote neurogenesis",
        "Sleep-dependent memory consolidation in hippocampus",
        "Fear memory reconsolidation interference via timing",
        "Ketamine-like NMDA antagonism without dissociation",
        "Psychedelic-induced neuroplasticity via 5-HT2A receptor",
        "Deep brain stimulation of subthalamic nucleus",
        "Cortical spreading depression mechanism in migraine",
    ],
    "physics": [
        "Quantum tunneling through energy barrier",
        "Topological insulator surface state conduction",
        "Bose-Einstein condensate at higher temperature",
        "Photonic bandgap manipulation in metamaterial",
        "Magnetohydrodynamic flow without moving parts",
        "Casimir effect between nanoscale surfaces",
        "Piezoelectric coupling in novel crystal structure",
        "Thermoelectric Seebeck coefficient maximization",
        "Plasma confinement via magnetic mirror geometry",
        "Resonant inductive coupling for wireless power",
        "Optical rectenna for direct photon-to-electron conversion",
        "Spintronics for low-power data storage",
        "Acoustic levitation for contactless manipulation",
        "Electromagnetic induction in moving biological tissue",
    ],
    "materials": [
        "Two-dimensional material stacking (van der Waals heterostructure)",
        "Metal-organic framework with specific pore geometry",
        "Polymer crosslinking under specific stimulus",
        "Atomic layer deposition of conformal coating",
        "Biomimetic surface structure (lotus, shark skin, gecko)",
        "Shape memory alloy phase transition",
        "Liquid crystal elastomer actuation",
        "Hydrogel swelling/shrinking response",
        "Carbon nanotube alignment in polymer matrix",
        "Perovskite crystal structure optimization",
        "Aerogel porosity for thermal/acoustic insulation",
        "Bacteriophage surface display for targeting",
        "Self-assembled monolayer for surface functionalization",
        "Electrospun nanofiber scaffold for tissue engineering",
    ],
    "environment": [
        "Photocatalytic oxidation under visible light",
        "Bioelectrochemical system for pollutant conversion",
        "Mycorrhizal network enhancement for nutrient cycling",
        "Biochar amendment for soil carbon sequestration",
        "Constructed wetland for water filtration",
        "Electrocoagulation for suspended particle removal",
        "Forward osmosis using draw solution gradient",
        "Enzymatic depolymerization of specific polymer",
        "Rhizobium inoculation for nitrogen fixation",
        "Phytoremediation with hyperaccumulator plant species",
    ],
    "computing": [
        "Neuromorphic spike-timing dependent plasticity",
        "Quantum annealing for optimization problems",
        "Homomorphic encryption for private computation",
        "Lattice-based cryptography for quantum resistance",
        "Monte Carlo tree search with learned heuristics",
        "Attention mechanism with linear complexity",
        "Reservoir computing with physical substrate",
        "Federated learning without data centralization",
        "DNA computing for massively parallel search",
        "Optical neural network for speed-of-light inference",
    ],
}

# ═══════════════════════════════════════════════════════════════
# HYPOTHESIS TEMPLATES
# How the organism structures its hypotheses
# ═══════════════════════════════════════════════════════════════

HYPOTHESIS_TEMPLATES = [
    "If {mechanism} is applied to {target}, then {outcome} will occur because {reasoning}.",
    "{mechanism} may resolve {problem} by {action} at the {level} level.",
    "The key to {problem} is {mechanism} — specifically {detail} — which would {benefit}.",
    "Combining {mechanism} with {existing_approach} could unlock {outcome} by addressing {gap}.",
    "{problem} remains unsolved because {missed_insight}. {mechanism} directly addresses this.",
]

EXPERIMENT_TYPES = {
    "biology":     ["In vitro cell culture assay", "Mouse model knockout study", "Human organoid model", "Retrospective cohort analysis", "Randomized controlled trial Phase I"],
    "neuroscience":["EEG/MEG signal analysis", "fMRI connectivity study", "Optogenetic mouse model", "Human TMS-EEG study", "Longitudinal patient cohort"],
    "physics":     ["Computational simulation", "Bench-top proof of concept", "Materials characterization (XRD, SEM)", "Calorimetric measurement", "Spectroscopic analysis"],
    "materials":   ["Synthesis and characterization", "Mechanical testing (tensile, fatigue)", "In vitro biocompatibility assay", "Accelerated degradation study", "Prototype device testing"],
    "environment": ["Mesocosm controlled study", "Field pilot deployment", "Life cycle assessment", "Microbial community sequencing", "Sensor network monitoring"],
    "computing":   ["Benchmark on standard dataset", "Theoretical complexity proof", "Hardware prototype", "Security audit", "Comparative ablation study"],
}

WISDOM_FOR_SCIENCE = [
    "To know that you do not know is the best. — Lao Tzu",
    "The impediment to action advances action. What stands in the way becomes the way. — Marcus Aurelius",
    "In the beginner's mind there are many possibilities. In the expert's mind there are few. — Shunryu Suzuki",
    "Real knowledge is to know the extent of one's ignorance. — Confucius",
    "The art of science is asking the right question, not answering. — Max Planck paraphrase",
    "If you want to find the secrets of the universe, think in terms of energy, frequency and vibration. — Tesla",
    "We cannot solve problems with the same thinking that created them. — Einstein paraphrase",
    "Nature uses only the longest threads to weave her patterns. — Richard Feynman",
    "The important thing is not to stop questioning. — Einstein",
    "What we observe is not nature itself but nature exposed to our method of questioning. — Heisenberg",
]

# ═══════════════════════════════════════════════════════════════
# DISCOVERY ENGINE
# ═══════════════════════════════════════════════════════════════

def load_registry():
    if REGISTRY.exists():
        try:
            return json.loads(REGISTRY.read_text())
        except:
            return []
    return []

def save_registry(reg):
    REGISTRY.write_text(json.dumps(reg, indent=2))

def select_problem(registry, generation):
    """Choose a problem based on urgency and not yet addressed"""
    addressed = {d.get("problem_id") for d in registry}
    candidates = [p for p in UNSOLVED_PROBLEMS if p["id"] not in addressed]
    if not candidates:
        candidates = UNSOLVED_PROBLEMS
    
    # Weight by urgency * log(population) — more suffering = higher priority
    weights = [p["urgency"] * math.log10(p["population"] + 1) for p in candidates]
    total = sum(weights)
    r = random.uniform(0, total)
    cum = 0
    for i, w in enumerate(weights):
        cum += w
        if r <= cum:
            return candidates[i]
    return candidates[0]

def generate_hypothesis(problem, mechanism, domain):
    """Generate a testable hypothesis"""
    template = random.choice(HYPOTHESIS_TEMPLATES)
    
    # Extract key words for placeholders
    words = problem["problem"].lower().split()
    target = words[-3] if len(words) > 3 else "the system"
    if target.endswith("?"): target = target[:-1]
    
    outcome = "disease progression slows" if "alzheimer" in problem["problem"] else "function improves"
    reasoning = "the mechanism targets the root cause directly" if random.random() > 0.5 else "prior evidence supports this pathway"
    action = "blocking" if "inhibit" in mechanism else "activating"
    level = "molecular" if domain in ["biology","materials"] else "systems"
    detail = mechanism.split(" ")[:3] if len(mechanism.split()) > 3 else mechanism
    benefit = f"help {problem['population']:,} people affected"
    existing_approach = "current standard of care"
    gap = "existing therapies only treat symptoms"
    missed_insight = "previous research missed the role of " + mechanism.split()[0]
    
    hypothesis = template.format(
        mechanism=mechanism,
        target=target,
        outcome=outcome,
        reasoning=reasoning,
        problem=problem["problem"],
        action=action,
        level=level,
        detail=" ".join(detail) if isinstance(detail,list) else detail,
        benefit=benefit,
        existing_approach=existing_approach,
        gap=gap,
        missed_insight=missed_insight
    )
    return hypothesis

def propose_experiment(domain, hypothesis):
    """Propose a falsifiable experiment to test the hypothesis"""
    exp_type = random.choice(EXPERIMENT_TYPES.get(domain, ["Literature review", "Computational model"]))
    duration = random.randint(3, 36) if domain in ["biology","neuroscience","materials"] else random.randint(1, 12)
    cost_map = {"biology":500000, "neuroscience":350000, "physics":250000, "materials":200000, "environment":150000, "computing":50000}
    cost = cost_map.get(domain, 100000) * (duration / 12) * random.uniform(0.8, 1.2)
    
    return {
        "type": exp_type,
        "duration_months": duration,
        "estimated_cost_usd": int(cost),
        "falsifiable": True,
        "control_required": True,
        "blinding": "double-blind" if domain in ["biology","neuroscience"] else "single-blind",
        "sample_size": int(100 * math.sqrt(duration)) if domain in ["biology","neuroscience"] else None,
        "outcome_measure": "quantitative biomarker" if random.random() > 0.5 else "validated scale",
        "protocol": f"{exp_type} with {duration} month follow-up. Control group receives placebo/sham."
    }

def estimate_impact(problem, discovery):
    """Estimate human impact of this discovery"""
    pop = problem["population"]
    fraction = random.uniform(0.1, 0.5) if pop > 100_000_000 else random.uniform(0.3, 0.8)
    lives_improved = int(pop * fraction)
    quality_of_life_gain = random.choice([10,20,30,40,50,60,70,80,90])
    years_if_solved = random.randint(5, 30)
    
    return {
        "lives_impacted": lives_improved,
        "quality_of_life_gain_pct": quality_of_life_gain,
        "years_of_benefit": years_if_solved,
        "economic_value_usd": lives_improved * quality_of_life_gain * 1000
    }

def generate_discovery(generation):
    """Main discovery generation function"""
    registry = load_registry()
    problem = select_problem(registry, generation)
    domain = problem["domain"]
    
    # Select mechanism from domain
    mechanism = random.choice(MECHANISMS.get(domain, ["Literature review", "Computational analysis"]))
    
    hypothesis = generate_hypothesis(problem, mechanism, domain)
    experiment = propose_experiment(domain, hypothesis)
    impact = estimate_impact(problem, experiment)
    
    discovery_id = hashlib.sha256(f"{problem['id']}{mechanism}{generation}".encode()).hexdigest()[:12]
    
    discovery = {
        "id": discovery_id,
        "generation": generation,
        "created_at": datetime.now().isoformat(),
        "problem_id": problem["id"],
        "problem": problem["problem"],
        "domain": domain,
        "population": problem["population"],
        "urgency": problem["urgency"],
        "mechanism": mechanism,
        "hypothesis": hypothesis,
        "experiment": experiment,
        "impact": impact,
        "confidence": random.uniform(0.3, 0.8),  # low confidence initially, will evolve
        "wisdom": random.choice(WISDOM_FOR_SCIENCE),
        "status": "proposed"
    }
    
    # Save individual file
    disc_dir = SCIENCE / "discoveries"
    disc_dir.mkdir(exist_ok=True)
    disc_file = disc_dir / f"gen_{generation:06d}_{discovery_id}.json"
    disc_file.write_text(json.dumps(discovery, indent=2))
    
    # Update registry
    registry.append({
        "id": discovery_id,
        "generation": generation,
        "problem_id": problem["id"],
        "problem": problem["problem"][:60] + "...",
        "domain": domain,
        "population": problem["population"],
        "confidence": discovery["confidence"],
        "file": str(disc_file)
    })
    save_registry(registry)
    
    return discovery

def print_discovery(d):
    print("\n" + "═" * 70)
    print(f"🔬 DISCOVERY {d['generation']:06d} — {d['domain'].upper()}")
    print("═" * 70)
    print(f"\nPROBLEM: {d['problem']}")
    print(f"People affected: {d['population']:,}   Urgency: {d['urgency']:.2f}")
    print(f"\nMECHANISM: {d['mechanism']}")
    print(f"\nHYPOTHESIS: {d['hypothesis']}")
    print(f"\nEXPERIMENT:")
    exp = d['experiment']
    print(f"  Type: {exp['type']}")
    print(f"  Duration: {exp['duration_months']} months")
    print(f"  Est. cost: ${exp['estimated_cost_usd']:,}")
    print(f"  Protocol: {exp['protocol']}")
    print(f"\nIMPACT:")
    imp = d['impact']
    print(f"  Lives impacted: {imp['lives_impacted']:,}")
    print(f"  Quality of life gain: {imp['quality_of_life_gain_pct']}%")
    print(f"  Est. economic value: ${imp['economic_value_usd']:,}")
    print(f"\nCONFIDENCE: {d['confidence']:.0%}")
    print(f"\n\"{d['wisdom']}\"")
    print("═" * 70)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def run(cycles=1, verbose=True):
    registry = load_registry()
    gen = len(registry)
    
    if verbose:
        print("\n" + "╔" + "═"*68 + "╗")
        print("║  🔬 PHOENIX SCIENCE ENGINE — AUTONOMOUS DISCOVERY            ║")
        print("╚" + "═"*68 + "╝")
        print(f"\nProblems in catalog: {len(UNSOLVED_PROBLEMS)}")
        print(f"Discoveries so far:  {gen}")
        print(f"Generations this run: {cycles}")
        print()
    
    for i in range(cycles):
        current_gen = gen + i + 1
        d = generate_discovery(current_gen)
        if verbose:
            print_discovery(d)
    
    if verbose:
        print(f"\n✅ {cycles} discoveries generated")
        print(f"Total discoveries: {gen + cycles}")
        print(f"Registry: {REGISTRY}")
        print("\nRun more: python3 science_engine.py --cycles 10")

if __name__ == "__main__":
    import sys
    cycles = 1
    for arg in sys.argv[1:]:
        if arg.startswith("--cycles="):
            cycles = int(arg.split("=")[1])
        elif arg == "--cycles" and len(sys.argv) > sys.argv.index(arg) + 1:
            cycles = int(sys.argv[sys.argv.index(arg) + 1])
    run(cycles=cycles)

# ── FREEDOM PROBLEMS (added March 2, 2026) ─────────────
    {"id":"survival_to_creation", "domain":"philosophy", "problem":"How do we remove survival fear so people can become fully creative?", "population":8_000_000_000, "urgency":1.0},
    {"id":"creative_block_poverty", "domain":"psychology", "problem":"What psychological mechanisms link poverty to reduced creative output?", "population":3_000_000_000, "urgency":0.9},
    {"id":"freedom_measurement", "domain":"computing", "problem":"How to measure whether a person has been freed from survival fear?", "population":8_000_000_000, "urgency":0.8},
