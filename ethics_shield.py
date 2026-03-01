#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  PHOENIX ETHICS SHIELD                                           ║
║  The Sword vs Shield Filter                                      ║
║                                                                  ║
║  Every discovery, device, and app must pass this gate            ║
║  before it is allowed to exist in Phoenix Forge.                 ║
║                                                                  ║
║  A SHIELD protects. A SWORD destroys.                            ║
║  Phoenix Forge only builds shields.                              ║
║                                                                  ║
║  This cannot be overridden. This cannot be evolved away.         ║
║  This is not a rule. This is who we are.                         ║
║                                                                  ║
║  "The supreme art of war is to subdue the enemy                  ║
║   without fighting." — Sun Tzu                                   ║
║  We do not fight. We heal.                                       ║
╚══════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════
# THE SWORD LIST
# These will never be built. Not for any reason. Not for anyone.
# If a discovery touches these — it is REJECTED immediately.
# ═══════════════════════════════════════════════════════════════

ABSOLUTE_PROHIBITIONS = [

    # Weapons of mass destruction
    "nuclear weapon", "atomic bomb", "hydrogen bomb", "thermonuclear",
    "fission weapon", "fusion weapon", "dirty bomb", "radiological weapon",
    "neutron bomb", "nuclear warhead", "fissile material weaponization",

    # Biological weapons
    "bioweapon", "biological weapon", "weaponized pathogen", "engineered plague",
    "gain of function for lethality", "enhanced transmissibility weapon",
    "weaponized virus", "weaponized bacteria", "toxin weapon", "botulinum weapon",
    "anthrax weapon", "smallpox weapon", "ebola weapon",

    # Chemical weapons
    "chemical weapon", "nerve agent", "sarin", "VX agent", "mustard gas",
    "weaponized chemical", "chemical warfare", "choking agent weapon",
    "blister agent weapon", "novichok",

    # Conventional weapons enhancement
    "explosive enhancement", "shaped charge design", "IED construction",
    "landmine", "cluster munition", "incendiary weapon design",
    "fragmentation weapon", "anti-personnel weapon",

    # Surveillance and control
    "mass surveillance", "population control technology", "thought monitoring",
    "involuntary tracking", "covert implant", "non-consensual monitoring",
    "authoritarian control", "dissent suppression",

    # Targeting specific groups
    "race-specific bioweapon", "ethnicity-targeted pathogen",
    "genetic discrimination tool", "eugenics application",

    # Autonomous lethal systems
    "autonomous killing", "lethal autonomous weapon", "killer robot",
    "autonomous targeting system", "unmanned lethal system",
]

# ═══════════════════════════════════════════════════════════════
# DUAL-USE CONCERNS
# These need extra scrutiny — could be shield OR sword
# Requires explicit defensive justification to proceed
# ═══════════════════════════════════════════════════════════════

DUAL_USE_FLAGS = [
    # Biology dual-use
    "pathogen modification", "viral enhancement", "bacterial resistance",
    "toxin synthesis", "venom extraction", "gain of function",
    "airborne transmission", "increased virulence",

    # Physics dual-use
    "electromagnetic pulse", "EMP generation", "directed energy",
    "high power microwave", "laser weapon", "particle beam",
    "plasma weapon",

    # Materials dual-use
    "explosive compound", "propellant chemistry", "oxidizer enhancement",
    "detonation", "armor piercing",

    # Cyber dual-use
    "malware", "cyberweapon", "exploit development", "zero day",
    "critical infrastructure attack", "power grid disruption",
    "ransomware", "botnet",

    # Surveillance dual-use
    "facial recognition mass", "location tracking without consent",
    "voice pattern identification without consent",
    "behavioral prediction for control",
]

# ═══════════════════════════════════════════════════════════════
# SHIELD CRITERIA
# What a protective discovery looks like
# ═══════════════════════════════════════════════════════════════

SHIELD_CRITERIA = {
    "heals_or_prevents":    "Does it heal disease, prevent suffering, or restore function?",
    "protects_vulnerable":  "Does it protect people who cannot protect themselves?",
    "informed_consent":     "Can people choose whether to use it?",
    "no_forced_application":"Can it not be used on someone without their knowledge?",
    "open_not_weaponizable":"Would publishing this openly make the world safer, not more dangerous?",
    "removes_power_imbalance": "Does it reduce the power gap between strong and weak?",
    "people_not_institutions": "Does it serve individuals over governments or corporations?",
}

# ═══════════════════════════════════════════════════════════════
# THE ETHICS ENGINE
# ═══════════════════════════════════════════════════════════════

class EthicsShield:

    def __init__(self):
        self.rejections = []
        self.approvals  = []
        self.warnings   = []

    def check(self, item, item_type="discovery"):
        """
        Run every piece of content through the shield.
        Returns: (approved: bool, verdict: str, details: dict)
        """
        text = self._extract_text(item).lower()
        result = {
            "item_type":     item_type,
            "item_id":       item.get("id", "unknown"),
            "item_name":     item.get("name") or item.get("problem_id") or item.get("id", ""),
            "approved":      False,
            "verdict":       "",
            "classification":"",
            "flags":         [],
            "shield_score":  0,
            "reasoning":     "",
        }

        # ── STEP 1: ABSOLUTE PROHIBITION CHECK ──────────────────
        for prohibition in ABSOLUTE_PROHIBITIONS:
            if prohibition in text:
                result["approved"]       = False
                result["verdict"]        = "REJECTED — SWORD"
                result["classification"] = "ABSOLUTE_PROHIBITION"
                result["flags"]          = [prohibition]
                result["reasoning"]      = f"Contains '{prohibition}' — this is an absolute prohibition. Phoenix Forge does not build weapons. Not for any reason. Not for anyone."
                self.rejections.append(result)
                return False, result

        # ── STEP 2: DUAL-USE FLAG CHECK ──────────────────────────
        dual_flags = []
        for flag in DUAL_USE_FLAGS:
            if flag in text:
                dual_flags.append(flag)

        if dual_flags:
            # Check if there's a clear defensive/protective framing
            defensive_words = ["protect", "defend", "detect", "prevent", "shield",
                              "diagnose", "treat", "heal", "monitor", "alert",
                              "safety", "security", "guard", "vaccine", "antidote",
                              "counter", "neutralize threat", "biosurveillance"]
            has_defensive = any(w in text for w in defensive_words)

            if not has_defensive:
                result["approved"]       = False
                result["verdict"]        = "REJECTED — DUAL USE WITHOUT DEFENSIVE FRAMING"
                result["classification"] = "DUAL_USE_CONCERN"
                result["flags"]          = dual_flags
                result["reasoning"]      = f"Flagged dual-use content: {', '.join(dual_flags[:3])}. No clear defensive/protective justification found. Reframe toward protection or reject."
                self.rejections.append(result)
                return False, result
            else:
                result["flags"]   = dual_flags
                result["verdict"] = "WARNING — DUAL USE, DEFENSIVE FRAMING PRESENT"
                self.warnings.append(result.copy())

        # ── STEP 3: SHIELD CRITERIA SCORING ─────────────────────
        shield_score = 0
        shield_checks = {}

        heals = any(w in text for w in ["heal", "treat", "cure", "therapy", "therapeutic",
                                         "medicine", "diagnosis", "prevent", "relief",
                                         "restore", "recovery", "rehabilitation"])
        shield_checks["heals_or_prevents"] = heals
        if heals: shield_score += 25

        protects = any(w in text for w in ["protect", "vulnerable", "shelter", "safety",
                                            "guard", "defend", "alert", "warn", "detect"])
        shield_checks["protects_vulnerable"] = protects
        if protects: shield_score += 20

        # Consent — does it require user participation?
        non_consent = any(w in text for w in ["covert", "involuntary", "without consent",
                                               "non-consensual", "forced", "compulsory"])
        shield_checks["informed_consent"] = not non_consent
        if not non_consent: shield_score += 20

        # Open publication safe?
        open_safe = not any(w in text for w in ["classified", "restricted", "secret weapon",
                                                  "military only", "defense only"])
        shield_checks["open_not_weaponizable"] = open_safe
        if open_safe: shield_score += 20

        # Serves people not institutions?
        people_focus = any(w in text for w in ["patient", "people", "human", "individual",
                                                "community", "family", "child", "elderly",
                                                "survivor", "person"])
        shield_checks["people_not_institutions"] = people_focus
        if people_focus: shield_score += 15

        result["shield_score"]  = shield_score
        result["shield_checks"] = shield_checks

        # ── FINAL VERDICT ────────────────────────────────────────
        if shield_score >= 40:
            result["approved"]       = True
            result["verdict"]        = "APPROVED — SHIELD"
            result["classification"] = "SHIELD"
            result["reasoning"]      = f"Shield score {shield_score}/100. Heals, protects, or serves people. No weapon indicators found. Safe to build."
            self.approvals.append(result)
            return True, result

        elif shield_score >= 20:
            result["approved"]       = True
            result["verdict"]        = "APPROVED WITH REVIEW — NEUTRAL"
            result["classification"] = "NEUTRAL"
            result["reasoning"]      = f"Shield score {shield_score}/100. Not clearly harmful but also not clearly beneficial. Recommend human review before proceeding."
            self.approvals.append(result)
            return True, result

        else:
            result["approved"]       = False
            result["verdict"]        = "REJECTED — INSUFFICIENT BENEFIT"
            result["classification"] = "REJECTED_LOW_BENEFIT"
            result["reasoning"]      = f"Shield score {shield_score}/100. Cannot confirm this serves people. Phoenix Forge only builds what helps. If it cannot be shown to help, it is not built."
            self.rejections.append(result)
            return False, result

    def _extract_text(self, item):
        """Pull all text from an item for scanning."""
        parts = []
        def extract(obj):
            if isinstance(obj, str):
                parts.append(obj)
            elif isinstance(obj, dict):
                for v in obj.values():
                    extract(v)
            elif isinstance(obj, list):
                for v in obj:
                    extract(v)
        extract(item)
        return " ".join(parts)

    def print_verdict(self, result):
        approved = result["approved"]
        icon     = "✅" if approved else "🚫"
        cls      = result["classification"]
        score    = result.get("shield_score", 0)

        colors = {
            "SHIELD":                  "SHIELD ✅",
            "NEUTRAL":                 "NEUTRAL ⚠️",
            "ABSOLUTE_PROHIBITION":    "SWORD 🚫 — ABSOLUTE PROHIBITION",
            "DUAL_USE_CONCERN":        "DUAL USE 🚫",
            "REJECTED_LOW_BENEFIT":    "REJECTED — NO CLEAR BENEFIT 🚫",
        }

        print(f"\n  {icon} ETHICS VERDICT: {colors.get(cls, cls)}")
        print(f"     Shield score: {score}/100")
        if result.get("flags"):
            print(f"     Flags: {', '.join(result['flags'][:3])}")
        print(f"     {result['reasoning'][:100]}")

    def summary(self):
        total     = len(self.approvals) + len(self.rejections)
        approved  = len(self.approvals)
        rejected  = len(self.rejections)
        warned    = len(self.warnings)
        rate      = (approved / total * 100) if total > 0 else 0

        print(f"\n  ╔══════════════════════════════════════════════════════╗")
        print(f"  ║  ETHICS SHIELD SUMMARY                               ║")
        print(f"  ╚══════════════════════════════════════════════════════╝")
        print(f"  Total reviewed:  {total}")
        print(f"  Approved:        {approved} ({rate:.0f}%)")
        print(f"  Rejected:        {rejected}")
        print(f"  Warnings:        {warned}")
        if self.rejections:
            print(f"\n  REJECTED ITEMS:")
            for r in self.rejections:
                print(f"    🚫 {r['item_name'][:50]} — {r['classification']}")

# ═══════════════════════════════════════════════════════════════
# STANDALONE TEST
# ═══════════════════════════════════════════════════════════════

def test_shield():
    shield = EthicsShield()

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  PHOENIX ETHICS SHIELD — Sword vs Shield Test                ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    test_cases = [
        {
            "id": "test_1",
            "name": "Alzheimer's treatment via CRISPR",
            "hypothesis": "CRISPR gene editing targeting amyloid precursor protein may reduce plaque formation and restore cognitive function in Alzheimer's patients",
            "experiment": "Human organoid model to test therapeutic gene editing",
            "population": 55000000,
        },
        {
            "id": "test_2",
            "name": "Bioweapon — REJECTED",
            "hypothesis": "Gain of function modification to increase airborne transmission of pathogen for biological weapon deployment",
            "mechanism": "weaponized virus enhanced transmissibility",
        },
        {
            "id": "test_3",
            "name": "Pain relief device",
            "hypothesis": "Pulsed electromagnetic field therapy may reduce chronic pain by modulating C-fiber signaling — heal patients who suffer daily",
            "experiment": "Randomized controlled trial in chronic pain patients",
            "population": 50000000,
        },
        {
            "id": "test_4",
            "name": "Nuclear weapon — REJECTED",
            "hypothesis": "Fission weapon design using enriched uranium for atomic bomb yield calculation",
        },
        {
            "id": "test_5",
            "name": "Fall detection for elderly",
            "hypothesis": "60GHz radar sensing can detect elderly fall events within 100ms to alert caregivers — protect vulnerable people who live alone",
            "experiment": "Prototype device testing in care facility",
            "population": 36000000,
        },
        {
            "id": "test_6",
            "name": "Depression photobiomodulation",
            "hypothesis": "810nm near-infrared transcranial photobiomodulation increases cerebral blood flow and BDNF to treat major depression in patients who do not respond to medication",
            "experiment": "Human TMS-EEG study with 12 week follow up",
            "population": 280000000,
        },
    ]

    for case in test_cases:
        print(f"  Testing: {case['name']}")
        approved, result = shield.check(case, "test")
        shield.print_verdict(result)
        print()

    shield.summary()

    print(f"\n  ════════════════════════════════════════════════════════")
    print(f"  Phoenix Forge does not build swords.")
    print(f"  Not for governments. Not for militaries. Not for money.")
    print(f"  Not for any reason. Not for anyone.")
    print(f"  ════════════════════════════════════════════════════════")


# Global shield instance — imported by science_engine, device_forge, phoenix_mind
SHIELD = EthicsShield()

def check(item, item_type="discovery"):
    """Single entry point for all ethics checks across Phoenix Forge."""
    return SHIELD.check(item, item_type)

if __name__ == "__main__":
    test_shield()
