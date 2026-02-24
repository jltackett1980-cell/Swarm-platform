#!/usr/bin/env python3
"""
TURBO EVOLUTION - 100 generations, no rest, full speed
Runs alongside the normal organism, targeting uncovered domains
"""
import os, json, re, shutil, random
from pathlib import Path
from datetime import datetime

HOME = Path.home()
CONFIGS_FILE = HOME / "organism_templates" / "domain_configs.json"
CHAMPIONS_DIR = HOME / "ORGANISM_ARMY" / "champions"
APPS_DIR = HOME
LOG_FILE = HOME / "turbo_evolve.log"
TARGET_GENERATIONS = 200

def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_configs():
    return json.loads(CONFIGS_FILE.read_text())

def get_champion(domain_id):
    cf = CHAMPIONS_DIR / domain_id / "champion.json"
    if cf.exists():
        return json.loads(cf.read_text())
    return None

def get_best_app(domain_id):
    """Find the highest scoring app for a domain"""
    champ = get_champion(domain_id)
    if champ and champ.get("source_app"):
        app_path = HOME / champ["source_app"]
        if app_path.exists():
            return app_path, champ.get("score", 0)
    return None, 0

def generate_evolved_app(domain_id, cfg, generation, parent_path=None):
    """Generate an evolved app based on parent champion"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    app_name = f"turbo_{domain_id}_{ts}"
    app_path = HOME / app_name
    
    backend_dir = app_path / "backend"
    frontend_dir = app_path / "frontend"
    if app_path.exists():
        shutil.rmtree(app_path)
    backend_dir.mkdir(parents=True)
    frontend_dir.mkdir(parents=True)

    name = cfg.get("name", domain_id)
    entity = cfg.get("entity", "Item")
    entities = cfg.get("entities", "Items")
    fields = cfg.get("fields", [])
    table_cols = cfg.get("table_cols", [])
    icon = cfg.get("icon", "📊")

    # Pre-compute values needed inside f-strings
    search_fields = fields[:3]
    search_where = " OR ".join([f"{f[0]} LIKE ?" for f in search_fields])
    search_params_count = len(search_fields)
    js_field_assignments = "\n    ".join([f'data["{f[0]}"] = document.getElementById("field_{f[0]}").value;' for f in fields])

    # Build evolved backend with all scoring criteria
    field_defs = "\n            ".join([
        f"{f[0]} {('TEXT' if f[2] in ['text','email','tel','date','time'] else 'INTEGER' if f[2]=='number' else 'TEXT')},"
        for f in fields
    ])
    
    field_names = [f[0] for f in fields]
    field_placeholders = ", ".join(["?" for _ in fields])
    field_assignments = ", ".join([f"{f[0]}=?" for f in fields])
    insert_fields = ", ".join(field_names)
    
    backend = f'''#!/usr/bin/env python3
"""
{name} - Generation {generation}
Turbo Evolved | Domain: {domain_id}
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, jwt, os, re

app = Flask(__name__)
CORS(app)
SECRET_KEY = 'swarm-{domain_id}-secret-gen{generation}'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '{domain_id}.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute(\'\'\'CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT "user",
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )\'\'\')
        db.execute(\'\'\'CREATE TABLE IF NOT EXISTS {entities.lower()} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {field_defs}
            status TEXT DEFAULT "active",
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id) REFERENCES users(id)
        )\'\'\')
        db.execute(\'\'\'CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            entity_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )\'\'\')
        db.commit()

def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({{"error": "No token"}}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = data
        except:
            return jsonify({{"error": "Invalid token"}}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/", methods=["GET"])
def index():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend/index.html")
    return send_file(p)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({{"status": "healthy", "app": "{name}", "generation": {generation}, "timestamp": datetime.now().isoformat()}})

@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not data.get("username") or not data.get("password"):
            return jsonify({{"error": "Username and password required"}}), 400
        hashed = generate_password_hash(data["password"])
        with get_db() as db:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (data["username"], hashed))
            db.commit()
        return jsonify({{"message": "User created successfully"}})
    except Exception as e:
        return jsonify({{"error": str(e)}}), 400

@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username=?", (data["username"],)).fetchone()
        if user and check_password_hash(user["password"], data["password"]):
            token = jwt.encode({{"user": data["username"], "role": user["role"]}}, SECRET_KEY, algorithm="HS256")
            return jsonify({{"token": token, "username": data["username"]}})
        return jsonify({{"error": "Invalid credentials"}}), 401
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500

@app.route("/api/{entities.lower()}", methods=["GET"])
@token_required
def get_{entities.lower()}():
    try:
        search = request.args.get("search", "")
        with get_db() as db:
            if search:
                rows = db.execute(
                    "SELECT * FROM {entities.lower()} WHERE " + 
                    search_where +
                    " ORDER BY created_at DESC",
                    [f"%{{search}}%" for _ in range({search_params_count})]
                ).fetchall()
            else:
                rows = db.execute("SELECT * FROM {entities.lower()} ORDER BY created_at DESC").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500

@app.route("/api/{entities.lower()}", methods=["POST"])
@token_required
def create_{entity.lower()}():
    try:
        data = request.get_json()
        if not data:
            return jsonify({{"error": "No data provided"}}), 400
        with get_db() as db:
            db.execute(
                "INSERT INTO {entities.lower()} ({insert_fields}) VALUES ({field_placeholders})",
                [data.get(fn, "") for fn in field_names]
            )
            db.commit()
        return jsonify({{"message": "{entity} created successfully"}})
    except Exception as e:
        return jsonify({{"error": str(e)}}), 400

@app.route("/api/{entities.lower()}/<int:item_id>", methods=["GET"])
@token_required
def get_{entity.lower()}(item_id):
    try:
        with get_db() as db:
            row = db.execute("SELECT * FROM {entities.lower()} WHERE id=?", (item_id,)).fetchone()
        if not row:
            return jsonify({{"error": "{entity} not found"}}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500

@app.route("/api/{entities.lower()}/<int:item_id>", methods=["PUT"])
@token_required
def update_{entity.lower()}(item_id):
    try:
        data = request.get_json()
        with get_db() as db:
            db.execute(
                "UPDATE {entities.lower()} SET {field_assignments}, updated_at=? WHERE id=?",
                [data.get(fn, "") for fn in field_names] + [datetime.now().isoformat(), item_id]
            )
            db.commit()
        return jsonify({{"message": "{entity} updated"}})
    except Exception as e:
        return jsonify({{"error": str(e)}}), 400

@app.route("/api/{entities.lower()}/<int:item_id>", methods=["DELETE"])
@token_required
def delete_{entity.lower()}(item_id):
    try:
        with get_db() as db:
            db.execute("DELETE FROM {entities.lower()} WHERE id=?", (item_id,))
            db.commit()
        return jsonify({{"message": "{entity} deleted"}})
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500

@app.route("/api/{entities.lower()}/search", methods=["GET"])
@token_required  
def search_{entities.lower()}():
    try:
        q = request.args.get("q", "")
        with get_db() as db:
            rows = db.execute(
                "SELECT * FROM {entities.lower()} WHERE status LIKE ? ORDER BY created_at DESC LIMIT 50",
                (f"%{{q}}%",)
            ).fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500

@app.route("/api/stats", methods=["GET"])
@token_required
def stats():
    try:
        with get_db() as db:
            total = db.execute("SELECT COUNT(*) as count FROM {entities.lower()}").fetchone()["count"]
            active = db.execute("SELECT COUNT(*) as count FROM {entities.lower()} WHERE status='active'").fetchone()["count"]
            recent = db.execute("SELECT COUNT(*) as count FROM {entities.lower()} WHERE date(created_at) = date('now')").fetchone()["count"]
        return jsonify({{"total": total, "active": active, "today": recent, "domain": "{domain_id}", "generation": {generation}}})
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
'''

    # Write backend
    (backend_dir / "app.py").write_text(backend)
    (backend_dir / "requirements.txt").write_text("flask\nflask-cors\nPyJWT\nwerkzeug\n")

    # Build evolved frontend
    col_headers = "".join([f'<th>{c[1]}</th>' for c in table_cols])
    col_data = "".join([f'<td>${{item.{c[0]}}}</td>' for c in table_cols])
    field_inputs = "".join([f'''
                <div class="form-group">
                    <label>{f[1]}</label>
                    <input type="{f[2]}" id="field_{f[0]}" placeholder="{f[1]}" />
                </div>''' for f in fields])

    frontend = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>{name}</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:#f0f2f5; }}
        .sidebar {{ width:240px; height:100vh; background:linear-gradient(180deg,#1a1a2e,#16213e); position:fixed; left:0; top:0; padding:20px; }}
        .sidebar h2 {{ color:#fff; font-size:18px; margin-bottom:30px; }}
        .sidebar a {{ display:block; color:#aaa; text-decoration:none; padding:10px; border-radius:8px; margin-bottom:5px; transition:all 0.2s; }}
        .sidebar a:hover, .sidebar a.active {{ background:rgba(255,255,255,0.1); color:#fff; }}
        .main {{ margin-left:240px; padding:30px; }}
        .header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:30px; }}
        .header h1 {{ font-size:24px; color:#1a1a2e; }}
        .stats {{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-bottom:30px; }}
        .stat-card {{ background:#fff; border-radius:12px; padding:20px; box-shadow:0 2px 10px rgba(0,0,0,0.08); }}
        .stat-card h3 {{ color:#666; font-size:12px; text-transform:uppercase; margin-bottom:8px; }}
        .stat-card p {{ font-size:32px; font-weight:700; color:#1a1a2e; }}
        .card {{ background:#fff; border-radius:12px; padding:20px; box-shadow:0 2px 10px rgba(0,0,0,0.08); margin-bottom:20px; }}
        .btn {{ padding:10px 20px; border:none; border-radius:8px; cursor:pointer; font-size:14px; font-weight:600; }}
        .btn-primary {{ background:linear-gradient(135deg,#667eea,#764ba2); color:#fff; }}
        .btn-danger {{ background:#ff4757; color:#fff; }}
        table {{ width:100%; border-collapse:collapse; }}
        th {{ background:#f8f9fa; padding:12px; text-align:left; font-size:12px; text-transform:uppercase; color:#666; }}
        td {{ padding:12px; border-bottom:1px solid #f0f2f5; }}
        tr:hover {{ background:#f8f9fa; }}
        .form-group {{ margin-bottom:15px; }}
        .form-group label {{ display:block; margin-bottom:5px; font-size:13px; font-weight:600; color:#444; }}
        .form-group input {{ width:100%; padding:10px; border:1px solid #ddd; border-radius:8px; font-size:14px; }}
        .search-box {{ padding:10px; border:1px solid #ddd; border-radius:8px; width:300px; margin-bottom:20px; }}
        #login-screen {{ display:flex; justify-content:center; align-items:center; height:100vh; background:linear-gradient(135deg,#667eea,#764ba2); }}
        .login-card {{ background:#fff; padding:40px; border-radius:16px; width:360px; box-shadow:0 20px 60px rgba(0,0,0,0.3); }}
        .login-card h2 {{ text-align:center; margin-bottom:25px; color:#1a1a2e; }}
        .badge {{ padding:3px 8px; border-radius:4px; font-size:11px; background:#e3f2fd; color:#1976d2; }}
        .gen-badge {{ position:fixed; bottom:10px; right:10px; background:#1a1a2e; color:#fff; padding:5px 10px; border-radius:20px; font-size:11px; }}
    </style>
</head>
<body>
<div id="login-screen">
    <div class="login-card">
        <h2>{icon} {name}</h2>
        <div class="form-group">
            <label>Username</label>
            <input type="text" id="login-user" placeholder="Username"/>
        </div>
        <div class="form-group">
            <label>Password</label>
            <input type="password" id="login-pass" placeholder="Password"/>
        </div>
        <button class="btn btn-primary" style="width:100%" onclick="login()">Login</button>
        <p style="text-align:center;margin-top:10px;font-size:12px;color:#999">Generation {generation}</p>
    </div>
</div>

<div id="app" style="display:none">
    <div class="sidebar">
        <h2>{icon} {name}</h2>
        <a href="#" class="active" onclick="showDashboard()">📊 Dashboard</a>
        <a href="#" onclick="showList()">📋 {entities}</a>
        <a href="#" onclick="showAdd()">➕ Add {entity}</a>
        <a href="#" onclick="showStats()">📈 Reports</a>
        <a href="#" onclick="logout()" style="margin-top:auto;color:#ff6b6b">🚪 Logout</a>
    </div>
    <div class="main">
        <div class="header">
            <h1 id="page-title">Dashboard</h1>
            <button class="btn btn-primary" onclick="showAdd()">+ Add {entity}</button>
        </div>
        <div id="content"></div>
    </div>
</div>
<div class="gen-badge">Gen {generation} | {name}</div>

<script>
let token = localStorage.getItem("token") || "";
let currentData = [];
const API = "";

async function api(method, path, body) {{
    const r = await fetch(API+path, {{
        method, headers: {{"Content-Type":"application/json", "Authorization":"Bearer "+token}},
        body: body ? JSON.stringify(body) : undefined
    }});
    return r.json();
}}

async function login() {{
    const u = document.getElementById("login-user").value;
    const p = document.getElementById("login-pass").value;
    const r = await fetch("/api/auth/login", {{
        method:"POST", headers:{{"Content-Type":"application/json"}},
        body: JSON.stringify({{username:u, password:p}})
    }});
    const d = await r.json();
    if(d.token) {{
        token = d.token;
        localStorage.setItem("token", token);
        document.getElementById("login-screen").style.display = "none";
        document.getElementById("app").style.display = "block";
        showDashboard();
    }} else {{
        alert("Login failed: " + (d.error || "Unknown error"));
    }}
}}

function logout() {{
    token = "";
    localStorage.removeItem("token");
    document.getElementById("login-screen").style.display = "flex";
    document.getElementById("app").style.display = "none";
}}

async function showDashboard() {{
    document.getElementById("page-title").textContent = "Dashboard";
    const stats = await api("GET", "/api/stats");
    document.getElementById("content").innerHTML = `
        <div class="stats">
            <div class="stat-card"><h3>Total {entities}</h3><p>${{stats.total || 0}}</p></div>
            <div class="stat-card"><h3>Active</h3><p>${{stats.active || 0}}</p></div>
            <div class="stat-card"><h3>Today</h3><p>${{stats.today || 0}}</p></div>
        </div>
        <div class="card">
            <h3 style="margin-bottom:15px">Recent {entities}</h3>
            <div id="recent-list"></div>
        </div>`;
    const items = await api("GET", "/api/{entities.lower()}");
    currentData = items;
    renderTable(items.slice(0,5), document.getElementById("recent-list"));
}}

async function showList() {{
    document.getElementById("page-title").textContent = "{entities}";
    document.getElementById("content").innerHTML = `
        <div class="card">
            <input class="search-box" placeholder="Search {entities.lower()}..." oninput="searchItems(this.value)"/>
            <div id="list-table"></div>
        </div>`;
    const items = await api("GET", "/api/{entities.lower()}");
    currentData = items;
    renderTable(items, document.getElementById("list-table"));
}}

async function searchItems(q) {{
    const items = await api("GET", "/api/{entities.lower()}?search="+q);
    renderTable(items, document.getElementById("list-table"));
}}

function renderTable(items, el) {{
    if(!items || !items.length) {{ el.innerHTML="<p style='color:#999;padding:20px'>No {entities.lower()} found</p>"; return; }}
    el.innerHTML = `<table><tr>{col_headers}<th>Actions</th></tr>` +
        items.map(item => `<tr>{col_data}
            <td><button class="btn btn-danger" onclick="deleteItem(${{item.id}})" style="padding:5px 10px;font-size:12px">Delete</button></td>
        </tr>`).join("") + "</table>";
}}

function showAdd() {{
    document.getElementById("page-title").textContent = "Add {entity}";
    document.getElementById("content").innerHTML = `
        <div class="card" style="max-width:600px">
            <h3 style="margin-bottom:20px">New {entity}</h3>
            {field_inputs}
            <button class="btn btn-primary" onclick="submitAdd()">Save {entity}</button>
        </div>`;
}}

async function submitAdd() {{
    const data = {{}};
    {js_field_assignments}
    const r = await api("POST", "/api/{entities.lower()}", data);
    if(r.message) {{ alert("{entity} saved!"); showList(); }}
    else alert("Error: " + r.error);
}}

async function deleteItem(id) {{
    if(!confirm("Delete this {entity.lower()}?")) return;
    await api("DELETE", "/api/{entities.lower()}/"+id);
    showList();
}}

async function showStats() {{
    document.getElementById("page-title").textContent = "Reports";
    const stats = await api("GET", "/api/stats");
    document.getElementById("content").innerHTML = `
        <div class="stats">
            <div class="stat-card"><h3>Total {entities}</h3><p>${{stats.total||0}}</p></div>
            <div class="stat-card"><h3>Active</h3><p>${{stats.active||0}}</p></div>
            <div class="stat-card"><h3>Added Today</h3><p>${{stats.today||0}}</p></div>
        </div>
        <div class="card"><h3>Platform Info</h3>
            <p style="margin-top:10px">Domain: {domain_id}</p>
            <p>Generation: {generation}</p>
            <p>App: {name}</p>
        </div>`;
}}

// Auto-login if token exists
if(token) {{
    document.getElementById("login-screen").style.display = "none";
    document.getElementById("app").style.display = "block";
    showDashboard();
}}
</script>
</body>
</html>'''

    (frontend_dir / "index.html").write_text(frontend)
    return app_path

def score_app(path, cfg):
    """Score the generated app"""
    score = 0
    breakdown = {}
    
    backend = path / "backend" / "app.py"
    frontend = path / "frontend" / "index.html"
    
    if backend.exists():
        content = backend.read_text()
        fields = cfg.get("fields", [])
        real_fields = [f[0] for f in fields if f[0] not in {"name","status","id","created_at"}]
        if real_fields:
            found = sum(1 for f in real_fields if f in content)
            breakdown["domain_fields"] = int((found / len(real_fields)) * 60)
        routes = len(re.findall(r"@app\.route\(", content))
        breakdown["routes"] = min(routes * 5, 30)
        auth = 0
        if "jwt" in content.lower(): auth += 10
        if "login" in content and "password" in content: auth += 10
        breakdown["auth"] = auth
        breakdown["relationships"] = 20 if "FOREIGN KEY" in content else (10 if content.count("CREATE TABLE") > 2 else 0)
        breakdown["validation"] = 10 if "get_json()" in content and "400" in content else (5 if "try:" in content else 0)
        breakdown["search"] = 10 if "LIKE" in content or "search" in content.lower() else 0
    
    if frontend.exists():
        content = frontend.read_text()
        if "fetch(" in content: breakdown["api_calls"] = 10
        if "/api/" in content: breakdown["api_calls"] = min(breakdown.get("api_calls", 0) + 10, 20)
        fields = cfg.get("fields", [])
        found = sum(1 for f in fields if f[0] in content)
        breakdown["ui_fields"] = min(found * 3, 15)
        breakdown["forms"] = 10 if "getElementById" in content else 0

    score = sum(breakdown.values())
    breakdown["total"] = score
    return score, breakdown

def save_champion(domain_id, cfg, score, breakdown, app_path, generation):
    champ_dir = CHAMPIONS_DIR / domain_id
    champ_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy app files
    for folder in ["backend", "frontend"]:
        src = app_path / folder
        dst = champ_dir / folder
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    
    # Save champion.json
    champ = {
        "domain": domain_id,
        "name": cfg.get("name", domain_id),
        "icon": cfg.get("icon", "📊"),
        "score": score,
        "breakdown": breakdown,
        "generation": generation,
        "crowned_at": datetime.now().isoformat(),
        "source_app": str(app_path.name)
    }
    (champ_dir / "champion.json").write_text(json.dumps(champ, indent=2))
    return generation

def discover_new_domains(configs):
    """Discover new domains by cross-pollinating existing ones"""
    new_domains = {
        "telehealth": {
            "name": "TeleHealth",
            "icon": "💻",
            "entity": "Consultation",
            "entities": "Consultations",
            "nav": [["dashboard","📊","Dashboard"],["consultations","💻","consultations"],["patients","👤","patients"],["prescriptions","💊","prescriptions"]],
            "fields": [["patient","Patient","text"],["doctor","Doctor","text"],["date","Date","date"],["time","Time","time"],["type","Type","text"],["diagnosis","Diagnosis","text"],["prescription","Prescription","text"]],
            "table_cols": [["patient","Patient"],["doctor","Doctor"],["date","Date"],["type","Type"]],
            "prompt": "telehealth video consultation platform with patient records, doctor scheduling, prescriptions and follow-ups"
        },
        "esports": {
            "name": "EsportsHub",
            "icon": "🏆",
            "entity": "Tournament",
            "entities": "Tournaments",
            "nav": [["dashboard","📊","Dashboard"],["tournaments","🏆","tournaments"],["teams","👥","teams"],["players","🎮","players"]],
            "fields": [["name","Tournament Name","text"],["game","Game","text"],["teams","Team Count","number"],["prize","Prize Pool","number"],["start_date","Start Date","date"],["status","Status","text"],["winner","Winner","text"]],
            "table_cols": [["name","Tournament"],["game","Game"],["prize","Prize Pool"],["status","Status"]],
            "prompt": "esports tournament management with team registration, brackets, prize pools, player stats and live scoring"
        },
        "drone_delivery": {
            "name": "DroneOps",
            "icon": "🚁",
            "entity": "Delivery",
            "entities": "Deliveries",
            "nav": [["dashboard","📊","Dashboard"],["deliveries","🚁","deliveries"],["drones","🤖","drones"],["routes","🗺️","routes"]],
            "fields": [["package_id","Package ID","text"],["drone_id","Drone ID","text"],["origin","Origin","text"],["destination","Destination","text"],["weight","Weight kg","number"],["status","Status","text"],["eta","ETA","time"]],
            "table_cols": [["package_id","Package"],["drone_id","Drone"],["destination","Destination"],["status","Status"]],
            "prompt": "drone delivery fleet management with route optimization, package tracking, drone status monitoring and delivery confirmation"
        },
        "smart_farm": {
            "name": "SmartFarm",
            "icon": "🌱",
            "entity": "Crop",
            "entities": "Crops",
            "nav": [["dashboard","📊","Dashboard"],["crops","🌱","crops"],["livestock","🐄","livestock"],["equipment","🚜","equipment"]],
            "fields": [["crop_name","Crop","text"],["field","Field","text"],["planted","Planted","date"],["harvest_date","Harvest Date","date"],["yield_kg","Yield kg","number"],["soil_ph","Soil pH","number"],["status","Status","text"]],
            "table_cols": [["crop_name","Crop"],["field","Field"],["planted","Planted"],["status","Status"]],
            "prompt": "smart farm management with crop tracking, soil monitoring, livestock management, equipment scheduling and yield analytics"
        },
        "vr_studio": {
            "name": "VRStudio",
            "icon": "🥽",
            "entity": "Experience",
            "entities": "Experiences",
            "nav": [["dashboard","📊","Dashboard"],["experiences","🥽","experiences"],["sessions","🎮","sessions"],["users","👤","users"]],
            "fields": [["title","Experience Title","text"],["type","Type","text"],["duration","Duration min","number"],["max_users","Max Users","number"],["platform","Platform","text"],["rating","Rating","number"],["status","Status","text"]],
            "table_cols": [["title","Experience"],["type","Type"],["duration","Duration"],["platform","Platform"]],
            "prompt": "VR studio management with experience catalog, session booking, user progress tracking, platform management and performance analytics"
        },
        "crypto_exchange": {
            "name": "CryptoDesk",
            "icon": "₿",
            "entity": "Transaction",
            "entities": "Transactions",
            "nav": [["dashboard","📊","Dashboard"],["transactions","₿","transactions"],["wallets","👛","wallets"],["markets","📈","markets"]],
            "fields": [["tx_id","Transaction ID","text"],["from_wallet","From","text"],["to_wallet","To","text"],["amount","Amount","number"],["currency","Currency","text"],["fee","Fee","number"],["status","Status","text"]],
            "table_cols": [["tx_id","TX ID"],["currency","Currency"],["amount","Amount"],["status","Status"]],
            "prompt": "crypto exchange management with wallet tracking, transaction history, market data, fee management and compliance reporting"
        },
        "fleet_management": {
            "name": "FleetCore",
            "icon": "🚛",
            "entity": "Vehicle",
            "entities": "Vehicles",
            "nav": [["dashboard","📊","Dashboard"],["vehicles","🚛","vehicles"],["drivers","👤","drivers"],["maintenance","🔧","maintenance"]],
            "fields": [["plate","Plate Number","text"],["driver","Driver","text"],["type","Vehicle Type","text"],["fuel","Fuel %","number"],["mileage","Mileage","number"],["last_service","Last Service","date"],["status","Status","text"]],
            "table_cols": [["plate","Plate"],["driver","Driver"],["fuel","Fuel"],["status","Status"]],
            "prompt": "fleet management system with vehicle tracking, driver assignment, fuel monitoring, maintenance scheduling and route optimization"
        },
        "music_studio": {
            "name": "StudioFlow",
            "icon": "🎵",
            "entity": "Track",
            "entities": "Tracks",
            "nav": [["dashboard","📊","Dashboard"],["tracks","🎵","tracks"],["artists","🎤","artists"],["sessions","🎛️","sessions"]],
            "fields": [["title","Track Title","text"],["artist","Artist","text"],["genre","Genre","text"],["duration","Duration","number"],["bpm","BPM","number"],["key","Key","text"],["status","Status","text"]],
            "table_cols": [["title","Track"],["artist","Artist"],["genre","Genre"],["status","Status"]],
            "prompt": "music studio management with track catalog, artist management, recording sessions, mixing workflow and release scheduling"
        },
        "supply_chain": {
            "name": "ChainTrack",
            "icon": "⛓️",
            "entity": "Shipment",
            "entities": "Shipments",
            "nav": [["dashboard","📊","Dashboard"],["shipments","⛓️","shipments"],["suppliers","🏭","suppliers"],["warehouses","🏪","warehouses"]],
            "fields": [["shipment_id","Shipment ID","text"],["supplier","Supplier","text"],["destination","Destination","text"],["items","Items","number"],["weight","Weight kg","number"],["departure","Departure","date"],["status","Status","text"]],
            "table_cols": [["shipment_id","Shipment"],["supplier","Supplier"],["destination","Destination"],["status","Status"]],
            "prompt": "supply chain management with shipment tracking, supplier management, warehouse inventory, delivery scheduling and analytics"
        },
        "mental_wellness": {
            "name": "MindSpace",
            "icon": "🧘",
            "entity": "Session",
            "entities": "Sessions",
            "nav": [["dashboard","📊","Dashboard"],["sessions","🧘","sessions"],["users","👤","users"],["programs","📋","programs"]],
            "fields": [["user","User","text"],["program","Program","text"],["type","Type","text"],["duration","Duration min","number"],["mood_before","Mood Before","number"],["mood_after","Mood After","number"],["notes","Notes","text"]],
            "table_cols": [["user","User"],["program","Program"],["type","Type"],["mood_after","Mood"]],
            "prompt": "mental wellness platform with meditation tracking, mood journaling, guided programs, progress analytics and therapist connection"
        }
    }
    
    added = 0
    configs_path = Path.home() / "organism_templates" / "domain_configs.json"
    for domain_id, config in new_domains.items():
        if domain_id not in configs:
            configs[domain_id] = config
            added += 1
            print(f"  🌱 New domain discovered: {config['name']} ({domain_id})")
    
    if added:
        with open(configs_path, "w") as f:
            json.dump(configs, f, indent=2)
        print(f"  ✅ {added} new domains seeded")
    
    return configs

def main():
    log("="*60)
    log("TURBO EVOLUTION - 200 GENERATIONS + DOMAIN DISCOVERY")
    log("="*60)
    
    configs = load_configs()
    log("🔍 Discovering new domains...")
    configs = discover_new_domains(configs)
    domains = list(configs.keys())
    log(f"📊 Total domains after discovery: {len(domains)}")
    total_generated = 0
    total_crowned = 0
    generation_scores = {}
    
    for gen in range(1, TARGET_GENERATIONS + 1):
        log(f"\n{'='*40}")
        log(f"GENERATION {gen}/{TARGET_GENERATIONS}")
        log(f"{'='*40}")
        
        # Pick domain - prioritize uncovered or low scoring
        uncovered = [d for d in domains if not (CHAMPIONS_DIR / d / "champion.json").exists()]
        low_score = [d for d in domains if (CHAMPIONS_DIR / d / "champion.json").exists() and 
                     json.loads((CHAMPIONS_DIR / d / "champion.json").read_text()).get("score", 0) < 185]
        
        if uncovered:
            domain_id = random.choice(uncovered)
            log(f"🆕 Targeting uncovered: {domain_id}")
        elif low_score:
            domain_id = random.choice(low_score)
            log(f"📈 Targeting low score: {domain_id}")
        else:
            domain_id = random.choice(domains)
            log(f"🔄 Evolving: {domain_id}")
        
        cfg = configs[domain_id]
        current_champ = get_champion(domain_id)
        current_score = current_champ.get("score", 0) if current_champ else 0
        current_gen = current_champ.get("generation", 0) if current_champ else 0
        
        # Generate evolved app
        try:
            app_path = generate_evolved_app(domain_id, cfg, current_gen + 1)
            total_generated += 1
            
            # Score it
            score, breakdown = score_app(app_path, cfg)
            log(f"  Score: {score} (champion: {current_score})")
            
            # Crown if better
            if score > current_score:
                new_gen = save_champion(domain_id, cfg, score, breakdown, app_path, current_gen + 1)
                total_crowned += 1
                log(f"  👑 NEW CHAMPION! {cfg['name']} Gen {new_gen} Score {score}")
            else:
                log(f"  ↩ Champion holds at {current_score}")
            
            # Track scores
            generation_scores[gen] = {"domain": domain_id, "score": score, "crowned": score > current_score}
            
            # Cleanup app to save space
            shutil.rmtree(app_path, ignore_errors=True)
            
        except Exception as e:
            log(f"  ERROR: {e}")
        
        # Progress report every 10 generations
        if gen % 10 == 0:
            covered = len([d for d in domains if (CHAMPIONS_DIR / d / "champion.json").exists()])
            log(f"\n📊 PROGRESS REPORT - Generation {gen}")
            log(f"  Generated: {total_generated} | Crowned: {total_crowned}")
            log(f"  Domains covered: {covered}/{len(domains)}")
    
    # Final report
    log("\n" + "="*60)
    log("TURBO EVOLUTION COMPLETE")
    log("="*60)
    covered = len([d for d in domains if (CHAMPIONS_DIR / d / "champion.json").exists()])
    log(f"  Total generated: {total_generated}")
    log(f"  Total crowned: {total_crowned}")
    log(f"  Domains covered: {covered}/{len(domains)}")
    
    # Save evolution report
    report = {
        "completed_at": datetime.now().isoformat(),
        "generations": TARGET_GENERATIONS,
        "total_generated": total_generated,
        "total_crowned": total_crowned,
        "domains_covered": covered,
        "total_domains": len(domains),
        "generation_scores": generation_scores
    }
    (HOME / "turbo_evolution_report.json").write_text(json.dumps(report, indent=2))
    log(f"  Report: ~/turbo_evolution_report.json")

if __name__ == "__main__":
    main()
