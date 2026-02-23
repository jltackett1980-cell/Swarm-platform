#!/usr/bin/env python3
"""
THE GOVERNOR - Real scoring based on domain quality
"""
import json, time, shutil, re
from pathlib import Path
from datetime import datetime

home = Path.home()
CHAMPIONS_DIR = home / "ORGANISM_ARMY" / "champions"
CONFIGS_FILE = home / "organism_templates" / "domain_configs.json"
LOG_FILE = home / "ORGANISM_ARMY" / "governor.log"

def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_configs():
    if CONFIGS_FILE.exists():
        return json.loads(CONFIGS_FILE.read_text())
    return {}

def get_champion(domain_id):
    cf = CHAMPIONS_DIR / domain_id / "champion.json"
    if cf.exists():
        return json.loads(cf.read_text())
    return None

def score_app(path, domain_config=None):
    """
    Real scoring criteria:
    - Domain fields present in schema (not just name/details)
    - Number of API routes
    - Auth wired up
    - Frontend makes API calls
    - Relationships between tables (foreign keys or joins)
    - Search/filter capability
    - Input validation
    """
    score = 0
    breakdown = {}
    path = Path(path)
    backend = path / "backend" / "app.py"
    frontend = path / "frontend" / "src" / "App.js"

    if backend.exists():
        content = backend.read_text()

        # Domain-specific fields (most important - 0 to 60 pts)
        domain_field_score = 0
        if domain_config:
            expected_fields = [f[0] for f in domain_config.get("fields", [])]
            generic = {"name", "details", "status", "id", "created_at"}
            real_fields = [f for f in expected_fields if f not in generic]
            found = sum(1 for f in real_fields if f in content)
            domain_field_score = int((found / max(len(real_fields), 1)) * 60)
        else:
            # No config - count non-generic columns
            cols = re.findall(r'"(\w+)\s+TEXT|INTEGER"', content)
            real = [c for c in cols if c not in {"id","name","details","status","created_at"}]
            domain_field_score = min(len(real) * 8, 60)
        score += domain_field_score
        breakdown["domain_fields"] = domain_field_score

        # Number of routes (0 to 30 pts)
        routes = len(re.findall(r"@app\.route\(", content))
        route_score = min(routes * 5, 30)
        score += route_score
        breakdown["routes"] = route_score

        # Auth present and wired (0 to 20 pts)
        auth_score = 0
        if "token_required" in content or "jwt" in content.lower():
            auth_score += 10
        if "login" in content and "password" in content:
            auth_score += 10
        score += auth_score
        breakdown["auth"] = auth_score

        # Table relationships / joins (0 to 20 pts)
        rel_score = 0
        if "JOIN" in content.upper() or "FOREIGN KEY" in content.upper():
            rel_score += 20
        elif "INTEGER" in content and content.count("CREATE TABLE") > 2:
            rel_score += 10  # multiple tables at least
        score += rel_score
        breakdown["relationships"] = rel_score

        # Input validation (0 to 10 pts)
        val_score = 0
        if "if not data" in content or "required" in content.lower():
            val_score += 5
        if "try:" in content and "except" in content:
            val_score += 5
        score += val_score
        breakdown["validation"] = val_score

        # Search/filter endpoint (0 to 10 pts)
        search_score = 0
        if "search" in content.lower() or "filter" in content.lower() or "LIKE" in content:
            search_score += 10
        score += search_score
        breakdown["search"] = search_score

    if frontend.exists():
        content = frontend.read_text()

        # Frontend actually calls API (0 to 20 pts)
        api_score = 0
        if "fetch(" in content or "axios" in content:
            api_score += 10
        if "/api/" in content:
            api_score += 10
        score += api_score
        breakdown["api_calls"] = api_score

        # UI has real domain fields rendered (0 to 15 pts)
        ui_score = 0
        if domain_config:
            expected_fields = [f[0] for f in domain_config.get("fields", [])]
            found_in_ui = sum(1 for f in expected_fields if f in content)
            ui_score = min(found_in_ui * 3, 15)
        score += ui_score
        breakdown["ui_fields"] = ui_score

        # Forms present (0 to 10 pts)
        form_score = 0
        if "onChange" in content or "setValue" in content:
            form_score += 5
        if "useState" in content:
            form_score += 5
        score += form_score
        breakdown["forms"] = form_score

    breakdown["total"] = score
    return score, breakdown

def print_status():
    configs = load_configs()
    log("\n=== DOMAIN ARMY STATUS ===")
    crowned = 0
    for domain_id, cfg in configs.items():
        champ = get_champion(domain_id)
        if champ:
            log(f"  {cfg.get('icon','🏢')} {cfg.get('name','?'):25} Score: {champ['score']:4} | Gen: {champ.get('generation',1)} | {champ.get('breakdown',{})}")
            crowned += 1
        else:
            log(f"  {cfg.get('icon','🏢')} {cfg.get('name','?'):25} No champion yet")
    log(f"\n  Crowned: {crowned}/{len(configs)} domains")
    log("="*40)

def check_new_apps(configs):
    new_apps = sorted(home.glob("professional_app_*"),
        key=lambda p: p.stat().st_mtime, reverse=True)[:10]

    for app_path in new_apps:
        html = app_path / "frontend" / "index.html"
        app_js = app_path / "frontend" / "src" / "App.js"
        if html.exists():
            content = html.read_text()
        elif app_js.exists():
            content = app_js.read_text()
        else:
            continue

        # Identify domain from title tag
        domain_id = None
        domain_config = None
        for did, cfg in configs.items():
            if cfg.get("name","") in content:
                domain_id = did
                domain_config = cfg
                break

        if not domain_id:
            continue

        new_score, breakdown = score_app(app_path, domain_config)
        champ = get_champion(domain_id)
        current_score = champ.get('score', 0) if champ else 0

        if new_score > current_score:
            champion_dir = CHAMPIONS_DIR / domain_id
            champion_dir.mkdir(parents=True, exist_ok=True)
            for item in champion_dir.iterdir():
                if item.name != 'champion.json':
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
            shutil.copytree(app_path / "backend", champion_dir / "backend")
            shutil.copytree(app_path / "frontend", champion_dir / "frontend")
            generation = (champ.get('generation', 1) + 1) if champ else 1
            (champion_dir / "champion.json").write_text(json.dumps({
                "domain": domain_id,
                "name": configs[domain_id]["name"],
                "icon": configs[domain_id]["icon"],
                "score": new_score,
                "breakdown": breakdown,
                "generation": generation,
                "crowned_at": datetime.now().isoformat(),
                "source": str(app_path)
            }, indent=2))
            log(f"👑 NEW CHAMPION: {configs[domain_id]['name']} gen {generation} | score {new_score} > {current_score} | {breakdown}")
        else:
            log(f"  ↩ {configs[domain_id]['name']} scored {new_score} — champion holds at {current_score}")

def run():
    log("👑 GOVERNOR ONLINE - Real Scoring Active")
    configs = load_configs()
    log(f"   Overseeing {len(configs)} domains")
    CHAMPIONS_DIR.mkdir(parents=True, exist_ok=True)
    print_status()
    cycle = 0
    while True:
        cycle += 1
        time.sleep(300)
        check_new_apps(configs)
        if cycle % 6 == 0:
            print_status()

if __name__ == "__main__":
    run()
