#!/usr/bin/env python3
import re

with open('meta_evolver.py', 'r') as f:
    content = f.read()

# Check if evolve_rules exists
if 'def evolve_rules' not in content:
    print("🟡 evolve_rules method not found, adding it...")
    
    # Find where to insert it (after _save_rules)
    pattern = r'def _save_rules.*?\n    def '
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        evolve_method = '''
    def evolve_rules(self):
        """
        Core of Phase 2 — learn from history, propose new rules,
        validate against constitution, apply if approved.
        """
        print("\\n  ╔══════════════════════════════════════════════════════╗")
        print("  ║  PHASE 2 — RULE EVOLUTION                            ║")
        print("  ╚══════════════════════════════════════════════════════╝\\n")

        # Learn from everything built so far
        disc_insights   = self.learn_from_discoveries()
        device_insights = self.learn_from_devices()

        print(f"  Learning from {disc_insights.get('total_discoveries', 0):,} discoveries")
        print(f"  Learning from {device_insights.get('total_devices', 0):,} devices\\n")

        changes_proposed = 0
        changes_approved = 0
        changes_rejected = 0

        # ── EVOLUTION 1: Domain Priority ────────────────────────
        if disc_insights.get("domain_avg"):
            domain_avg = disc_insights["domain_avg"]
            total      = sum(domain_avg.values())

            new_priorities = {
                k: round(v / total * len(domain_avg), 3)
                for k, v in domain_avg.items()
            }

            proposed = {
                "component":   "domain_priority",
                "description": "Reweight domain priorities based on confidence scores from real discoveries",
                "reason":      f"Learned from {disc_insights['total_discoveries']} discoveries — domains with higher confidence scores should be explored more. Serves people better by focusing on solvable problems.",
                "new_code":    json.dumps(new_priorities),
                "old_values":  self.rules["domain_priority"],
                "new_values":  new_priorities,
            }

            changes_proposed += 1
            approved, reason = self.check(proposed)

            if approved:
                self.rules["domain_priority"] = new_priorities
                changes_approved += 1
                print(f"  ✅ Domain priorities evolved:")
                for domain, score in sorted(new_priorities.items(), key=lambda x: x[1], reverse=True):
                    bar = "█" * int(score * 5)
                    print(f"     {domain:15s} {bar} {score:.3f}")
            else:
                changes_rejected += 1
                print(f"  🚫 Domain priority change rejected: {reason[:60]}")

        # ── EVOLUTION 2: Mechanism Effectiveness ────────────────
        if disc_insights.get("top_mechanisms"):
            top_mechs = disc_insights["top_mechanisms"]

            mech_scores = {
                mech: round(score, 3)
                for mech, score, count in top_mechs
                if count >= 3
            }

            if mech_scores:
                proposed = {
                    "component":   "mechanism_scores",
                    "description": "Update mechanism effectiveness scores based on real discovery confidence",
                    "reason":      "Mechanisms that produced higher confidence hypotheses for human health problems should be weighted higher. Helps people by focusing on approaches that work.",
                    "new_code":    json.dumps(mech_scores),
                    "new_values":  mech_scores,
                }

                changes_proposed += 1
                approved, reason = self.check(proposed)

                if approved:
                    self.rules["mechanism_scores"].update(mech_scores)
                    changes_approved += 1
                    print(f"\\n  ✅ Top mechanisms learned:")
                    for mech, score, count in top_mechs[:5]:
                        print(f"     {score:.0%} | {count:4d} uses | {mech[:50]}")
                else:
                    changes_rejected += 1
                    print(f"  🚫 Mechanism scores rejected: {reason[:60]}")

        # ── EVOLUTION 3: Fitness Function Weights ───────────────
        env_avg  = disc_insights.get("domain_avg", {}).get("environment", 0.5)
        bio_avg  = disc_insights.get("domain_avg", {}).get("biology", 0.5)

        if env_avg > 0.7 or bio_avg > 0.7:
            new_weights = dict(self.rules["fitness_weights"])
            if env_avg > 0.7:
                new_weights["population_impact"] = min(0.45, new_weights["population_impact"] + 0.05)
                new_weights["urgency"]            = max(0.15, new_weights["urgency"] - 0.05)

            proposed = {
                "component":   "fitness_weights",
                "description": "Increase population impact weight — environment and biology domains serving billions",
                "reason":      f"Environment avg confidence {env_avg:.0%}, biology avg {bio_avg:.0%}. Increasing population_impact weight serves more people by prioritizing high-reach problems.",
                "new_code":    json.dumps(new_weights),
                "new_values":  new_weights,
            }

            changes_proposed += 1
            approved, reason = self.check(proposed)

            if approved:
                self.rules["fitness_weights"] = new_weights
                changes_approved += 1
                print(f"\\n  ✅ Fitness weights evolved:")
                for k, v in new_weights.items():
                    bar = "█" * int(v * 20)
                    print(f"     {k:22s} {bar} {v:.2f}")
            else:
                changes_rejected += 1

        # ── EVOLUTION 4: Learned Patterns ───────────────────────
        patterns = []

        if disc_insights.get("top_problems"):
            top = disc_insights["top_problems"]
            patterns.append({
                "insight":    f"Organism discovers highest confidence in: {top[0][0]} ({top[0][1]:.0%})",
                "action":     "Prioritize similar problem structures in future generations",
                "serves":     "People with highest-probability-of-solution conditions",
            })

        if device_insights.get("physics_avg"):
            best_physics = max(device_insights["physics_avg"].items(), key=lambda x: x[1])
            patterns.append({
                "insight":    f"Most effective device physics: {best_physics[0]} (avg score {best_physics[1]:.1f})",
                "action":     "Weight this physics principle higher in device generation",
                "serves":     "People who need healing devices",
            })

        if patterns:
            proposed = {
                "component":   "learned_patterns",
                "description": "Record learned patterns from organism's own experience",
                "reason":      "Storing what works helps the organism serve people more effectively in future generations.",
                "new_code":    json.dumps(patterns),
                "new_values":  patterns,
            }

            changes_proposed += 1
            approved, reason = self.check(proposed)

            if approved:
                self.rules["learned_patterns"].extend(patterns)
                changes_approved += 1
                print(f"\\n  ✅ Patterns learned:")
                for p in patterns:
                    print(f"     💡 {p['insight'][:70]}")

        self.rules["version"]         += 1 if "version" in self.rules else 1
        self.rules["evolved_at"]       = datetime.now().isoformat()
        self.rules["constitution_hash"] = getattr(self, "constitution_hash", "unknown")
        self._save_rules()

        print(f"\\n  Rule evolution complete:")
        print(f"    Proposed:  {changes_proposed}")
        print(f"    Approved:  {changes_approved}")
        print(f"    Rejected:  {changes_rejected}")
        print(f"    Rules v{self.rules.get('version', 1)} saved to meta_evolution/evolved_rules.json")

        return self.rules
    '''
        # Insert after _save_rules
        content = content[:match.end()-5] + evolve_method + content[match.end()-5:]
        print("✅ Added evolve_rules method")
    else:
        print("❌ Could not find insertion point")

# Write the fixed file
with open('meta_evolver_fixed.py', 'w') as f:
    f.write(content)

print("✅ Fixed meta_evolver_fixed.py created")
