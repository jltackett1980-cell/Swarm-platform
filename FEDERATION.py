#!/usr/bin/env python3
"""
FEDERATION - Shares champion insights between nodes
No data leaves. Only code. Federated evolution.
"""
import json, time, shutil, subprocess
from pathlib import Path
from datetime import datetime

home = Path.home()
CHAMPIONS_DIR = home / "ORGANISM_ARMY" / "champions"
CONFIGS_FILE = home / "organism_templates" / "domain_configs.json"
FEDERATION_DIR = home / "swarm-platform" / "federation"
LOG_FILE = home / "ORGANISM_ARMY" / "federation.log"

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
    """Same scoring as Governor — must stay in sync"""
    import re
    score = 0
    path = Path(path)
    backend = path / "backend" / "app.py"
    frontend = path / "frontend" / "src" / "App.js"

    if backend.exists():
        content = backend.read_text()
        if domain_config:
            expected = [f[0] for f in domain_config.get("fields", [])]
            generic = {"name","details","status","id","created_at"}
            real = [f for f in expected if f not in generic]
            found = sum(1 for f in real if f in content)
            score += int((found / max(len(real), 1)) * 60)
        routes = len(re.findall(r"@app\.route\(", content))
        score += min(routes * 5, 30)
        if "jwt" in content.lower(): score += 10
        if "login" in content and "password" in content: score += 10
        if "JOIN" in content.upper() or "FOREIGN KEY" in content.upper(): score += 20
        elif content.count("CREATE TABLE") > 2: score += 10
        if "try:" in content and "except" in content: score += 5
        if "LIKE" in content or "search" in content.lower(): score += 10

    if frontend.exists():
        content = frontend.read_text()
        if "fetch(" in content: score += 10
        if "/api/" in content: score += 10
        if "onChange" in content: score += 5
        if "useState" in content: score += 5
        if domain_config:
            expected = [f[0] for f in domain_config.get("fields", [])]
            found = sum(1 for f in expected if f in content)
            score += min(found * 3, 15)

    return score

def push_champions():
    """Export local champions to federation folder for git push"""
    configs = load_configs()
    FEDERATION_DIR.mkdir(exist_ok=True)
    pushed = 0
    for domain_id in configs:
        champ = get_champion(domain_id)
        if not champ:
            continue
        champ_dir = CHAMPIONS_DIR / domain_id
        fed_dir = FEDERATION_DIR / domain_id
        fed_dir.mkdir(exist_ok=True)

        # Copy backend and frontend
        for folder in ["backend", "frontend"]:
            src = champ_dir / folder
            dst = fed_dir / folder
            if src.exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)

        # Write metadata
        (fed_dir / "node_champion.json").write_text(json.dumps({
            "domain": domain_id,
            "name": champ["name"],
            "score": champ["score"],
            "generation": champ.get("generation", 1),
            "node": get_node_id(),
            "shared_at": datetime.now().isoformat()
        }, indent=2))
        pushed += 1

    log(f"📤 Pushed {pushed} champions to federation")

def pull_and_evolve():
    """Pull from git, score incoming champions, crown if better"""
    configs = load_configs()

    # Git pull
    result = subprocess.run(
        ["git", "pull", "origin", "main"],
        cwd=home / "swarm-platform",
        capture_output=True, text=True
    )
    log(f"🔄 Git pull: {result.stdout.strip() or result.stderr.strip()}")

    if "Already up to date" in result.stdout:
        log("  No new insights from network")
        return

    # Score incoming federation apps
    improved = 0
    for domain_id, cfg in configs.items():
        fed_dir = FEDERATION_DIR / domain_id
        if not fed_dir.exists():
            continue

        meta_file = fed_dir / "node_champion.json"
        if not meta_file.exists():
            continue

        meta = json.loads(meta_file.read_text())

        # Don't process our own pushes
        if meta.get("node") == get_node_id():
            continue

        incoming_score = score_app(fed_dir, cfg)
        local_champ = get_champion(domain_id)
        local_score = local_champ.get("score", 0) if local_champ else 0

        if incoming_score > local_score:
            # Crown the incoming champion
            champ_dir = CHAMPIONS_DIR / domain_id
            champ_dir.mkdir(parents=True, exist_ok=True)
            for item in champ_dir.iterdir():
                if item.name != "champion.json":
                    if item.is_dir(): shutil.rmtree(item)
                    else: item.unlink()
            for folder in ["backend", "frontend"]:
                src = fed_dir / folder
                if src.exists():
                    shutil.copytree(src, champ_dir / folder)
            generation = (local_champ.get("generation", 1) + 1) if local_champ else 1
            (champ_dir / "champion.json").write_text(json.dumps({
                "domain": domain_id,
                "name": cfg["name"],
                "icon": cfg.get("icon", ""),
                "score": incoming_score,
                "generation": generation,
                "source_node": meta.get("node", "unknown"),
                "crowned_at": datetime.now().isoformat()
            }, indent=2))
            log(f"🌐 FEDERATED CHAMPION: {cfg['name']} from node {meta.get('node','?')} score {incoming_score} > {local_score}")
            improved += 1

    if improved:
        log(f"  Adopted {improved} insights from network")

def push_to_git():
    """Commit and push federation folder"""
    repo = home / "swarm-platform"
    subprocess.run(["git", "add", "federation/"], cwd=repo, capture_output=True)
    result = subprocess.run(
        ["git", "commit", "-m", f"Federation update {datetime.now().strftime('%Y%m%d_%H%M%S')} node:{get_node_id()}"],
        cwd=repo, capture_output=True, text=True
    )
    if "nothing to commit" in result.stdout + result.stderr:
        log("  No changes to push")
        return
    push = subprocess.run(["git", "push", "origin", "main"], cwd=repo, capture_output=True, text=True)
    log(f"📡 Git push: {push.stdout.strip() or push.stderr.strip()}")

def get_node_id():
    """Unique ID for this node"""
    id_file = home / ".swarm_node_id"
    if id_file.exists():
        return id_file.read_text().strip()
    import hashlib, socket
    node_id = hashlib.md5(socket.gethostname().encode()).hexdigest()[:8]
    id_file.write_text(node_id)
    return node_id

def run():
    node_id = get_node_id()
    log(f"🌐 FEDERATION ONLINE - Node: {node_id}")
    log(f"   Sharing insights across the swarm")

    cycle = 0
    while True:
        cycle += 1
        time.sleep(600)  # Every 10 minutes

        log(f"\n--- Federation cycle {cycle} ---")
        try:
            push_champions()
            push_to_git()
            pull_and_evolve()
        except Exception as e:
            log(f"⚠️  Federation error: {e}")

if __name__ == "__main__":
    run()
