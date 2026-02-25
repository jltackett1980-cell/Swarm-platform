#!/usr/bin/env python3
"""
GOVERNOR.py
Swarm Platform - Scoring and Champion Selection
Author: Jason Tackett
License: Copyright 2026, all rights reserved
"""

import json
import re
import shutil
import time
from datetime import datetime
from pathlib import Path

HOME = Path.home()
CHAMPIONS_DIR = HOME / "ORGANISM_ARMY" / "champions"
CONFIGS_FILE = HOME / "organism_templates" / "domain_configs.json"
LOG_FILE = HOME / "governor.log"


def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_configs():
    try:
        if CONFIGS_FILE.exists():
            return json.loads(CONFIGS_FILE.read_text())
    except Exception as e:
        log(f"WARNING: Could not load configs: {e}")
    return {}


def get_champion(domain_id):
    try:
        cf = CHAMPIONS_DIR / domain_id / "champion.json"
        if cf.exists():
            return json.loads(cf.read_text())
    except Exception:
        pass
    return None


def save_champion(domain_id, cfg, score, breakdown, app_path):
    try:
        champ = get_champion(domain_id)
        generation = (champ.get("generation", 1) + 1) if champ else 1
        champ_dir = CHAMPIONS_DIR / domain_id
        champ_dir.mkdir(parents=True, exist_ok=True)
        for item in champ_dir.iterdir():
            if item.name != "champion.json":
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                except Exception:
                    pass
        for folder in ["backend", "frontend"]:
            src = app_path / folder
            if src.exists():
                shutil.copytree(src, champ_dir / folder)
        (champ_dir / "champion.json").write_text(json.dumps({
            "domain": domain_id,
            "name": cfg.get("name", domain_id),
            "icon": cfg.get("icon", ""),
            "score": score,
            "breakdown": breakdown,
            "generation": generation,
            "crowned_at": datetime.now().isoformat(),
            "source_app": str(app_path.name)
        }, indent=2))
        return generation
    except Exception as e:
        log(f"ERROR saving champion for {domain_id}: {e}")
        return 1



def score_app(path, domain_config=None):
    """Enhanced scoring function with human-centric criteria"""
    score = 0
    breakdown = {
        "domain_fields": 0, "routes": 0, "auth": 0,
        "relationships": 0, "validation": 0, "search": 0,
        "api_calls": 0, "ui_fields": 0, "forms": 0,
        "loading_states": 0, "responsive": 0, "notifications": 0,
        "api_versioning": 0, "rate_limiting": 0, "pagination": 0,
        "audit_trail": 0, "error_handling": 0,
        "persona_alignment": 0,
        "pain_resolution": 0,
        "lead_with": 0,
        "one_tap_actions": 0,
        "offline_capability": 0,
        "mobile_ux": 0,
        "no_cruft": 0,
        "tone_alignment": 0
    }
    
    path = Path(path)
    backend = path / "backend" / "app.py"
    html_file = path / "frontend" / "index.html"
    app_js = path / "frontend" / "src" / "App.js"
    manifest_file = path / "frontend" / "manifest.json"
    css_files = list((path / "frontend" / "src").glob("*.css"))
    
    frontend_content = ""
    if html_file.exists():
        frontend_content = html_file.read_text()
    elif app_js.exists():
        frontend_content = app_js.read_text()
    
    domain_name = "unknown"
    if domain_config:
        domain_name = domain_config.get("name", "unknown")
    insight = HUMAN_INSIGHTS.get(domain_name, {})
    
    # ORIGINAL BACKEND SCORING
    if backend.exists():
        try:
            content = backend.read_text()
            
            if domain_config:
                expected = [f[0] for f in domain_config.get("fields", [])]
                reserved = {"name", "details", "status", "id", "created_at"}
                real = [f for f in expected if f not in reserved]
                if real:
                    found = sum(1 for f in real if f in content)
                    breakdown["domain_fields"] = int((found / len(real)) * 60)
            
            routes = len(re.findall(r"@app\.route\(", content))
            breakdown["routes"] = min(routes * 5, 30)
            
            auth = 0
            if "jwt" in content.lower():
                auth += 10
            if "login" in content and "password" in content:
                auth += 10
            breakdown["auth"] = auth
            
            if "JOIN" in content.upper() or "FOREIGN KEY" in content.upper():
                breakdown["relationships"] = 20
            elif content.count("CREATE TABLE") > 2:
                breakdown["relationships"] = 10
            
            if "try:" in content and "except" in content:
                breakdown["validation"] = 5
            if "get_json()" in content and "400" in content:
                breakdown["validation"] = 10
            
            if "LIKE" in content or "search" in content.lower():
                breakdown["search"] = 10
                
        except Exception as e:
            print(f"WARNING: Could not score backend: {e}")
    
    # ORIGINAL FRONTEND SCORING
    if frontend_content:
        try:
            if "fetch(" in frontend_content:
                breakdown["api_calls"] += 10
            if "axios" in frontend_content:
                breakdown["api_calls"] += 10
            
            if domain_config:
                expected = [f[0] for f in domain_config.get("fields", [])]
                found_ui = sum(1 for f in expected if f in frontend_content)
                breakdown["ui_fields"] = int((found_ui / len(expected)) * 15) if expected else 0
            
            if "<form" in frontend_content or "form>" in frontend_content:
                breakdown["forms"] = 10
            
            if "loading" in frontend_content.lower() or "spinner" in frontend_content.lower():
                breakdown["loading_states"] = 10
            
            if "viewport" in frontend_content or "@media" in frontend_content:
                breakdown["responsive"] = 10
            
            if "toast" in frontend_content or "alert" in frontend_content:
                breakdown["notifications"] = 10
            
            if "/api/v1" in frontend_content or "/v1/" in frontend_content:
                breakdown["api_versioning"] = 10
            
            if "X-RateLimit" in frontend_content:
                breakdown["rate_limiting"] = 10
            
            if ".slice" in frontend_content or ".limit" in frontend_content:
                breakdown["pagination"] = 10
            
            if "audit" in frontend_content.lower() or "log" in frontend_content.lower():
                breakdown["audit_trail"] = 10
            
            if "try" in frontend_content and "catch" in frontend_content:
                breakdown["error_handling"] = 10
                
        except Exception as e:
            print(f"WARNING: Could not score frontend: {e}")
    
    # HUMAN-CENTRIC SCORING
    # 1. PERSONA ALIGNMENT (30 pts)
    persona_score = 0
    who = insight.get("who", "").lower()
    
    if "nurse" in who or "coordinator" in who:
        if "patient lookup" in frontend_content.lower() or "search" in frontend_content.lower():
            persona_score += 10
        if "today" in frontend_content.lower() or "appointment" in frontend_content.lower():
            persona_score += 10
        if "quick" in frontend_content.lower() and "onclick=" in frontend_content:
            persona_score += 10
    elif "owner" in who or "cook" in who or "manager" in who:
        if "order" in frontend_content.lower() and "table" in frontend_content.lower():
            persona_score += 10
        if "kitchen" in frontend_content.lower() or "status" in frontend_content.lower():
            persona_score += 10
        if "large" in frontend_content.lower() or "big button" in frontend_content.lower():
            persona_score += 10
    elif "pharmacist" in who:
        if "prescription" in frontend_content.lower() or "rx" in frontend_content.lower():
            persona_score += 10
        if "ready" in frontend_content.lower() and "pending" in frontend_content.lower():
            persona_score += 10
        if "queue" in frontend_content.lower() or "waiting" in frontend_content.lower():
            persona_score += 10
    
    breakdown["persona_alignment"] = min(30, persona_score)
    
    # 2. PAIN RESOLUTION (30 pts)
    pain_score = 0
    pain = insight.get("pain", "").lower()
    
    if "cannot find" in pain or "looking for" in pain:
        if "search" in frontend_content.lower() and "filter" in frontend_content.lower():
            pain_score += 15
        if "recent" in frontend_content.lower() or "history" in frontend_content.lower():
            pain_score += 15
    elif "rush" in pain or "busy" in pain or "behind" in pain:
        if "quick" in frontend_content.lower() and ("click" in frontend_content.lower() or "tap" in frontend_content.lower()):
            pain_score += 15
        if "shortcut" in frontend_content.lower() or "fast" in frontend_content.lower():
            pain_score += 15
    
    breakdown["pain_resolution"] = min(30, pain_score)
    
    # Calculate total
    total = 0
    for key, value in breakdown.items():
        if key != "total":
            total += value
    
    breakdown["total"] = total
    return total, breakdown
    if frontend_content:
        try:
            # Loading states
            if "spinner" in frontend_content or "loading" in frontend_content.lower():
                breakdown["loading_states"] = 10
            if "viewport" in frontend_content and "media" in frontend_content:
                breakdown["responsive"] = 10
            if "toast" in frontend_content:
                breakdown["notifications"] = 10
        except:
            pass

    score = sum(v for k, v in breakdown.items())
    breakdown["total"] = score
    return score, breakdown


def check_new_apps(configs):
    try:
        new_apps = sorted(
            HOME.glob("professional_app_*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:10]
        crowned = 0
        for app_path in new_apps:
            try:
                html = app_path / "frontend" / "index.html"
                app_js = app_path / "frontend" / "src" / "App.js"
                if html.exists():
                    content = html.read_text()
                elif app_js.exists():
                    content = app_js.read_text()
                else:
                    continue
                domain_id = None
                domain_config = None
                for did, cfg in configs.items():
                    if cfg.get("name", "") in content:
                        domain_id = did
                        domain_config = cfg
                        break
                if not domain_id:
                    continue
                new_score, breakdown = score_app(app_path, domain_config)
                champ = get_champion(domain_id)
                current_score = champ.get("score", 0) if champ else 0
                if new_score > current_score:
                    generation = save_champion(domain_id, domain_config, new_score, breakdown, app_path)
                    log(f"👑 NEW CHAMPION: {domain_config.get('name')} gen {generation} | "
                        f"score {new_score} > {current_score} | {breakdown}")
                    crowned += 1
                else:
                    log(f"  ↩ {domain_config.get('name')} scored {new_score} — champion holds at {current_score}")
            except Exception as e:
                log(f"WARNING: Could not process {app_path.name}: {e}")
                continue
        return crowned
    except Exception as e:
        log(f"ERROR in check_new_apps: {e}")
        return 0


def display_status(configs):
    try:
        log("")
        log("=== DOMAIN ARMY STATUS ===")
        crowned = 0
        for domain_id, cfg in configs.items():
            champ = get_champion(domain_id)
            icon = cfg.get("icon", "")
            name = cfg.get("name", domain_id)
            if champ:
                score = champ.get("score", 0)
                gen = champ.get("generation", 1)
                breakdown = champ.get("breakdown", {})
                log(f"  {icon} {name:25} Score: {score:4} | Gen: {gen} | {breakdown}")
                crowned += 1
            else:
                log(f"  {icon} {name:25} No champion yet")
        log(f"\n  Crowned: {crowned}/{len(configs)} domains")
        log("=" * 40)
    except Exception as e:
        log(f"ERROR in display_status: {e}")


def run():
    CHAMPIONS_DIR.mkdir(parents=True, exist_ok=True)
    log("👑 GOVERNOR ONLINE - Real Scoring Active")
    configs = load_configs()
    log(f"   Overseeing {len(configs)} domains")
    display_status(configs)
    cycle = 0
    while True:
        try:
            time.sleep(300)
            cycle += 1
            configs = load_configs()
            log(f"\n--- Governor cycle {cycle} ---")
            crowned = check_new_apps(configs)
            if crowned:
                log(f"  Crowned {crowned} new champion(s) this cycle")
            display_status(configs)
        except Exception as e:
            log(f"ERROR in governor cycle: {e}")
            time.sleep(60)


if __name__ == "__main__":
    run()
