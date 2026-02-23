#!/usr/bin/env python3
"""
AUTONOMOUS_ORGANISM.py
Swarm Platform - App Generation Engine
Author: Jason Tackett
License: Copyright 2026, all rights reserved
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path

HOME = Path.home()
SWARM_DIR = HOME / "swarm-platform"
CONFIGS_FILE = HOME / "organism_templates" / "domain_configs.json"
STATE_FILE = HOME / "organism_state.json"
CHAMPIONS_DIR = HOME / "ORGANISM_ARMY" / "champions"
OUTPUT_DIR = HOME


def load_state():
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text())
    except Exception:
        pass
    return {"cycles": 0, "projects_created": 0}


def save_state(state):
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception as e:
        print(f"[WARNING] Could not save state: {e}")


def load_configs():
    try:
        if CONFIGS_FILE.exists():
            return json.loads(CONFIGS_FILE.read_text())
    except Exception as e:
        print(f"[WARNING] Could not load configs: {e}")
    return {}


def build_backend(domain_id, cfg):
    name = cfg.get("name", "App")
    fields = cfg.get("fields", [])
    table = cfg.get("entities", "Records").lower().replace(" ", "_")
    reserved = {"id", "created_at", "status"}
    domain_fields = [f for f in fields if f[0] not in reserved]

    col_sql = ""
    for f in domain_fields:
        ftype = "REAL" if f[2] == "number" else "DATE" if f[2] == "date" else "TEXT"
        col_sql += f"            {f[0]} {ftype},\n"

    enhancements = random.sample(["search", "stats", "validate"], k=random.randint(1, 3))
    has_search = "search" in enhancements
    has_stats = "stats" in enhancements

    search_route = ""
    if has_search and domain_fields:
        search_route = f"""
@app.route('/api/{table}/search', methods=['GET'])
def search_{table}():
    try:
        q = request.args.get('q', '')
        with get_db() as db:
            rows = db.execute(
                "SELECT * FROM {table} WHERE {domain_fields[0][0]} LIKE ?",
                (f'%{{q}}%',)
            ).fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500
"""

    stats_route = ""
    if has_stats:
        stats_route = f"""
@app.route('/api/stats', methods=['GET'])
def stats():
    try:
        with get_db() as db:
            count = db.execute("SELECT COUNT(*) FROM {table}").fetchone()[0]
        return jsonify({{'total': count, 'domain': '{domain_id}'}})
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500
"""

    insert_fields = ", ".join([f[0] for f in domain_fields])
    insert_placeholders = ", ".join(["?" for _ in domain_fields])
    insert_values = ", ".join([f"data.get('{f[0]}')" for f in domain_fields])

    return f"""#!/usr/bin/env python3
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, jwt, os

app = Flask(__name__)
CORS(app)
SECRET_KEY = 'swarm-{domain_id}-secret'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '{domain_id}.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS {table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
{col_sql}            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.commit()

@app.route('/', methods=['GET'])
def index():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../frontend/index.html')
    return send_file(p)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({{'status': 'healthy', 'app': '{name}', 'timestamp': datetime.now().isoformat()}})

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        hashed = generate_password_hash(data['password'])
        with get_db() as db:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (data['username'], hashed))
            db.commit()
        return jsonify({{'message': 'User created'}})
    except Exception as e:
        return jsonify({{'error': str(e)}}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username=?", (data['username'],)).fetchone()
        if user and check_password_hash(user['password'], data['password']):
            token = jwt.encode({{'user': data['username']}}, SECRET_KEY, algorithm='HS256')
            return jsonify({{'token': token}})
        return jsonify({{'error': 'Invalid credentials'}}), 401
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500

@app.route('/api/{table}', methods=['GET'])
def get_{table}():
    try:
        with get_db() as db:
            rows = db.execute("SELECT * FROM {table} ORDER BY created_at DESC").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500

@app.route('/api/{table}', methods=['POST'])
def create_{table}():
    try:
        data = request.get_json()
        with get_db() as db:
            cursor = db.execute(
                "INSERT INTO {table} ({insert_fields}) VALUES ({insert_placeholders})",
                ({insert_values},)
            )
            db.commit()
        return jsonify({{'id': cursor.lastrowid, 'message': 'Created'}})
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500

@app.route('/api/{table}/<int:item_id>', methods=['GET'])
def get_{table}_item(item_id):
    try:
        with get_db() as db:
            row = db.execute("SELECT * FROM {table} WHERE id=?", (item_id,)).fetchone()
        if not row:
            return jsonify({{'error': 'Not found'}}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500

@app.route('/api/{table}/<int:item_id>', methods=['PUT'])
def update_{table}(item_id):
    try:
        data = request.get_json()
        sets = ", ".join([f"{{k}}=?" for k in data.keys()])
        vals = list(data.values()) + [item_id]
        with get_db() as db:
            db.execute(f"UPDATE {table} SET {{sets}} WHERE id=?", vals)
            db.commit()
        return jsonify({{'message': 'Updated'}})
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500

@app.route('/api/{table}/<int:item_id>', methods=['DELETE'])
def delete_{table}(item_id):
    try:
        with get_db() as db:
            db.execute("DELETE FROM {table} WHERE id=?", (item_id,))
            db.commit()
        return jsonify({{'message': 'Deleted'}})
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500

{search_route}
{stats_route}

if __name__ == '__main__':
    init_db()
    print(f'Starting {name} on http://localhost:5000')
    app.run(debug=False, host='0.0.0.0', port=5000)
"""


def build_frontend(cfg):
    name = cfg.get("name", "App")
    entity = cfg.get("entity", "Record")
    entities = cfg.get("entities", "Records")
    fields = cfg.get("fields", [])
    table = entities.lower().replace(" ", "_")
    nav = cfg.get("nav", [])
    icon = cfg.get("icon", "")
    table_cols = cfg.get("table_cols", fields[:4])
    accent = random.choice(["#2563eb", "#7c3aed", "#059669", "#dc2626", "#d97706", "#0891b2"])

    form_fields = ""
    for f in fields:
        form_fields += (
            f'<div style="margin-bottom:12px">'
            f'<label style="display:block;font-size:12px;font-weight:600;margin-bottom:4px;color:#374151">{f[1]}</label>'
            f'<input type="{f[2]}" id="field_{f[0]}" style="width:100%;padding:8px;border:1px solid #d1d5db;border-radius:4px;box-sizing:border-box;font-size:14px" /></div>'
        )

    headers = ""
    for c in table_cols:
        label = c[1] if len(c) > 1 else c[0]
        headers += f'<th style="padding:10px 12px;text-align:left;font-weight:600;color:#374151">{label}</th>'
    headers += '<th style="padding:10px 12px">Actions</th>'

    nav_html = ""
    for n in nav:
        nav_html += (
            f'<div id="nav_{n[0]}" class="nav-item" data-page="{n[0]}" '
            f'style="padding:10px 16px;cursor:pointer;border-radius:6px;margin-bottom:4px">'
            f'{n[1]} {n[2]}</div>'
        )

    nav_js = ""
    for n in nav:
        nav_js += f"document.getElementById('nav_{n[0]}').onclick = function() {{ setPage('{n[0]}'); }};\n"

    extra_pages = ""
    for n in nav[2:]:
        extra_pages += (
            f'<div id="page_{n[0]}" class="page" style="display:none">'
            f'<h2 style="margin-bottom:16px">{n[2]}</h2>'
            f'<div class="card" style="padding:24px"><p style="color:#6b7280">{n[2]} coming soon.</p></div>'
            f'</div>'
        )

    records_page = nav[1][0] if len(nav) > 1 else "records"
    field_names_js = "[" + ",".join([f'"{f[0]}"' for f in fields]) + "]"
    col_names_js = "[" + ",".join([f'"{c[0]}"' for c in table_cols]) + "]"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{name}</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: system-ui, sans-serif; background: #f8fafc; display: flex; height: 100vh; overflow: hidden; }}
.nav-item:hover {{ background: rgba(255,255,255,0.1); }}
.nav-active {{ background: {accent} !important; }}
table {{ width: 100%; border-collapse: collapse; }}
th {{ background: #f1f5f9; }}
tr:not(:first-child) {{ border-top: 1px solid #e2e8f0; }}
tr:hover {{ background: #f8fafc; }}
input:focus {{ border-color: {accent} !important; outline: none; }}
.btn-primary {{ background: {accent}; color: white; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }}
.btn-secondary {{ background: #e2e8f0; color: #374151; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }}
.btn-danger {{ background: #fee2e2; color: #dc2626; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; }}
.card {{ background: white; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); overflow: hidden; }}
.page {{ display: none; }}
.toast {{ position: fixed; top: 16px; right: 16px; padding: 12px 20px; border-radius: 6px; font-size: 14px; display: none; z-index: 999; }}
#topbar {{ display: none; position: fixed; top: 0; left: 0; right: 0; height: 50px; background: #1e293b; z-index: 200; align-items: center; padding: 0 16px; }}
#overlay {{ display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 201; }}
#sidebar {{ width: 220px; background: #1e293b; color: white; padding: 16px; position: fixed; top: 0; bottom: 0; left: 0; z-index: 202; overflow-y: auto; transform: translateX(-100%); transition: transform 0.3s; }}
#main_content {{ flex: 1; padding: 24px; overflow: auto; }}
</style>
</head>
<body>
<div id="topbar">
  <button onclick="toggleMenu()" style="background:none;border:none;color:white;font-size:26px;cursor:pointer;">&#9776;</button>
  <span style="color:{accent};font-weight:bold;margin-left:12px;font-size:16px;">{icon} {name}</span>
</div>
<div id="overlay" onclick="toggleMenu()"></div>
<div id="sidebar">
  <div style="font-size:18px;font-weight:bold;margin-bottom:24px;color:{accent};">{icon} {name}</div>
  {nav_html}
</div>
<div id="main_content">
  <div id="page_dashboard" class="page">
    <h2 style="margin-bottom:16px">Dashboard</h2>
    <div class="card" style="padding:24px">
      <p style="color:#6b7280">Welcome to {name}.</p>
      <p style="margin-top:12px;color:#6b7280">Total {entities.lower()}: <strong id="dash_count">...</strong></p>
    </div>
  </div>
  <div id="page_{records_page}" class="page">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2>{entities}</h2>
      <button class="btn-primary" onclick="showForm(true)">+ New {entity}</button>
    </div>
    <div id="record_form" class="card" style="padding:24px;margin-bottom:16px;display:none">
      <h3 style="margin-bottom:16px">New {entity}</h3>
      {form_fields}
      <div style="display:flex;gap:8px;margin-top:8px">
        <button class="btn-primary" onclick="saveRecord()">Save</button>
        <button class="btn-secondary" onclick="showForm(false)">Cancel</button>
      </div>
    </div>
    <div class="card" id="loading" style="padding:24px;text-align:center;color:#9ca3af">Loading...</div>
    <div class="card" id="table_wrap" style="display:none">
      <table><thead><tr>{headers}</tr></thead><tbody id="table_body"></tbody></table>
    </div>
  </div>
  {extra_pages}
</div>
<div class="toast" id="toast"></div>
<script>
const API = '/api';
const FIELDS = {field_names_js};
const COLS = {col_names_js};
const TABLE = '{table}';
const RECORDS_PAGE = '{records_page}';

function toast(msg, ok) {{
  var t = document.getElementById('toast');
  t.textContent = msg;
  t.style.background = ok === false ? '#fee2e2' : '#dcfce7';
  t.style.color = ok === false ? '#991b1b' : '#166534';
  t.style.display = 'block';
  setTimeout(function() {{ t.style.display = 'none'; }}, 3000);
}}

function toggleMenu() {{
  var sb = document.getElementById('sidebar');
  var ov = document.getElementById('overlay');
  var open = sb.style.transform === 'translateX(0px)' || sb.style.transform === 'translateX(0%)';
  sb.style.transform = open ? 'translateX(-100%)' : 'translateX(0%)';
  ov.style.display = open ? 'none' : 'block';
}}

function initLayout() {{
  var topbar = document.getElementById('topbar');
  var sidebar = document.getElementById('sidebar');
  var main = document.getElementById('main_content');
  if (window.innerWidth < 768) {{
    topbar.style.display = 'flex';
    main.style.marginTop = '50px';
    main.style.marginLeft = '0';
  }} else {{
    topbar.style.display = 'none';
    sidebar.style.transform = 'translateX(0%)';
    sidebar.style.position = 'relative';
    sidebar.style.flexShrink = '0';
    main.style.marginLeft = '0';
    main.style.marginTop = '0';
  }}
}}

function setPage(page) {{
  document.querySelectorAll('.page').forEach(function(p) {{ p.style.display = 'none'; }});
  document.querySelectorAll('.nav-item').forEach(function(n) {{ n.classList.remove('nav-active'); }});
  var pg = document.getElementById('page_' + page);
  if (pg) pg.style.display = 'block';
  var nav = document.querySelector('[data-page="' + page + '"]');
  if (nav) nav.classList.add('nav-active');
  if (page === RECORDS_PAGE) loadRecords();
  if (page === 'dashboard') loadDash();
  if (window.innerWidth < 768) toggleMenu();
}}

function loadDash() {{
  fetch(API + '/' + TABLE).then(function(r) {{ return r.json(); }}).then(function(d) {{
    document.getElementById('dash_count').textContent = Array.isArray(d) ? d.length : 0;
  }}).catch(function() {{ document.getElementById('dash_count').textContent = '?'; }});
}}

function loadRecords() {{
  document.getElementById('loading').style.display = 'block';
  document.getElementById('table_wrap').style.display = 'none';
  fetch(API + '/' + TABLE).then(function(r) {{ return r.json(); }}).then(function(items) {{
    var tbody = document.getElementById('table_body');
    tbody.innerHTML = '';
    if (!Array.isArray(items) || items.length === 0) {{
      tbody.innerHTML = '<tr><td colspan="99" style="padding:16px;text-align:center;color:#9ca3af">No {entities.lower()} yet.</td></tr>';
    }} else {{
      items.forEach(function(row) {{
        var tr = document.createElement('tr');
        var cells = COLS.map(function(c) {{
          return '<td style="padding:10px 12px">' + (row[c] || '') + '</td>';
        }}).join('');
        cells += '<td style="padding:10px 12px"><button class="btn-danger" onclick="deleteRecord(' + row.id + ')">Delete</button></td>';
        tr.innerHTML = cells;
        tbody.appendChild(tr);
      }});
    }}
    document.getElementById('loading').style.display = 'none';
    document.getElementById('table_wrap').style.display = 'block';
  }}).catch(function() {{
    document.getElementById('loading').textContent = 'Could not connect to backend.';
  }});
}}

function showForm(show) {{
  document.getElementById('record_form').style.display = show ? 'block' : 'none';
  if (!show) FIELDS.forEach(function(f) {{
    var el = document.getElementById('field_' + f);
    if (el) el.value = '';
  }});
}}

function saveRecord() {{
  var data = {{}};
  FIELDS.forEach(function(f) {{
    var el = document.getElementById('field_' + f);
    if (el) data[f] = el.value;
  }});
  fetch(API + '/' + TABLE, {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify(data)
  }}).then(function(r) {{ return r.json(); }}).then(function(d) {{
    if (d.id) {{
      toast('{entity} saved!');
      showForm(false);
      loadRecords();
    }} else {{
      toast(d.error || 'Error saving', false);
    }}
  }}).catch(function() {{ toast('Connection error', false); }});
}}

function deleteRecord(id) {{
  if (!confirm('Delete this record?')) return;
  fetch(API + '/' + TABLE + '/' + id, {{method: 'DELETE'}}).then(function() {{
    toast('Deleted');
    loadRecords();
  }}).catch(function() {{ toast('Delete failed', false); }});
}}

{nav_js}
window.addEventListener('resize', initLayout);
initLayout();
setPage('dashboard');
</script>
</body>
</html>"""


def generate_app(domain_id, cfg):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    app_id = f"professional_app_{timestamp}"
    path = OUTPUT_DIR / app_id
    try:
        path.mkdir(parents=True, exist_ok=True)
        (path / "backend").mkdir(exist_ok=True)
        (path / "frontend").mkdir(exist_ok=True)
        (path / "backend" / "app.py").write_text(build_backend(domain_id, cfg))
        (path / "backend" / "requirements.txt").write_text("flask\nflask-cors\nwerkzeug\npyjwt\n")
        (path / "frontend" / "index.html").write_text(build_frontend(cfg))
        return app_id
    except Exception as e:
        print(f"[ERROR] Failed to generate app: {e}")
        return None


def life_cycle():
    state = load_state()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SWARM ORGANISM ONLINE")
    print(f"  Cycles: {state['cycles']} | Projects: {state['projects_created']}")

    while True:
        try:
            configs = load_configs()
            if not configs:
                print("[WARNING] No domain configs found — retrying in 60s")
                time.sleep(60)
                continue

            state["cycles"] += 1
            domain_id = random.choice(list(configs.keys()))
            cfg = configs[domain_id]

            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            print("=" * 60)
            print(f"LIFE CYCLE {state['cycles']}")
            print("=" * 60)
            print(f"Selected: {cfg.get('icon','')} {cfg.get('name','')}")
            print("Generating...")

            app_id = generate_app(domain_id, cfg)
            if app_id:
                state["projects_created"] += 1
                print(f"Generated: {app_id}")
                print(f"Fields: {len(cfg.get('fields', []))}")
                print(f"Total cycles: {state['cycles']} | Projects: {state['projects_created']}")
            else:
                print("[ERROR] Generation failed — skipping this cycle")

            save_state(state)

        except Exception as e:
            print(f"[ERROR] Cycle failed: {e}")

        print("Resting 300 seconds...")
        time.sleep(300)


if __name__ == "__main__":
    life_cycle()
