#!/usr/bin/env python3
"""
HUMAN SCORE ENGINE
Scores apps on what actually matters to real people.
Not just technical correctness — human value.
"""
from pathlib import Path
import json
import re

HOME = Path.home()

# ═══════════════════════════════════════════════════
# SCORING DIMENSIONS
# Max score: 500 points (275 technical + 225 human)
# ═══════════════════════════════════════════════════

HUMAN_DIMENSIONS = {

    # ── OFFLINE CAPABILITY (50 pts) ──────────────────
    "offline": {
        "max": 50,
        "checks": {
            "has_localstorage":     (15, "Uses localStorage for data"),
            "no_server_required":   (15, "Works without backend server"),
            "offline_api_fallback": (10, "Falls back gracefully offline"),
            "data_persists":        (10, "Data survives page refresh"),
        }
    },

    # ── MOBILE FIRST (40 pts) ────────────────────────
    "mobile": {
        "max": 40,
        "checks": {
            "bottom_nav":           (15, "Mobile-friendly navigation"),
            "no_sidebar":           (10, "No desktop sidebar on mobile"),
            "touch_targets":        (10, "Buttons big enough to tap"),
            "no_horizontal_scroll": ( 5, "Content fits on phone screen"),
        }
    },

    # ── HUMAN INSIGHT QUALITY (50 pts) ───────────────
    "insight": {
        "max": 50,
        "checks": {
            "has_insight_layer":    (15, "Built with human insight engine"),
            "domain_color":         (10, "Domain-specific color scheme"),
            "leads_with_priority":  (10, "Dashboard shows most important thing first"),
            "no_generic_title":     ( 8, "Not named 'Item Management'"),
            "tone_appropriate":     ( 7, "Copy matches domain tone"),
        }
    },

    # ── REAL WORLD USABILITY (45 pts) ────────────────
    "usability": {
        "max": 45,
        "checks": {
            "no_login_wall":        (20, "No login screen blocking usage"),
            "works_immediately":    (15, "App is useful on first open"),
            "clear_empty_states":   (10, "Helpful message when no data"),
        }
    },

    # ── ALERT & WELLNESS AWARENESS (40 pts) ──────────
    "awareness": {
        "max": 40,
        "checks": {
            "has_alerts":           (15, "Shows important alerts prominently"),
            "has_status_badges":    (10, "Visual status indicators"),
            "today_focused":        (10, "Emphasizes what matters today"),
            "action_oriented":      ( 5, "Tells user what to do next"),
        }
    },
}

# ═══════════════════════════════════════════════════
# SCORER
# ═══════════════════════════════════════════════════
class HumanScoreEngine:

    def score(self, app_path, domain_id, cfg):
        """Score an app on human dimensions"""
        path = Path(app_path)
        frontend = path / "frontend" / "index.html"

        if not frontend.exists():
            return {"total": 0, "breakdown": {}, "error": "No frontend found"}

        html = frontend.read_text()
        html_lower = html.lower()

        breakdown = {}
        total_human = 0

        for dim_name, dim in HUMAN_DIMENSIONS.items():
            dim_score = 0
            dim_detail = {}

            for check_key, (points, description) in dim["checks"].items():
                passed = self._run_check(check_key, html, html_lower, domain_id, cfg)
                earned = points if passed else 0
                dim_score += earned
                dim_detail[check_key] = {
                    "points": earned,
                    "max": points,
                    "passed": passed,
                    "description": description
                }

            breakdown[dim_name] = {
                "score": dim_score,
                "max": dim["max"],
                "pct": round(dim_score / dim["max"] * 100),
                "checks": dim_detail
            }
            total_human += dim_score

        return {
            "human_score": total_human,
            "human_max": 225,
            "breakdown": breakdown,
            "grade": self._grade(total_human, 225)
        }

    def _run_check(self, check, html, html_lower, domain_id, cfg):
        checks = {
            # Offline
            "has_localstorage":     lambda: "localstorage" in html_lower,
            "no_server_required":   lambda: "offline_mode" in html_lower or "localstorage" in html_lower,
            "offline_api_fallback": lambda: "offlineapi" in html_lower or "offline_mode" in html_lower,
            "data_persists":        lambda: "localstorage.setitem" in html_lower,

            # Mobile
            "bottom_nav":           lambda: "overflow-x:auto" in html or "overflow-x: auto" in html,
            "no_sidebar":           lambda: "sidebar" not in html_lower or "display:none" in html_lower,
            "touch_targets":        lambda: "padding:1" in html or "padding: 1" in html,
            "no_horizontal_scroll": lambda: "max-width" in html_lower and "overflow-x" in html_lower,

            # Insight
            "has_insight_layer":    lambda: "offline_mode" in html_lower or "insight" in html_lower,
            "domain_color":         lambda: self._has_domain_color(html, domain_id),
            "leads_with_priority":  lambda: "today" in html_lower or "alert" in html_lower,
            "no_generic_title":     lambda: "item management" not in html_lower and "patient management" not in html_lower,
            "tone_appropriate":     lambda: self._has_tone(html_lower, domain_id),

            # Usability
            "no_login_wall":        lambda: "login-screen" not in html_lower,
            "works_immediately":    lambda: "localstorage" in html_lower or "login-screen" not in html_lower,
            "clear_empty_states":   lambda: "no " in html_lower and ("yet" in html_lower or "found" in html_lower),

            # Awareness
            "has_alerts":           lambda: "alert" in html_lower or "warning" in html_lower,
            "has_status_badges":    lambda: "badge" in html_lower,
            "today_focused":        lambda: "today" in html_lower,
            "action_oriented":      lambda: "add" in html_lower and "save" in html_lower,
        }
        fn = checks.get(check)
        if fn:
            try: return fn()
            except: return False
        return False

    def _has_domain_color(self, html, domain_id):
        """Check if app uses domain-specific color"""
        domain_colors = {
            "salon": "#7c3aed", "healthcare": "#2563eb",
            "restaurant": "#dc2626", "agriculture": "#2d6a4f",
            "nutrition_center": "#e07b39", "gym": "#f59e0b",
            "pharmacy": "#0891b2", "rf_sensing": "#4f46e5",
            "robotics": "#1d4ed8", "autonomous_vehicle": "#059669"
        }
        color = domain_colors.get(domain_id)
        return color and color in html

    def _has_tone(self, html_lower, domain_id):
        """Check if copy matches domain tone"""
        tone_signals = {
            "salon": ["welcome", "looking good", "all set", "great"],
            "healthcare": ["confirmed", "scheduled", "ready", "on track"],
            "restaurant": ["ready", "up next", "now", "fire"],
            "agriculture": ["done", "check", "good", "on it"],
            "nutrition_center": ["safe", "accounted for", "cared for"],
            "gym": ["strong", "crushing", "let's go", "on track"],
            "pharmacy": ["verified", "confirmed", "accurate", "ready"],
        }
        signals = tone_signals.get(domain_id, ["ready", "done", "good"])
        return any(s in html_lower for s in signals)

    def _grade(self, score, max_score):
        pct = score / max_score * 100
        if pct >= 90: return "A"
        if pct >= 80: return "B"
        if pct >= 70: return "C"
        if pct >= 60: return "D"
        return "F"


# ═══════════════════════════════════════════════════
# TEST ON EXISTING CHAMPIONS
# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    from pathlib import Path
    import json

    engine = HumanScoreEngine()
    champions_dir = HOME / "ORGANISM_ARMY/champions"
    configs_file = HOME / "organism_templates/domain_configs.json"
    configs = json.loads(configs_file.read_text())

    print("=" * 60)
    print("HUMAN SCORE ENGINE — SCORING ALL CHAMPIONS")
    print("Technical max: 275 | Human max: 225 | Total max: 500")
    print("=" * 60)

    results = []
    for domain_dir in sorted(champions_dir.iterdir()):
        if not domain_dir.is_dir(): continue
        champ_file = domain_dir / "champion.json"
        if not champ_file.exists(): continue

        champ = json.loads(champ_file.read_text())
        domain_id = champ.get("domain", domain_dir.name)
        cfg = configs.get(domain_id, {})
        source = champ.get("source_app", "")
        app_path = HOME / source if source else None

        if not app_path or not app_path.exists():
            continue

        tech_score = champ.get("score", 0)
        human = engine.score(app_path, domain_id, cfg)
        total = tech_score + human["human_score"]

        results.append({
            "domain": domain_id,
            "tech": tech_score,
            "human": human["human_score"],
            "total": total,
            "grade": human["grade"]
        })

        bar = "█" * (human["human_score"] // 10) + "░" * ((225 - human["human_score"]) // 10)
        print(f"\n{domain_id:22} Tech:{tech_score:4} Human:{human['human_score']:4}/225 Total:{total:4} [{human['grade']}]")
        print(f"  [{bar}]")

    print("\n" + "=" * 60)
    if results:
        avg_human = sum(r["human"] for r in results) / len(results)
        avg_total = sum(r["total"] for r in results) / len(results)
        top = max(results, key=lambda r: r["total"])
        print(f"Avg human score: {avg_human:.0f}/225")
        print(f"Avg total score: {avg_total:.0f}/500")
        print(f"Top performer:   {top['domain']} — {top['total']}/500")
    print("=" * 60)
    print("\nNext: Wire this into turbo_evolve.py scoring")
    print("Apps that score high on BOTH dimensions crown")
