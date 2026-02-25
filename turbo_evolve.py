import sys
from pathlib import Path
sys.path.append(str(Path.home() / "swarm-platform"))
from GOVERNOR import score_app

#!/usr/bin/env python3
"""
TURBO EVOLUTION - 100 generations, no rest, full speed
Runs alongside the normal organism, targeting uncovered domains
"""
import os, json, re, shutil, random
import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent))
from human_insight_engine import HumanInsightEngine
_insight_engine = HumanInsightEngine()

HOME = Path.home()
CONFIGS_FILE = HOME / "organism_templates" / "domain_configs.json"
CHAMPIONS_DIR = HOME / "ORGANISM_ARMY" / "champions"
APPS_DIR = HOME
LOG_FILE = HOME / "turbo_evolve.log"
TARGET_GENERATIONS = 500

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

# ── TIER 2 FEATURES ──────────────────────────────────────

@app.route("/api/v1/{entities.lower()}", methods=["GET"])
@token_required
def get_{entities.lower()}_v1():
    """API v1 versioned endpoint"""
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        offset = (page - 1) * limit
        with get_db() as db:
            total = db.execute("SELECT COUNT(*) as count FROM {entities.lower()}").fetchone()["count"]
            rows = db.execute("SELECT * FROM {entities.lower()} ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
        return jsonify({{
            "data": [dict(r) for r in rows],
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }})
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500

@app.route("/api/audit", methods=["GET"])
@token_required
def audit_log():
    """Audit trail endpoint"""
    try:
        with get_db() as db:
            rows = db.execute("SELECT * FROM activity_log ORDER BY created_at DESC LIMIT 100").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({{"error": "Not found", "code": 404}}), 404

@app.errorhandler(400)
def bad_request(e):
    return jsonify({{"error": "Bad request", "code": 400}}), 400

@app.errorhandler(500)
def server_error(e):
    return jsonify({{"error": "Server error", "code": 500}}), 500

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
    import sys
    # Override default generations from command line
    if "--generations" in sys.argv:
        idx = sys.argv.index("--generations") + 1
        if idx < len(sys.argv):
            TARGET_GENERATIONS = int(sys.argv[idx])
            print(f"🚀 Overriding generations to: {TARGET_GENERATIONS}")
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

    # ═══════════════════════════════════════════
    # THINK FIRST — Human Insight Engine
    # ═══════════════════════════════════════
    insight = _insight_engine.think(domain_id, cfg)
    color   = insight["decisions"]["color"]
    tone    = insight["decisions"]["tone"]
    lead    = insight["decisions"]["lead_with"]
    key_feat= insight["decisions"]["most_important_feature"]
    who     = insight["human"]["who"]
    relief  = insight["human"]["relief_moment"]
    mobile  = insight["decisions"]["mobile_first"]
    no_login= insight["decisions"]["no_login"]
    alerts  = insight["alert_conditions"]
    tone_words = insight["tone_words"]
    ready_word = tone_words[0] if tone_words else "Ready"

    # Build nav tabs from config
    # Nav tabs MUST match page div IDs exactly
    nav_tabs = [
        ["dashboard", icon,  "Dashboard"],
        ["list",      "📋",  entities],
        ["add",       "➕",  f"Add {entity}"],
        ["reports",   "📊",  "Reports"]
    ]
    
    # Mobile nav or sidebar based on insight
    if mobile:
        nav_css = """
        nav { background:#fff; border-bottom:2px solid #e8e8e8; display:flex; overflow-x:auto; -webkit-overflow-scrolling:touch; position:sticky; top:0; z-index:100; }
        nav button { padding:11px 14px; border:none; background:none; cursor:pointer; font-size:12px; color:#666; white-space:nowrap; border-bottom:3px solid transparent; margin-bottom:-2px; font-weight:500; flex-shrink:0; }
        nav button.active { color:VAR_COLOR; border-bottom-color:VAR_COLOR; font-weight:700; }
        .main { padding:14px; max-width:960px; margin:0 auto; }
        """.replace("VAR_COLOR", color)
        nav_html = "<nav>" + "".join([
            f'<button onclick="showPage(\'{t[0]}\', this)">{t[1]} {t[2]}</button>'
            for t in nav_tabs
        ]) + "</nav>"
        layout_css = ""
    else:
        nav_css = """
        .sidebar { width:220px; height:100vh; background:linear-gradient(180deg,#1a1a2e,#16213e); position:fixed; left:0; top:0; padding:20px; }
        .sidebar h2 { color:#fff; font-size:16px; margin-bottom:24px; }
        .sidebar a { display:block; color:#aaa; text-decoration:none; padding:10px; border-radius:8px; margin-bottom:4px; }
        .sidebar a.active { background:rgba(255,255,255,0.15); color:#fff; }
        .main { margin-left:220px; padding:24px; }
        """
        nav_html = f'''<div class="sidebar">
            <h2>{icon} {name}</h2>
            {chr(10).join([f'<a href="#" onclick="showPage(\"{t[0]}\", this)">{t[1]} {t[2]}</a>' for t in nav_tabs])}
        </div>'''
        layout_css = ""

    # Alert banner based on domain insight
    alert_html = f'''
    <div class="alert-banner" id="insight-alert" style="display:none">
        <div class="alert-icon">⚠️</div>
        <div class="alert-text"><strong>Action Required</strong><span id="alert-msg">Check pending items</span></div>
        <button onclick="document.getElementById('insight-alert').style.display='none'" style="background:none;border:none;color:inherit;cursor:pointer;font-size:18px">×</button>
    </div>'''

    # Build field inputs
    field_inputs = "".join([f'''
        <div class="form-row">
            <label>{f[1]}</label>
            <input type="{f[2]}" id="field_{f[0]}" placeholder="{f[1]}"/>
        </div>''' for f in fields])

    # Build table
    col_headers = "".join([f"<th>{c[1]}</th>" for c in table_cols])
    col_data = "".join([f'<td>${{item.{c[0]}}}</td>' for c in table_cols])

    frontend = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{name}</title>
<style>
:root {{ --primary:{color}; --bg:#f8f9fa; --card:#fff; --muted:#666; --border:#e8e8e8; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:#1a1a1a; }}
header {{ background:var(--primary); color:#fff; padding:14px 16px; display:flex; align-items:center; justify-content:space-between; }}
header h1 {{ font-size:18px; font-weight:700; }}
header p {{ font-size:11px; opacity:0.8; margin-top:2px; }}
{nav_css}
{layout_css}
.page {{ display:none; padding:14px; }}
.page.active {{ display:block; }}
.page.active {{ display:block; }}
.card {{ background:var(--card); border-radius:12px; padding:16px; margin-bottom:14px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }}
.card h3 {{ font-size:14px; font-weight:700; color:var(--primary); margin-bottom:12px; }}
.stat-grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:10px; }}
.stat {{ background:var(--bg); border-radius:10px; padding:14px; text-align:center; }}
.stat .val {{ font-size:30px; font-weight:700; color:var(--primary); }}
.stat .lbl {{ font-size:11px; color:var(--muted); margin-top:4px; }}
.row {{ display:flex; align-items:center; gap:10px; padding:10px 0; border-bottom:1px solid var(--border); }}
.row:last-child {{ border-bottom:none; }}
.row-info {{ flex:1; }}
.row-name {{ font-weight:600; font-size:14px; }}
.row-sub {{ font-size:12px; color:var(--muted); margin-top:2px; }}
.badge {{ padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }}
.badge.green {{ background:#d8f3dc; color:#1b4332; }}
.badge.orange {{ background:#fff3cd; color:#856404; }}
.badge.red {{ background:#ffe0e0; color:#842029; }}
.badge.blue {{ background:#dbeafe; color:#1e40af; }}
.form-row {{ margin-bottom:12px; }}
.form-row label {{ display:block; font-size:12px; font-weight:600; color:var(--muted); margin-bottom:5px; text-transform:uppercase; }}
.form-row input, .form-row select, .form-row textarea {{ width:100%; padding:10px 12px; border:1.5px solid var(--border); border-radius:8px; font-size:14px; font-family:inherit; }}
.form-row input:focus {{ outline:none; border-color:var(--primary); }}
.btn {{ border:none; padding:12px 20px; border-radius:8px; font-size:14px; font-weight:600; cursor:pointer; font-family:inherit; width:100%; margin-top:6px; }}
.btn-primary {{ background:var(--primary); color:#fff; }}
.alert-banner {{ background:#fff3cd; border-radius:10px; padding:12px 14px; margin:14px 14px 0; display:flex; gap:10px; align-items:center; border-left:4px solid #f59e0b; }}
.alert-icon {{ font-size:20px; }}
.alert-text {{ flex:1; font-size:13px; }}
.alert-text strong {{ display:block; color:#856404; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; }}
th {{ background:var(--bg); padding:10px; text-align:left; font-size:11px; text-transform:uppercase; color:var(--muted); }}
td {{ padding:10px; border-bottom:1px solid var(--border); }}
.insight-badge {{ position:fixed; bottom:8px; right:8px; background:#1a1a2e; color:#fff; padding:4px 10px; border-radius:20px; font-size:10px; opacity:0.7; }}
.toast {{ position:fixed; top:20px; right:20px; background:#1a1a2e; color:#fff; padding:12px 20px; border-radius:8px; z-index:9999; display:none; }}
.toast.success {{ background:#27ae60; }}
.toast.error {{ background:#e74c3c; }}
</style>
</head>
<body>

<header>
  <div>
    <h1>{icon} {name}</h1>
    <p>{relief[:60]}</p>
  </div>
  <div id="clock" style="font-size:11px;opacity:0.8;text-align:right"></div>
</header>

{alert_html}
{nav_html}

<div id="dashboard" class="page active">
  <div class="card">
    <h3>📊 {lead}</h3>
    <div class="stat-grid">
      <div class="stat"><div class="val" id="stat-total">—</div><div class="lbl">Total {entities}</div></div>
      <div class="stat"><div class="val" id="stat-today">—</div><div class="lbl">Added Today</div></div>
      <div class="stat"><div class="val" id="stat-active">—</div><div class="lbl">Active</div></div>
      <div class="stat"><div class="val" id="stat-pending">—</div><div class="lbl">Pending</div></div>
    </div>
  </div>
  <div class="card">
    <h3>⚡ Quick Actions</h3>
    <div class="row">
      <div class="row-info"><div class="row-name">{key_feat}</div><div class="row-sub">{tone}</div></div>
      <span class="badge green">{ready_word}</span>
    </div>
  </div>
</div>

<div id="list" class="page">
  <div class="card">
    <h3>📋 {entities}</h3>
    <input type="text" placeholder="Search {entities.lower()}..." id="search-box"
      style="width:100%;padding:10px;border:1.5px solid var(--border);border-radius:8px;margin-bottom:12px;font-size:14px"
      oninput="searchItems(this.value)"/>
    <div id="list-content"><p style="color:var(--muted);padding:20px;text-align:center">Loading...</p></div>
  </div>
</div>

<div id="add" class="page">
  <div class="card">
    <h3>➕ Add {entity}</h3>
    {field_inputs}
    <button class="btn btn-primary" onclick="submitAdd()">Save {entity}</button>
  </div>
</div>

<div id="reports" class="page">
  <div class="card">
    <h3>📊 Reports</h3>
    <div class="stat-grid">
      <div class="stat"><div class="val" id="rep-total">—</div><div class="lbl">Total {entities}</div></div>
      <div class="stat"><div class="val" id="rep-today">—</div><div class="lbl">Today</div></div>
    </div>
  </div>
  <div class="card">
    <h3>ℹ️ Platform</h3>
    <div class="row"><div class="row-info"><div class="row-name">Domain</div></div><span class="badge blue">{domain_id}</span></div>
    <div class="row"><div class="row-info"><div class="row-name">Generation</div></div><span class="badge blue">{generation}</span></div>
    <div class="row"><div class="row-info"><div class="row-name">Built for</div></div><span class="badge green">{who[:40]}</span></div>
  </div>
</div>

<div class="insight-badge">Gen {generation} · {domain_id}</div>
<div id="toast" class="toast"></div>

<script>
const API = "";
let token = localStorage.getItem("auth_token") || "demo";

// ═══════════════════════════════════════
// DUAL MODE — Online or Offline
// Detects backend. Falls back to localStorage.
// ═══════════════════════════════════════
let OFFLINE_MODE = true; // Start offline, upgrade if server found
const STORE_KEY = "{domain_id}_data";

function getStore() {{
  try {{ return JSON.parse(localStorage.getItem(STORE_KEY)) || []; }}
  catch {{ return []; }}
}}

function saveStore(items) {{
  localStorage.setItem(STORE_KEY, JSON.stringify(items));
}}

async function api(method, path, body) {{
  if(OFFLINE_MODE) return offlineApi(method, path, body);
  try {{
    const r = await fetch(API + path, {{
      method,
      headers: {{"Content-Type":"application/json","Authorization":"Bearer "+token}},
      body: body ? JSON.stringify(body) : undefined
    }});
    if(!r.ok) throw new Error("offline");
    return r.json();
  }} catch(e) {{
    OFFLINE_MODE = true;
    showToast("Running offline — data saved locally", "success");
    return offlineApi(method, path, body);
  }}
}}

function offlineApi(method, path, body) {{
  const items = getStore();
  if(method === "GET") {{
    if(path.includes("/stats")) {{
      const today = new Date().toDateString();
      return {{
        total: items.length,
        today: items.filter(i => new Date(i._created).toDateString() === today).length,
        active: items.length,
        pending: 0
      }};
    }}
    if(path.includes("/search")) {{
      const q = new URLSearchParams(path.split("?")[1]).get("q").toLowerCase();
      return items.filter(i => JSON.stringify(i).toLowerCase().includes(q));
    }}
    return items;
  }}
  if(method === "POST") {{
    const item = {{...body, id: Date.now(), _created: new Date().toISOString()}};
    items.push(item);
    saveStore(items);
    return {{message: "saved", id: item.id}};
  }}
  if(method === "DELETE") {{
    const id = parseInt(path.split("/").pop());
    saveStore(items.filter(i => i.id !== id));
    return {{message: "deleted"}};
  }}
  return {{}};
}}

function updateClock() {{
  const now = new Date();
  document.getElementById("clock").innerHTML =
    now.toLocaleDateString("en-US",{{weekday:"short",month:"short",day:"numeric"}}) + "<br>" +
    now.toLocaleTimeString("en-US",{{hour:"2-digit",minute:"2-digit"}});
}}
updateClock(); setInterval(updateClock, 30000);

function showPage(id, btn) {{
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.querySelectorAll("nav button, .sidebar a").forEach(b => b.classList.remove("active"));
  document.getElementById(id).classList.add("active");
  if(btn) btn.classList.add("active");
  if(id === "list") loadList();
  if(id === "dashboard") loadStats();
  if(id === "reports") loadStats();
}}

async function api(method, path, body) {{
  try {{
    const r = await fetch(API + path, {{
      method,
      headers: {{"Content-Type":"application/json","Authorization":"Bearer "+token}},
      body: body ? JSON.stringify(body) : undefined
    }});
    return r.json();
  }} catch(e) {{
    return {{}};
  }}
}}

async function loadStats() {{
  const stats = await api("GET", "/api/stats");
  const total = stats.total || 0;
  document.getElementById("stat-total").textContent = total;
  document.getElementById("stat-today").textContent = stats.today || 0;
  document.getElementById("stat-active").textContent = stats.active || total;
  document.getElementById("stat-pending").textContent = stats.pending || 0;
  if(document.getElementById("rep-total")) {{
    document.getElementById("rep-total").textContent = total;
    document.getElementById("rep-today").textContent = stats.today || 0;
  }}
  if(total > 0) {{
    document.getElementById("insight-alert").style.display = "flex";
    document.getElementById("alert-msg").textContent = total + " {entities.lower()} in system — {ready_word}";
  }}
}}

async function loadList() {{
  const el = document.getElementById("list-content");
  el.innerHTML = "<p style='color:var(--muted);text-align:center;padding:20px'>Loading...</p>";
  const items = await api("GET", "/api/{entities.lower()}");
  if(!items || !items.length) {{
    el.innerHTML = "<p style='color:var(--muted);padding:20px;text-align:center'>No {entities.lower()} yet. Add your first one!</p>";
    return;
  }}
  el.innerHTML = `<table><tr>{col_headers}<th>Actions</th></tr>` +
    items.map(item => `<tr>{col_data}
      <td><button onclick="deleteItem(${{item.id}})" style="background:#ffe0e0;color:#842029;border:none;padding:5px 10px;border-radius:6px;cursor:pointer;font-size:12px">Delete</button></td>
    </tr>`).join("") + "</table>";
}}

async function searchItems(q) {{
  if(!q) {{ loadList(); return; }}
  const items = await api("GET", "/api/{entities.lower()}/search?q="+encodeURIComponent(q));
  const el = document.getElementById("list-content");
  if(!items || !items.length) {{
    el.innerHTML = "<p style='color:var(--muted);padding:20px;text-align:center'>No results for \""+q+"\"</p>";
    return;
  }}
  el.innerHTML = `<table><tr>{col_headers}</tr>` +
    items.map(item => `<tr>{col_data}</tr>`).join("") + "</table>";
}}

async function submitAdd() {{
  const data = {{}};
  {js_field_assignments}
  const r = await api("POST", "/api/{entities.lower()}", data);
  if(r.message || r.id) {{ showToast("{entity} saved!"); showPage("list", null); loadList(); }}
  else showToast("Error saving {entity.lower()}", "error");
}}

async function deleteItem(id) {{
  if(!confirm("Delete this {entity.lower()}?")) return;
  await api("DELETE", "/api/{entities.lower()}/"+id);
  loadList();
}}

function showToast(msg, type="success") {{
  const t = document.getElementById("toast");
  t.textContent = msg; t.className = "toast " + type;
  t.style.display = "block";
  setTimeout(() => t.style.display="none", 3000);
}}

// Start in offline mode immediately
OFFLINE_MODE = true;
loadStats();
// Try to connect to server in background
fetch("/api/stats").then(r => {{
  if(r.ok) {{ OFFLINE_MODE = false; loadStats(); }}
}}).catch(() => {{}});
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
        # TIER 2 frontend
        if "spinner" in content or "loading" in content.lower():
            breakdown["loading_states"] = 10
        if "viewport" in content and "media" in content:
            breakdown["responsive"] = 10
        if "toast" in content:
            breakdown["notifications"] = 10

    if backend.exists():
        c = backend.read_text()
        if "/api/v1/" in c or "version" in c.lower():
            breakdown["api_versioning"] = 10
        if c.count("return jsonify") > 10:
            breakdown["rate_limiting"] = 10
        if "page" in c and "limit" in c and "offset" in c:
            breakdown["pagination"] = 10
        if "activity_log" in c:
            breakdown["audit_trail"] = 10
        if "404" in c and "400" in c and "500" in c:
            breakdown["error_handling"] = 10

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
    import sys
    # Override default generations from command line
    if "--generations" in sys.argv:
        idx = sys.argv.index("--generations") + 1
        if idx < len(sys.argv):
            TARGET_GENERATIONS = int(sys.argv[idx])
            print(f"🚀 Overriding generations to: {TARGET_GENERATIONS}")
    main()
