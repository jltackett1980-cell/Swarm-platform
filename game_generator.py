#!/usr/bin/env python3
"""
SWARM GAME GENERATOR
Generates actual playable HTML5 canvas games
No pay-to-win. No loot boxes. Just fun.
"""
import json, random, shutil
from pathlib import Path
from datetime import datetime

HOME = Path.home()
GAMES_DIR = HOME / "SWARM_GAMES"
GAMES_DIR.mkdir(exist_ok=True)

GAME_TEMPLATES = {
    "roguelike": {
        "name": "DungeonForge",
        "icon": "⚔️",
        "description": "Procedural dungeon crawler - every run different",
        "mechanics": ["procedural_levels", "permadeath", "loot", "enemy_ai", "fog_of_war"]
    },
    "puzzle_platformer": {
        "name": "ShiftWorld", 
        "icon": "🧩",
        "description": "Physics puzzle platformer - think your way through",
        "mechanics": ["physics", "procedural_puzzles", "gravity_shift", "checkpoints"]
    },
    "tower_defense": {
        "name": "WaveCore",
        "icon": "🏰",
        "description": "Strategic tower defense - evolving enemy waves",
        "mechanics": ["wave_spawner", "tower_placement", "upgrades", "evolving_enemies"]
    },
    "word_logic": {
        "name": "LexForge",
        "icon": "📝", 
        "description": "Word and logic puzzles - pure brain challenge",
        "mechanics": ["word_generation", "logic_puzzles", "hint_system", "daily_challenge"]
    },
    "space_shooter": {
        "name": "VoidRunner",
        "icon": "🚀",
        "description": "Arcade space shooter - skill based, no BS",
        "mechanics": ["procedural_enemies", "powerups", "boss_fights", "local_highscore"]
    }
}

def generate_roguelike(seed=None):
    """Generate a complete playable roguelike dungeon crawler"""
    if not seed:
        seed = random.randint(1000, 9999)
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>DungeonForge - Seed {seed}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0a0a0a; color:#fff; font-family:"Courier New", monospace; display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:100vh; }}
canvas {{ border:2px solid #333; image-rendering:pixelated; }}
#ui {{ display:flex; gap:20px; padding:10px; background:#111; width:100%; max-width:640px; justify-content:space-between; align-items:center; }}
#ui span {{ font-size:14px; }}
.hp {{ color:#e74c3c; }}
.gold {{ color:#f1c40f; }}
.floor {{ color:#3498db; }}
.xp {{ color:#2ecc71; }}
#msg {{ height:20px; font-size:12px; color:#888; padding:4px; }}
#gameover {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); justify-content:center; align-items:center; flex-direction:column; gap:20px; }}
#gameover h2 {{ font-size:48px; color:#e74c3c; }}
#gameover p {{ color:#888; }}
button {{ background:#333; color:#fff; border:1px solid #555; padding:10px 20px; cursor:pointer; font-family:inherit; font-size:14px; }}
button:hover {{ background:#444; }}
</style>
</head>
<body>
<div id="ui">
    <span class="hp">❤️ <span id="hp-val">20</span>/<span id="maxhp-val">20</span></span>
    <span class="xp">⭐ LV<span id="lv">1</span> XP:<span id="xp">0</span></span>
    <span class="floor">🏰 Floor <span id="floor">1</span></span>
    <span class="gold">💰 <span id="gold">0</span></span>
</div>
<canvas id="c" width="640" height="480"></canvas>
<div id="msg">Find the stairs ▼ to go deeper. Kill enemies. Grab loot.</div>
<div id="dpad" style="display:grid;grid-template-columns:50px 50px 50px;grid-template-rows:50px 50px;gap:4px;padding:8px;background:#111;width:100%;max-width:640px;justify-content:center;justify-items:center;">
    <div></div>
    <button onclick="tryMove(0,-1)" style="width:50px;height:50px;background:#222;color:#fff;border:1px solid #444;font-size:20px;cursor:pointer;border-radius:8px;">▲</button>
    <div></div>
    <button onclick="tryMove(-1,0)" style="width:50px;height:50px;background:#222;color:#fff;border:1px solid #444;font-size:20px;cursor:pointer;border-radius:8px;">◀</button>
    <button onclick="tryMove(0,1)" style="width:50px;height:50px;background:#222;color:#fff;border:1px solid #444;font-size:20px;cursor:pointer;border-radius:8px;">▼</button>
    <button onclick="tryMove(1,0)" style="width:50px;height:50px;background:#222;color:#fff;border:1px solid #444;font-size:20px;cursor:pointer;border-radius:8px;">▶</button>
</div>
<div id="gameover">
    <h2>YOU DIED</h2>
    <p id="death-msg"></p>
    <button onclick="newGame()">Play Again</button>
</div>

<script>
const C = document.getElementById("c");
const ctx = C.getContext("2d");
const TILE = 32;
const COLS = 20, ROWS = 15;

// Game state
let state = {{}};

function newGame() {{
    document.getElementById("gameover").style.display = "none";
    state = {{
        seed: Math.floor(Math.random() * 99999),
        floor: 1,
        player: {{ x:1, y:1, hp:20, maxHp:20, atk:3, def:1, xp:0, xpNext:10, lv:1, gold:0 }},
        map: [],
        enemies: [],
        items: [],
        stairs: {{x:0, y:0}},
        turn: 0,
        msg: "You enter the dungeon..."
    }};
    generateFloor();
    render();
}}

function rng(seed, n) {{
    // Simple seeded random
    let x = Math.sin(seed + n) * 10000;
    return x - Math.floor(x);
}}

function generateFloor() {{
    const s = state;
    s.map = [];
    s.enemies = [];
    s.items = [];
    
    // Fill with walls
    for(let y=0; y<ROWS; y++) {{
        s.map[y] = [];
        for(let x=0; x<COLS; x++) s.map[y][x] = 1;
    }}
    
    // Generate rooms
    const rooms = [];
    const numRooms = 5 + s.floor;
    
    for(let i=0; i<numRooms*10 && rooms.length<numRooms; i++) {{
        const rw = 4 + Math.floor(rng(s.seed, i*3)*4);
        const rh = 3 + Math.floor(rng(s.seed, i*3+1)*3);
        const rx = 1 + Math.floor(rng(s.seed, i*3+2)*(COLS-rw-2));
        const ry = 1 + Math.floor(rng(s.seed, i*3+3)*(ROWS-rh-2));
        
        let overlap = false;
        for(const r of rooms) {{
            if(rx < r.x+r.w+2 && rx+rw > r.x-2 && ry < r.y+r.h+2 && ry+rh > r.y-2) {{
                overlap = true; break;
            }}
        }}
        if(!overlap) rooms.push({{x:rx, y:ry, w:rw, h:rh}});
    }}
    
    // Carve rooms
    for(const r of rooms) {{
        for(let y=r.y; y<r.y+r.h; y++)
            for(let x=r.x; x<r.x+r.w; x++)
                s.map[y][x] = 0;
    }}
    
    // Connect rooms with corridors
    for(let i=1; i<rooms.length; i++) {{
        const a = rooms[i-1], b = rooms[i];
        const ax = Math.floor(a.x+a.w/2), ay = Math.floor(a.y+a.h/2);
        const bx = Math.floor(b.x+b.w/2), by = Math.floor(b.y+b.h/2);
        let cx=ax, cy=ay;
        while(cx!=bx) {{ s.map[cy][cx]=0; cx+=cx<bx?1:-1; }}
        while(cy!=by) {{ s.map[cy][cx]=0; cy+=cy<by?1:-1; }}
    }}
    
    // Place player in first room
    s.player.x = Math.floor(rooms[0].x + rooms[0].w/2);
    s.player.y = Math.floor(rooms[0].y + rooms[0].h/2);
    
    // Place stairs in last room
    s.stairs.x = Math.floor(rooms[rooms.length-1].x + rooms[rooms.length-1].w/2);
    s.stairs.y = Math.floor(rooms[rooms.length-1].y + rooms[rooms.length-1].h/2);
    
    // Spawn enemies
    const enemyTypes = [
        {{name:"Rat", hp:3, atk:1, def:0, xp:2, gold:1, char:"r", color:"#8B4513"}},
        {{name:"Goblin", hp:6, atk:2, def:1, xp:5, gold:3, char:"g", color:"#2ecc71"}},
        {{name:"Orc", hp:12, atk:4, def:2, xp:10, gold:6, char:"O", color:"#e67e22"}},
        {{name:"Troll", hp:20, atk:6, def:3, xp:20, gold:12, char:"T", color:"#9b59b6"}},
        {{name:"BOSS", hp:40+s.floor*10, atk:8+s.floor, def:4, xp:50, gold:30, char:"D", color:"#e74c3c"}}
    ];
    
    const numEnemies = 3 + s.floor * 2;
    for(let i=0; i<numEnemies; i++) {{
        const room = rooms[1 + Math.floor(rng(s.seed+i, s.floor)*(rooms.length-1))];
        const type = enemyTypes[Math.min(Math.floor(rng(s.seed, i+100)*((s.floor/2)+2)), enemyTypes.length-1)];
        s.enemies.push({{
            ...type,
            maxHp: type.hp,
            x: room.x + 1 + Math.floor(rng(s.seed+i, 200)*(room.w-2)),
            y: room.y + 1 + Math.floor(rng(s.seed+i, 201)*(room.h-2)),
            id: i
        }});
    }}
    
    // Place boss on last floor every 5 floors
    if(s.floor % 5 === 0) {{
        const boss = {{...enemyTypes[4]}};
        boss.x = s.stairs.x - 1;
        boss.y = s.stairs.y;
        boss.id = 999;
        s.enemies.push(boss);
    }}
    
    // Spawn items
    const itemTypes = [
        {{name:"Health Potion", char:"!", color:"#e74c3c", effect:"heal", value:10}},
        {{name:"Sword+1", char:"/", color:"#bdc3c7", effect:"atk", value:1}},
        {{name:"Shield+1", char:"[", color:"#7f8c8d", effect:"def", value:1}},
        {{name:"Gold Pile", char:"$", color:"#f1c40f", effect:"gold", value:5+s.floor*2}}
    ];
    
    for(let i=0; i<rooms.length; i++) {{
        if(rng(s.seed+i, 300) > 0.4) {{
            const room = rooms[i];
            const type = itemTypes[Math.floor(rng(s.seed+i, 301)*itemTypes.length)];
            s.items.push({{
                ...type,
                x: room.x + Math.floor(rng(s.seed+i, 302)*room.w),
                y: room.y + Math.floor(rng(s.seed+i, 303)*room.h),
                id: i
            }});
        }}
    }}
}}

function updateUI() {{
    const p = state.player;
    document.getElementById("hp-val").textContent = p.hp;
    document.getElementById("maxhp-val").textContent = p.maxHp;
    document.getElementById("lv").textContent = p.lv;
    document.getElementById("xp").textContent = p.xp;
    document.getElementById("floor").textContent = state.floor;
    document.getElementById("gold").textContent = p.gold;
    document.getElementById("msg").textContent = state.msg;
}}

function tryMove(dx, dy) {{
    const s = state;
    const nx = s.player.x + dx;
    const ny = s.player.y + dy;
    
    if(nx<0||ny<0||nx>=COLS||ny>=ROWS||s.map[ny][nx]===1) return;
    
    // Check enemy collision - attack
    const enemy = s.enemies.find(e => e.x===nx && e.y===ny);
    if(enemy) {{
        const dmg = Math.max(1, s.player.atk - enemy.def + Math.floor(Math.random()*3));
        enemy.hp -= dmg;
        s.msg = `You hit ${{enemy.name}} for ${{dmg}} damage!`;
        if(enemy.hp <= 0) {{
            s.msg = `You killed ${{enemy.name}}! +${{enemy.xp}}xp +${{enemy.gold}}g`;
            s.player.xp += enemy.xp;
            s.player.gold += enemy.gold;
            s.enemies = s.enemies.filter(e => e.id !== enemy.id);
            // Level up
            if(s.player.xp >= s.player.xpNext) {{
                s.player.lv++;
                s.player.xpNext = Math.floor(s.player.xpNext * 1.5);
                s.player.maxHp += 5;
                s.player.hp = s.player.maxHp;
                s.player.atk++;
                s.msg = `LEVEL UP! You are now level ${{s.player.lv}}!`;
            }}
        }}
        enemyTurn();
        render(); updateUI(); return;
    }}
    
    // Move player
    s.player.x = nx;
    s.player.y = ny;
    
    // Pick up items
    const item = s.items.find(i => i.x===nx && i.y===ny);
    if(item) {{
        if(item.effect === "heal") {{ s.player.hp = Math.min(s.player.maxHp, s.player.hp + item.value); s.msg = `You drink a potion. +${{item.value}} HP`; }}
        else if(item.effect === "atk") {{ s.player.atk += item.value; s.msg = `You equip ${{item.name}}. ATK+${{item.value}}`; }}
        else if(item.effect === "def") {{ s.player.def += item.value; s.msg = `You equip ${{item.name}}. DEF+${{item.value}}`; }}
        else if(item.effect === "gold") {{ s.player.gold += item.value; s.msg = `You find ${{item.value}} gold!`; }}
        s.items = s.items.filter(i => i.id !== item.id);
    }}
    
    // Check stairs
    if(nx === s.stairs.x && ny === s.stairs.y) {{
        s.floor++;
        s.msg = `You descend to floor ${{s.floor}}...`;
        generateFloor();
    }}
    
    enemyTurn();
    render(); updateUI();
}}

function enemyTurn() {{
    const s = state;
    for(const e of s.enemies) {{
        // Simple chase AI
        const dx = s.player.x - e.x;
        const dy = s.player.y - e.y;
        const dist = Math.abs(dx) + Math.abs(dy);
        
        if(dist <= 1 && dist > 0) {{
            // Attack player
            const dmg = Math.max(0, e.atk - s.player.def + Math.floor(Math.random()*2) - 1);
            s.player.hp -= dmg;
            if(dmg > 0) s.msg = `${{e.name}} hits you for ${{dmg}}!`;
            if(s.player.hp <= 0) {{
                document.getElementById("death-msg").textContent = 
                    `Killed by ${{e.name}} on floor ${{s.floor}} with ${{s.player.gold}} gold`;
                document.getElementById("gameover").style.display = "flex";
                return;
            }}
        }} else if(dist < 8) {{
            // Move toward player
            const mx = Math.abs(dx) > Math.abs(dy) ? Math.sign(dx) : 0;
            const my = Math.abs(dx) > Math.abs(dy) ? 0 : Math.sign(dy);
            const nx = e.x + mx, ny = e.y + my;
            if(nx>=0&&ny>=0&&nx<COLS&&ny<ROWS&&s.map[ny][nx]===0) {{
                const blocked = s.enemies.some(o => o.id!==e.id && o.x===nx && o.y===ny);
                if(!blocked && !(nx===s.player.x && ny===s.player.y)) {{ e.x=nx; e.y=ny; }}
            }}
        }}
    }}
}}

const COLORS = {{
    0: "#1a1a2e",  // floor
    1: "#0d0d1a",  // wall
}};

function render() {{
    const s = state;
    ctx.fillStyle = "#000";
    ctx.fillRect(0,0,640,480);
    
    // Calculate camera offset to center on player
    const camX = Math.max(0, Math.min(s.player.x - 10, COLS - 20)) * TILE;
    const camY = Math.max(0, Math.min(s.player.y - 7, ROWS - 15)) * TILE;
    
    // Draw map
    for(let y=0; y<ROWS; y++) {{
        for(let x=0; x<COLS; x++) {{
            const px = x*TILE - camX;
            const py = y*TILE - camY;
            if(px < -TILE || py < -TILE || px > 640 || py > 480) continue;
            
            if(s.map[y][x] === 1) {{
                ctx.fillStyle = "#16213e";
                ctx.fillRect(px, py, TILE, TILE);
                ctx.fillStyle = "#0d0d1a";
                ctx.fillRect(px+2, py+2, TILE-4, TILE-4);
            }} else {{
                ctx.fillStyle = "#1a1a2e";
                ctx.fillRect(px, py, TILE, TILE);
                ctx.fillStyle = "#1e1e3e";
                ctx.fillRect(px+1, py+1, TILE-2, TILE-2);
            }}
        }}
    }}
    
    // Draw stairs
    const sx = s.stairs.x*TILE - camX;
    const sy = s.stairs.y*TILE - camY;
    ctx.fillStyle = "#f1c40f";
    ctx.font = "20px serif";
    ctx.fillText("▼", sx+8, sy+22);
    
    // Draw items
    for(const item of s.items) {{
        const ix = item.x*TILE - camX;
        const iy = item.y*TILE - camY;
        ctx.fillStyle = item.color;
        ctx.font = "bold 18px Courier New";
        ctx.fillText(item.char, ix+8, iy+22);
    }}
    
    // Draw enemies
    for(const e of s.enemies) {{
        const ex = e.x*TILE - camX;
        const ey = e.y*TILE - camY;
        ctx.fillStyle = e.color;
        ctx.font = "bold 20px Courier New";
        ctx.fillText(e.char, ex+7, ey+23);
        // HP bar
        ctx.fillStyle = "#333";
        ctx.fillRect(ex, ey+26, TILE, 4);
        ctx.fillStyle = "#e74c3c";
        ctx.fillRect(ex, ey+26, TILE*(e.hp/e.maxHp), 4);
    }}
    
    // Draw player
    const px = s.player.x*TILE - camX;
    const py = s.player.y*TILE - camY;
    ctx.fillStyle = "#3498db";
    ctx.font = "bold 22px Courier New";
    ctx.fillText("@", px+6, py+24);
}}

// Controls
document.addEventListener("keydown", e => {{
    const keys = {{
        ArrowUp:"up", ArrowDown:"down", ArrowLeft:"left", ArrowRight:"right",
        w:"up", s:"down", a:"left", d:"right",
        k:"up", j:"down", h:"left", l:"right"
    }};
    const dir = keys[e.key];
    if(dir) {{
        e.preventDefault();
        if(dir==="up") tryMove(0,-1);
        else if(dir==="down") tryMove(0,1);
        else if(dir==="left") tryMove(-1,0);
        else if(dir==="right") tryMove(1,0);
    }}
}});

// Touch controls
let touchStart = null;
C.addEventListener("touchstart", e => {{ touchStart = e.touches[0]; e.preventDefault(); }}, {{passive:false}});
C.addEventListener("touchend", e => {{
    if(!touchStart) return;
    const dx = e.changedTouches[0].clientX - touchStart.clientX;
    const dy = e.changedTouches[0].clientY - touchStart.clientY;
    if(Math.abs(dx) > Math.abs(dy)) tryMove(dx>0?1:-1, 0);
    else tryMove(0, dy>0?1:-1);
    touchStart = null;
    e.preventDefault();
}}, {{passive:false}});

newGame();
</script>
</body>
</html>'''

def generate_space_shooter(seed=None):
    if not seed:
        seed = random.randint(1000, 9999)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>VoidRunner</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#000; display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:100vh; }}
canvas {{ border:1px solid #111; }}
#ui {{ display:flex; gap:20px; padding:8px; background:#050505; width:480px; justify-content:space-between; font-family:monospace; font-size:14px; color:#fff; }}
.lives {{ color:#e74c3c; }}
.score {{ color:#f1c40f; }}
.level {{ color:#3498db; }}
#overlay {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); justify-content:center; align-items:center; flex-direction:column; gap:15px; font-family:monospace; color:#fff; }}
#overlay h1 {{ font-size:36px; color:#f1c40f; }}
#overlay p {{ color:#888; font-size:14px; }}
button {{ background:#111; color:#fff; border:1px solid #333; padding:10px 25px; cursor:pointer; font-family:monospace; font-size:14px; margin:5px; }}
button:hover {{ background:#222; border-color:#666; }}
</style>
</head>
<body>
<div id="ui">
    <span class="lives">❤️ <span id="lives">3</span></span>
    <span class="score">⭐ <span id="score">0</span></span>
    <span class="level">WAVE <span id="wave">1</span></span>
    <span style="color:#2ecc71">BOMB: <span id="bombs">2</span></span>
</div>
<canvas id="c" width="480" height="600"></canvas>
<div id="overlay">
    <h1 id="overlay-title">VOIDRUNNER</h1>
    <p id="overlay-msg">Arrow keys / WASD to move. SPACE to shoot. X for bomb.</p>
    <p id="overlay-score"></p>
    <button onclick="startGame()">▶ START</button>
</div>

<script>
const C = document.getElementById("c");
const ctx = C.getContext("2d");
document.getElementById("overlay").style.display = "flex";

let game = {{}};

function startGame() {{
    document.getElementById("overlay").style.display = "none";
    game = {{
        running: true,
        score: 0,
        wave: 1,
        lives: 3,
        bombs: 2,
        player: {{ x:240, y:540, w:30, h:30, speed:5, invincible:0, shooting:0 }},
        bullets: [],
        enemies: [],
        enemyBullets: [],
        particles: [],
        stars: Array.from({{length:100}}, () => ({{
            x: Math.random()*480, y: Math.random()*600,
            speed: 0.5 + Math.random()*2, size: Math.random()*2
        }})),
        keys: {{}},
        spawnTimer: 0,
        waveEnemies: 0,
        waveTarget: 8,
        waveClear: false
    }};
    spawnWave();
    requestAnimationFrame(loop);
}}

function spawnWave() {{
    const g = game;
    const types = [
        {{hp:1, speed:1.5, pts:10, w:24, h:20, color:"#e74c3c", shoot:0.002}},
        {{hp:2, speed:1.2, pts:20, w:28, h:24, color:"#e67e22", shoot:0.004}},
        {{hp:3, speed:0.8, pts:40, w:36, h:30, color:"#9b59b6", shoot:0.006}},
        {{hp:8, speed:0.5, pts:100, w:50, h:40, color:"#e74c3c", shoot:0.01, boss:true}}
    ];
    
    const wave = Math.min(g.wave - 1, types.length - 1);
    const count = g.wave < 5 ? 6 + g.wave * 2 : (g.wave % 5 === 0 ? 1 : 8 + g.wave);
    g.waveTarget = count;
    g.waveEnemies = 0;
    
    for(let i=0; i<count; i++) {{
        const t = g.wave % 5 === 0 ? types[3] : types[Math.min(Math.floor(i/4), wave)];
        g.enemies.push({{
            ...t, maxHp: t.hp,
            x: 40 + (i % 8) * 52,
            y: -60 - Math.floor(i/8) * 60,
            dx: (Math.random()-0.5) * 0.5,
            id: Date.now() + i
        }});
    }}
}}

function spawnParticles(x, y, color, count=8) {{
    for(let i=0; i<count; i++) {{
        const angle = (Math.PI*2/count)*i + Math.random()*0.5;
        const speed = 1 + Math.random()*3;
        game.particles.push({{
            x, y, color,
            dx: Math.cos(angle)*speed,
            dy: Math.sin(angle)*speed,
            life: 1, decay: 0.05 + Math.random()*0.05
        }});
    }}
}}

function loop() {{
    if(!game.running) return;
    update();
    draw();
    requestAnimationFrame(loop);
}}

function update() {{
    const g = game;
    const p = g.player;
    
    // Move player
    if((g.keys["ArrowLeft"]||g.keys["a"]) && p.x > 15) p.x -= p.speed;
    if((g.keys["ArrowRight"]||g.keys["d"]) && p.x < 465) p.x += p.speed;
    if((g.keys["ArrowUp"]||g.keys["w"]) && p.y > 100) p.y -= p.speed;
    if((g.keys["ArrowDown"]||g.keys["s"]) && p.y < 585) p.y += p.speed;
    
    // Auto shoot
    p.shooting++;
    if(p.shooting > 8 && (g.keys[" "]||g.keys["z"])) {{
        p.shooting = 0;
        g.bullets.push({{x:p.x, y:p.y-15, speed:10, w:4, h:12}});
    }}
    
    // Bomb
    if(g.keys["x"] && g.bombs > 0) {{
        g.keys["x"] = false;
        g.bombs--;
        document.getElementById("bombs").textContent = g.bombs;
        for(const e of g.enemies) spawnParticles(e.x, e.y, e.color, 12);
        g.enemies = [];
        g.score += 500;
    }}
    
    if(p.invincible > 0) p.invincible--;
    
    // Update stars
    for(const s of g.stars) {{
        s.y += s.speed;
        if(s.y > 600) {{ s.y = 0; s.x = Math.random()*480; }}
    }}
    
    // Update bullets
    g.bullets = g.bullets.filter(b => {{ b.y -= b.speed; return b.y > -20; }});
    
    // Update enemies
    for(const e of g.enemies) {{
        e.y += e.speed;
        e.x += e.dx;
        if(e.x < 20 || e.x > 460) e.dx *= -1;
        if(e.boss) e.x += Math.sin(Date.now()*0.002)*2;
        
        // Enemy shoots
        if(Math.random() < e.shoot) {{
            g.enemyBullets.push({{x:e.x, y:e.y+e.h/2, dy:3+g.wave*0.3, w:6, h:10, color:e.color}});
        }}
        
        // Enemy reaches bottom
        if(e.y > 620) {{
            g.lives--;
            document.getElementById("lives").textContent = g.lives;
            spawnParticles(p.x, p.y, "#3498db", 16);
            g.enemies = g.enemies.filter(x => x.id !== e.id);
            if(g.lives <= 0) gameOver();
        }}
    }}
    
    // Update enemy bullets
    g.enemyBullets = g.enemyBullets.filter(b => {{ b.y += b.dy; return b.y < 620; }});
    
    // Bullet-enemy collision
    for(const b of [...g.bullets]) {{
        for(const e of [...g.enemies]) {{
            if(Math.abs(b.x-e.x)<e.w/2+2 && Math.abs(b.y-e.y)<e.h/2+6) {{
                e.hp--;
                g.bullets = g.bullets.filter(x => x !== b);
                spawnParticles(e.x, e.y, e.color, 4);
                if(e.hp <= 0) {{
                    g.score += e.pts * g.wave;
                    document.getElementById("score").textContent = g.score;
                    spawnParticles(e.x, e.y, e.color, 12);
                    g.enemies = g.enemies.filter(x => x.id !== e.id);
                    g.waveEnemies++;
                }}
                break;
            }}
        }}
    }}
    
    // Enemy bullet hits player
    if(p.invincible === 0) {{
        for(const b of g.enemyBullets) {{
            if(Math.abs(b.x-p.x)<16 && Math.abs(b.y-p.y)<16) {{
                g.enemyBullets = g.enemyBullets.filter(x => x !== b);
                g.lives--;
                p.invincible = 120;
                document.getElementById("lives").textContent = g.lives;
                spawnParticles(p.x, p.y, "#3498db", 16);
                if(g.lives <= 0) gameOver();
                break;
            }}
        }}
    }}
    
    // Update particles
    g.particles = g.particles.filter(p => {{
        p.x += p.dx; p.y += p.dy;
        p.dx *= 0.95; p.dy *= 0.95;
        p.life -= p.decay;
        return p.life > 0;
    }});
    
    // Wave clear
    if(g.enemies.length === 0 && !g.waveClear) {{
        g.waveClear = true;
        g.score += g.wave * 100;
        setTimeout(() => {{
            g.wave++;
            g.bombs = Math.min(g.bombs+1, 5);
            document.getElementById("wave").textContent = g.wave;
            document.getElementById("bombs").textContent = g.bombs;
            document.getElementById("score").textContent = g.score;
            g.waveClear = false;
            spawnWave();
        }}, 1500);
    }}
}}

function drawShip(x, y, invincible) {{
    const t = Date.now();
    if(invincible > 0 && Math.floor(invincible/8)%2) return;
    
    ctx.save();
    ctx.translate(x, y);
    // Engine glow
    ctx.shadowBlur = 15;
    ctx.shadowColor = "#3498db";
    // Body
    ctx.fillStyle = "#3498db";
    ctx.beginPath();
    ctx.moveTo(0, -15);
    ctx.lineTo(-12, 10);
    ctx.lineTo(-5, 5);
    ctx.lineTo(0, 8);
    ctx.lineTo(5, 5);
    ctx.lineTo(12, 10);
    ctx.closePath();
    ctx.fill();
    // Engine
    ctx.fillStyle = `hsl(${{t%360}}, 100%, 60%)`;
    ctx.beginPath();
    ctx.moveTo(-5, 10);
    ctx.lineTo(5, 10);
    ctx.lineTo(3, 18);
    ctx.lineTo(-3, 18);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
}}

function drawEnemy(e) {{
    ctx.save();
    ctx.translate(e.x, e.y);
    ctx.shadowBlur = 10;
    ctx.shadowColor = e.color;
    ctx.fillStyle = e.color;
    if(e.boss) {{
        // Diamond boss
        ctx.beginPath();
        ctx.moveTo(0, -e.h/2);
        ctx.lineTo(e.w/2, 0);
        ctx.lineTo(0, e.h/2);
        ctx.lineTo(-e.w/2, 0);
        ctx.closePath();
        ctx.fill();
        // HP bar
        ctx.fillStyle = "#333";
        ctx.fillRect(-e.w/2, -e.h/2-8, e.w, 5);
        ctx.fillStyle = "#e74c3c";
        ctx.fillRect(-e.w/2, -e.h/2-8, e.w*(e.hp/e.maxHp), 5);
    }} else {{
        ctx.beginPath();
        ctx.moveTo(0, e.h/2);
        ctx.lineTo(-e.w/2, -e.h/2);
        ctx.lineTo(0, -e.h/4);
        ctx.lineTo(e.w/2, -e.h/2);
        ctx.closePath();
        ctx.fill();
    }}
    ctx.restore();
}}

function draw() {{
    const g = game;
    ctx.fillStyle = "#000005";
    ctx.fillRect(0,0,480,600);
    
    // Stars
    for(const s of g.stars) {{
        ctx.fillStyle = `rgba(255,255,255,${{s.size/2}})`;
        ctx.fillRect(s.x, s.y, s.size, s.size);
    }}
    
    // Particles
    for(const p of g.particles) {{
        ctx.globalAlpha = p.life;
        ctx.fillStyle = p.color;
        ctx.fillRect(p.x-2, p.y-2, 4, 4);
    }}
    ctx.globalAlpha = 1;
    
    // Bullets
    ctx.shadowBlur = 8;
    ctx.shadowColor = "#2ecc71";
    ctx.fillStyle = "#2ecc71";
    for(const b of g.bullets) ctx.fillRect(b.x-2, b.y, b.w, b.h);
    
    // Enemy bullets
    for(const b of g.enemyBullets) {{
        ctx.shadowColor = b.color;
        ctx.fillStyle = b.color;
        ctx.beginPath();
        ctx.ellipse(b.x, b.y, b.w/2, b.h/2, 0, 0, Math.PI*2);
        ctx.fill();
    }}
    ctx.shadowBlur = 0;
    
    // Enemies
    for(const e of g.enemies) drawEnemy(e);
    
    // Player
    drawShip(g.player.x, g.player.y, g.player.invincible);
    
    // Wave clear message
    if(g.waveClear) {{
        ctx.fillStyle = "#f1c40f";
        ctx.font = "bold 32px monospace";
        ctx.textAlign = "center";
        ctx.fillText(`WAVE ${{g.wave}} CLEAR!`, 240, 300);
        ctx.fillText(`+${{g.wave*100}} BONUS`, 240, 340);
        ctx.textAlign = "left";
    }}
}}

function gameOver() {{
    game.running = false;
    document.getElementById("overlay-title").textContent = "GAME OVER";
    document.getElementById("overlay-msg").textContent = `Reached Wave ${{game.wave}}`;
    document.getElementById("overlay-score").textContent = `Final Score: ${{game.score}}`;
    document.getElementById("overlay").style.display = "flex";
}}

document.addEventListener("keydown", e => {{ 
    game.keys[e.key] = true; 
    if([" ","ArrowUp","ArrowDown"].includes(e.key)) e.preventDefault();
}});
document.addEventListener("keyup", e => {{ game.keys[e.key] = false; }});

// Touch controls
let touchX = null;
C.addEventListener("touchstart", e => {{ 
    touchX = e.touches[0].clientX;
    game.keys[" "] = true;
    e.preventDefault(); 
}}, {{passive:false}});
C.addEventListener("touchmove", e => {{
    const dx = e.touches[0].clientX - touchX;
    if(game.player) game.player.x = Math.max(15, Math.min(465, game.player.x + dx*0.5));
    touchX = e.touches[0].clientX;
    e.preventDefault();
}}, {{passive:false}});
C.addEventListener("touchend", e => {{ game.keys[" "] = false; }});
</script>
</body>
</html>'''

def generate_game(game_type, output_dir=None):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not output_dir:
        output_dir = GAMES_DIR / f"{game_type}_{ts}"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if game_type == "roguelike":
        html = generate_roguelike()
        name = "DungeonForge"
    elif game_type == "space_shooter":
        html = generate_space_shooter()
        name = "VoidRunner"
    else:
        html = generate_roguelike()
        name = "DungeonForge"
    
    game_file = output_dir / "index.html"
    game_file.write_text(html)
    
    # Write game metadata
    meta = {
        "name": name,
        "type": game_type,
        "generated_at": datetime.now().isoformat(),
        "no_paywalls": True,
        "no_loot_boxes": True,
        "offline": True,
        "file": str(game_file)
    }
    (output_dir / "game.json").write_text(json.dumps(meta, indent=2))
    
    print(f"  🎮 Generated: {name}")
    print(f"  📁 Location: {output_dir}")
    print(f"  🌐 Open: {game_file}")
    return output_dir

if __name__ == "__main__":
    print("="*50)
    print("SWARM GAME GENERATOR")
    print("Real games. No BS.")
    print("="*50)
    
    for game_type in ["roguelike", "space_shooter"]:
        print(f"\nGenerating {game_type}...")
        generate_game(game_type)
    
    print(f"\n✅ Games saved to {GAMES_DIR}")
    print("Open the index.html files in any browser to play")
