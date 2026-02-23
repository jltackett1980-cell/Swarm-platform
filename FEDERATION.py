#!/usr/bin/env python3
"""
FEDERATION.py
Swarm Platform - Peer-to-peer champion sharing
Author: Jason Tackett
License: Copyright 2026, all rights reserved
"""

import hashlib
import json
import re
import shutil
import socket
import subprocess
import time
from datetime import datetime
from pathlib import Path

HOME = Path.home()
SWARM_DIR = HOME / "swarm-platform"
CHAMPIONS_DIR = HOME / "ORGANISM_ARMY" / "champions"
CONFIGS_FILE = HOME / "organism_templates" / "domain_configs.json"
FEDERATION_DIR = SWARM_DIR / "federation"
LOG_FILE = HOME / "federation.log"
NODE_ID_FILE = HOME / ".swarm_node_id"


def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def get_node_id():
    try:
        if NODE_ID_FILE.exists():
            return NODE_ID_FILE.read_text().strip()
        node_id = hashlib.md5(socket.gethostname().encode()).hexdigest()[:8]
        NODE_ID_FILE.write_text(node_id)
        return node_id
    except Exception:
        return "unknown"


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


def score_app(path, domain_config=None):
    score = 0
    path = Path(path)
    backend = path / "backend" / "app.py"
    html = path / "frontend" / "index.html"
    app_js = path / "frontend" / "src" / "App.js"
    frontend_content = ""
    if html.exists():
        frontend_content = html.read_text()
    elif app_js.exists():
        frontend_content = app_js.read_text()
    if backend.exists():
        try:
            content = backend.read_text()
            if domain_config:
                expected = [f[0] for f in domain_config.get("fields", [])]
                reserved = {"name", "details", "status", "id", "created_at"}
                real = [f for f in expected if f not in reserved]
                if real:
                    found = sum(1 for f in real if f in content)
                    score += int((found / len(real)) * 60)
            routes = len(re.findall(r"@app\.route\(", content))
            score += min(routes * 5, 30)
            if "jwt" in content.lower():
                score += 10
            if "login" in content and "password" in content:
                score += 10
            if "JOIN" in content.upper() or "FOREIGN KEY" in content.upper():
                score += 20
            elif content.count("CREATE TABLE") > 2:
                score += 10
            if "try:" in content and "except" in content:
                score += 5
            if "LIKE" in content or "search" in content.lower():
                score += 10
        except Exception:
            pass
    if frontend_content:
        try:
            if "fetch(" in frontend_content:
                score += 10
            if "/api/" in frontend_content:
                score += 10
            if domain_config:
                expected = [f[0] for f in domain_config.get("fields", [])]
                found = sum(1 for f in expected if f in frontend_content)
                score += min(found * 3, 15)
            if "onChange" in frontend_content or "getElementById" in frontend_content:
                score += 10
        except Exception:
            pass
    return score


def git_run(args):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=SWARM_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return f"git error: {e}"


def push_champions(configs, node_id):
    FEDERATION_DIR.mkdir(exist_ok=True)
    pushed = 0
    for domain_id, cfg in configs.items():
        try:
            champ = get_champion(domain_id)
            if not champ:
                continue
            champ_dir = CHAMPIONS_DIR / domain_id
            fed_dir = FEDERATION_DIR / domain_id
            fed_dir.mkdir(exist_ok=True)
            for folder in ["backend", "frontend"]:
                src = champ_dir / folder
                dst = fed_dir / folder
                if src.exists():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
            (fed_dir / "node_champion.json").write_text(json.dumps({
                "domain": domain_id,
                "name": champ.get("name", ""),
                "score": champ.get("score", 0),
                "generation": champ.get("generation", 1),
                "node": node_id,
                "shared_at": datetime.now().isoformat()
            }, indent=2))
            pushed += 1
        except Exception as e:
            log(f"WARNING: Could not push {domain_id}: {e}")
    log(f"📤 Pushed {pushed} champions to federation")
    return pushed


def pull_and_evolve(configs, node_id):
    result = git_run(["pull", "origin", "main"])
    log(f"🔄 Git pull: {result}")
    if "Already up to date" in result:
        log("  No new insights from network")
        return 0
    improved = 0
    for domain_id, cfg in configs.items():
        try:
            fed_dir = FEDERATION_DIR / domain_id
            if not fed_dir.exists():
                continue
            meta_file = fed_dir / "node_champion.json"
            if not meta_file.exists():
                continue
            meta = json.loads(meta_file.read_text())
            if meta.get("node") == node_id:
                continue
            incoming_score = score_app(fed_dir, cfg)
            local_champ = get_champion(domain_id)
            local_score = local_champ.get("score", 0) if local_champ else 0
            if incoming_score > local_score:
                champ_dir = CHAMPIONS_DIR / domain_id
                champ_dir.mkdir(parents=True, exist_ok=True)
                for item in champ_dir.iterdir():
                    if item.name != "champion.json":
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                for folder in ["backend", "frontend"]:
                    src = fed_dir / folder
                    if src.exists():
                        shutil.copytree(src, champ_dir / folder)
                generation = (local_champ.get("generation", 1) + 1) if local_champ else 1
                (champ_dir / "champion.json").write_text(json.dumps({
                    "domain": domain_id,
                    "name": cfg.get("name", ""),
                    "icon": cfg.get("icon", ""),
                    "score": incoming_score,
                    "generation": generation,
                    "source_node": meta.get("node", "unknown"),
                    "crowned_at": datetime.now().isoformat()
                }, indent=2))
                log(f"🌐 FEDERATED CHAMPION: {cfg.get('name')} from node "
                    f"{meta.get('node','?')} score {incoming_score} > {local_score}")
                improved += 1
        except Exception as e:
            log(f"WARNING: Could not process federation for {domain_id}: {e}")
    if improved:
        log(f"  Adopted {improved} insights from network")
    return improved


def push_to_git(node_id):
    git_run(["add", "federation/"])
    result = git_run([
        "commit", "-m",
        f"Federation update {datetime.now().strftime('%Y%m%d_%H%M%S')} node:{node_id}"
    ])
    if "nothing to commit" in result:
        log("  No changes to push")
        return
    push_result = git_run(["push", "origin", "main"])
    log(f"📡 Git push: {push_result}")


def run():
    node_id = get_node_id()
    log(f"🌐 FEDERATION ONLINE - Node: {node_id}")
    log(f"   Sharing insights across the swarm")
    cycle = 0
    while True:
        try:
            time.sleep(600)
            cycle += 1
            configs = load_configs()
            log(f"\n--- Federation cycle {cycle} ---")
            push_champions(configs, node_id)
            push_to_git(node_id)
            pull_and_evolve(configs, node_id)
        except Exception as e:
            log(f"ERROR in federation cycle: {e}")
            time.sleep(60)


if __name__ == "__main__":
    run()
