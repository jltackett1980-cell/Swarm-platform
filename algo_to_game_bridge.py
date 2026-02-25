import json
from pathlib import Path

HOME = Path.home()
lib = json.loads((HOME / "MASTER_ALGORITHMS/master_algorithm_library.json").read_text())
champs = lib['champions']

print("=== ALGORITHM CHAMPIONS → GAME ENGINE ===")
for family, c in champs.items():
    print(f"  {family:12} : {c['name']:30} fitness:{c['fitness']} mutation:{c['mutation']}")

# Write summary for game generator to read
out = {
    "game_ai": champs['game_ai'],
    "physics": champs['physics'],
    "rendering": champs['rendering'],
    "optimization": champs['optimization'],
    "control": champs['control'],
    "graph": champs['graph']
}
(HOME / "SWARM_GAMES" / "active_algorithms.json").write_text(json.dumps(out, indent=2))
print(f"\n✅ Active algorithms saved to ~/SWARM_GAMES/active_algorithms.json")
print(f"   game_ai:      {champs['game_ai']['name']} (fitness {champs['game_ai']['fitness']})")
print(f"   control(MPC): {champs['control']['name']} (fitness {champs['control']['fitness']})")
print(f"   graph(path):  {champs['graph']['name']} (fitness {champs['graph']['fitness']})")
