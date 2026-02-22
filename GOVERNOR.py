#!/usr/bin/env python3
"""
THE GOVERNOR - Oversees all 30 domain champions
"""
import json, time, shutil
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

def score_app(path):
    score = 0
    path = Path(path)
    backend = path / "backend" / "app.py"
    frontend = path / "frontend" / "src" / "App.js"
    if backend.exists():
        content = backend.read_text()
        score += len(content.split('\n'))
        if 'token_required' in content: score += 50
        if 'sqlite3' in content: score += 50
        if '/api/records' in content: score += 30
    if frontend.exists():
        content = frontend.read_text()
        score += len(content.split('\n'))
        if 'Login' in content: score += 50
        if 'modal' in content.lower(): score += 30
    return score

def print_status():
    configs = load_configs()
    log("\n=== DOMAIN ARMY STATUS ===")
    crowned = 0
    for domain_id, cfg in configs.items():
        champ = get_champion(domain_id)
        if champ:
            log(f"  {cfg.get('icon','🏢')} {cfg.get('name','?'):25} Score: {champ['score']:4} | Gen: {champ.get('generation',1)}")
            crowned += 1
        else:
            log(f"  {cfg.get('icon','🏢')} {cfg.get('name','?'):25} No champion yet")
    log(f"\n  Crowned: {crowned}/{len(configs)} domains")
    log("="*40)

def check_new_apps(configs):
    kw_file = home / "organism_templates" / "keyword_map.json"
    kw_map = json.loads(kw_file.read_text()) if kw_file.exists() else {}
    new_apps = sorted(home.glob("professional_app_*"),
        key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    for app_path in new_apps:
        app_js = app_path / "frontend" / "src" / "App.js"
        if not app_js.exists(): continue
        content = app_js.read_text()
        domain_id = None
        for line in content.split('\n'):
            if 'const APP_NAME' in line and "'" in line:
                app_name = line.split("'")[1]
                for did, cfg in configs.items():
                    if cfg.get('name','') == app_name:
                        domain_id = did
                        break
                break
        if not domain_id: continue
        new_score = score_app(app_path)
        champ = get_champion(domain_id)
        current_score = champ.get('score', 0) if champ else 0
        if new_score > current_score:
            champion_dir = CHAMPIONS_DIR / domain_id
            for item in champion_dir.iterdir():
                if item.name != 'champion.json':
                    if item.is_dir(): shutil.rmtree(item)
                    else: item.unlink()
            shutil.copytree(app_path / "backend", champion_dir / "backend")
            shutil.copytree(app_path / "frontend", champion_dir / "frontend")
            generation = (champ.get('generation', 1) + 1) if champ else 1
            (champion_dir / "champion.json").write_text(json.dumps({
                "domain": domain_id,
                "name": configs[domain_id]["name"],
                "icon": configs[domain_id]["icon"],
                "score": new_score,
                "generation": generation,
                "crowned_at": datetime.now().isoformat(),
                "source": str(app_path)
            }, indent=2))
            log(f"👑 NEW CHAMPION: {configs[domain_id]['name']} gen {generation} (score: {new_score} > {current_score})")

def run():
    log("👑 GOVERNOR ONLINE")
    configs = load_configs()
    log(f"   Overseeing {len(configs)} domains")
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
