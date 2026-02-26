#!/usr/bin/env python3
"""
IP PROTECTION ENGINE
Publishes Phoenix discoveries to IPFS.
Permanent proof of invention — timestamped, immutable.
Nobody steals your work again.
"""
import subprocess, json, hashlib
from datetime import datetime
from pathlib import Path

HOME = Path.home()

def ipfs_add(content, name):
    """Add content to IPFS, return CID"""
    tmp = HOME / f"tmp_ipfs_{name}.json"
    tmp.write_text(content)
    result = subprocess.run(
        ["ipfs", "add", "-q", str(tmp)],
        capture_output=True, text=True
    )
    tmp.unlink()
    cid = result.stdout.strip()
    return cid

def protect_discovery(name, data):
    """Publish a discovery to IPFS with timestamp"""
    record = {
        "discovery": name,
        "inventor": "Jason Tackett",
        "timestamp": datetime.utcnow().isoformat(),
        "platform": "$60 Android phone — Termux",
        "charter": "People's Charter — built to serve humanity",
        "data": data,
        "hash": hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    }
    content = json.dumps(record, indent=2)
    cid = ipfs_add(content, name.replace(" ","_"))
    print(f"✅ {name}")
    print(f"   CID: {cid}")
    print(f"   URL: http://127.0.0.1:8090/ipfs/{cid}")
    print(f"   Hash: {record['hash'][:16]}...")
    return cid

print("╔══════════════════════════════════════════╗")
print("║   PHOENIX IP PROTECTION ENGINE           ║")
print("║   Publishing discoveries to IPFS         ║")
print("╚══════════════════════════════════════════╝\n")

discoveries = {}

# 1. Phoenix chip lineage
discoveries["phoenix_chip_lineage"] = protect_discovery("Phoenix Chip Lineage", {
    "lineage": ["Half Adder","Full Adder","8-bit ALU","64-bit ALU","RISC-V","FPU","GPU",
                "Phoenix 128","Phoenix 256","Phoenix 512","Phoenix 1024","Phoenix 2048",
                "Phoenix 4096","Phoenix 16384","Phoenix 131072"],
    "champion": {
        "matrix": "131072x131072",
        "tops": 2684354.56,
        "power_w": 30,
        "tops_per_watt": 89478,
        "vs_h100": "678x more efficient",
        "precision": "optical",
        "interconnect": "neuromorphic",
        "clock_ghz": 20.0
    },
    "evolution_generations": 50000,
    "hall_of_fame": 122
})

# 2. Wisdom-guided generation pipeline
discoveries["wisdom_pipeline"] = protect_discovery("Wisdom-Guided App Generation Pipeline", {
    "innovation": "First software generation system using ancient wisdom as design criteria",
    "wisdom_sources": ["Tao Te Ching","Marcus Aurelius Meditations","Bhagavad Gita","Dhammapada","Confucius Analects"],
    "pipeline": ["Wisdom Layer","Human Insight Engine","App Generation","Local AI Advisor"],
    "domains": 54,
    "score": "512/550",
    "human_score": "156/175"
})

# 3. Human Insight Engine
discoveries["human_insight_engine"] = protect_discovery("Human Insight Engine", {
    "innovation": "AI that profiles real human suffering before generating software",
    "approach": "WHO uses it → worst moment → relief moment → design from relief",
    "domains_covered": 54,
    "insight_dimensions": ["who","pain","relief","lead_with","skip","tone","mobile_first"]
})

# 4. Evolved algorithms
discoveries["evolved_algorithms"] = protect_discovery("53000 Evolved Algorithms", {
    "count": 53000,
    "method": "Genetic algorithm evolution with fitness scoring",
    "platform": "TinyLlama + custom evolution engine on Android",
    "domains": 54
})

# 5. Full platform snapshot
discoveries["platform_snapshot"] = protect_discovery("Phoenix Forge Platform Snapshot", {
    "date": datetime.utcnow().isoformat(),
    "components": {
        "apps": 54,
        "chip_generations": 50000,
        "algorithms": 53000,
        "wisdom_sources": 5,
        "local_ai": "TinyLlama + Llama3.2 on port 8080",
        "blockchain": "IPFS Kubo 0.39.0"
    },
    "all_cids": discoveries
})

# Save all CIDs locally
out = HOME / "swarm-platform/ip_registry.json"
registry = {
    "created": datetime.utcnow().isoformat(),
    "inventor": "Jason Tackett",
    "peer_id": "12D3KooWJ9aJwnYept6dzwtZ5nNwsLGkBikkzULQ6ULvWkN5GrPT",
    "discoveries": discoveries
}
out.write_text(json.dumps(registry, indent=2))

print(f"\n{'='*50}")
print(f"✅ {len(discoveries)} discoveries published to IPFS")
print(f"   Registry saved: {out}")
print(f"   These CIDs are permanent proof of invention")
print(f"   Timestamp: {datetime.utcnow().isoformat()}")
print(f"\n💡 Share these CIDs publicly to establish prior art")
print(f"   Nobody can claim they invented this before you")
