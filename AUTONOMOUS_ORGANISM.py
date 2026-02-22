#!/usr/bin/env python3
import os, json, time, random
from pathlib import Path
from datetime import datetime

home = Path.home()
CONFIGS_FILE = home / "organism_templates" / "domain_configs.json"
STATE_FILE = home / "organism_state.json"

def load_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except:
        return {"cycles": 0, "projects_created": 0}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def load_configs():
    if CONFIGS_FILE.exists():
        return json.loads(CONFIGS_FILE.read_text())
    return {}

def build_backend(domain_id, cfg):
    entity = cfg.get("entity", "Record")
    entities = cfg.get("entities", "Records")
    fields = cfg.get("fields", [])
    table = entities.lower().replace(" ", "_")

    col_defs = []
    reserved = {"status", "id", "created_at"}
    for f in fields:
        if f[0] in reserved: continue
        fname, flabel, ftype = f[0], f[1], f[2]
        if ftype == "number":
            col_defs.append('"' + fname + '" REAL')
        elif ftype == "date":
            col_defs.append('"' + fname + '" DATE')
        else:
            col_defs.append('"' + fname + '" TEXT')
    cols_sql = ",\n               ".join(col_defs)

    field_names = [f[0] for f in fields]
    placeholders = ", ".join(["?" for _ in field_names])
    insert_cols = ", ".join(field_names)
    insert_vals = ", ".join(["data.get('" + f + "')" for f in field_names])
    search_field = next((f[0] for f in fields if f[2] == "text"), "name")

    enhancements = []
    if random.random() > 0.5: enhancements.append("search")
    if random.random() > 0.6: enhancements.append("stats")
    if random.random() > 0.7: enhancements.append("validation")

    search_route = ""
    if "search" in enhancements:
        search_route = (
            "\n@app.route('/api/" + table + "/search', methods=['GET'])\n"
            "def search_" + table + "():\n"
            "    q = request.args.get('q', '')\n"
            "    db = get_db()\n"
            "    items = db.execute('SELECT * FROM " + table + " WHERE " + search_field + " LIKE ?', ('%'+q+'%',)).fetchall()\n"
            "    return jsonify([dict(i) for i in items])\n"
        )

    stats_route = ""
    if "stats" in enhancements:
        stats_route = (
            "\n@app.route('/api/" + table + "/stats', methods=['GET'])\n"
            "def stats_" + table + "():\n"
            "    db = get_db()\n"
            "    total = db.execute('SELECT COUNT(*) as c FROM " + table + "').fetchone()['c']\n"
            "    return jsonify({'total': total, 'entity': '" + entity + "'})\n"
        )

    validation = ""
    if "validation" in enhancements and field_names:
        req = field_names[:2]
        validation = (
            "    required = " + repr(req) + "\n"
            "    for rf in required:\n"
            "        if not data.get(rf):\n"
            "            return jsonify({'error': rf + ' is required'}), 400\n"
        )

    app_name = cfg.get("name", "App")

    code = (
        "import os\nimport sqlite3\nfrom datetime import datetime\n"
        "from flask import Flask, request, jsonify, g\n"
        "from flask_cors import CORS\n"
        "from werkzeug.security import generate_password_hash, check_password_hash\n"
        "import jwt\n\n"
        "app = Flask(__name__)\nCORS(app)\n"
        "app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-in-production')\n"
        "app.config['DATABASE'] = 'app.db'\n\n"
        "def get_db():\n"
        "    db = getattr(g, '_database', None)\n"
        "    if db is None:\n"
        "        db = g._database = sqlite3.connect(app.config['DATABASE'])\n"
        "        db.row_factory = sqlite3.Row\n"
        "    return db\n\n"
        "@app.teardown_appcontext\n"
        "def close_db(error):\n"
        "    db = getattr(g, '_database', None)\n"
        "    if db is not None: db.close()\n\n"
        "def init_db():\n"
        "    db = get_db()\n"
        "    db.execute('''CREATE TABLE IF NOT EXISTS users (\n"
        "               id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "               email TEXT UNIQUE NOT NULL,\n"
        "               username TEXT UNIQUE NOT NULL,\n"
        "               password_hash TEXT NOT NULL,\n"
        "               role TEXT DEFAULT 'user',\n"
        "               created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')\n"
        "    db.execute('''CREATE TABLE IF NOT EXISTS " + table + " (\n"
        "               id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "               " + cols_sql + ",\n"
        "               status TEXT DEFAULT 'active',\n"
        "               created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')\n"
        "    db.commit()\n\n"
        "@app.route('/', methods=['GET'])\n"
        "def index():\n"
        "    from flask import send_file\n"
        "    import os\n"
        "    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../frontend/index.html')\n"
        "    return send_file(p)\n\n"
        "@app.route('/api/health', methods=['GET'])\n"
        "def health():\n"
        "    return jsonify({'status': 'healthy', 'app': '" + app_name + "', 'timestamp': datetime.now().isoformat()})\n\n"
        "@app.route('/api/auth/register', methods=['POST'])\n"
        "def register():\n"
        "    data = request.get_json()\n"
        "    db = get_db()\n"
        "    if db.execute('SELECT id FROM users WHERE email = ?', (data['email'],)).fetchone():\n"
        "        return jsonify({'error': 'Email exists'}), 409\n"
        "    pw = generate_password_hash(data['password'])\n"
        "    cursor = db.execute('INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)',\n"
        "                       (data['email'], data.get('username', data['email']), pw))\n"
        "    db.commit()\n"
        "    return jsonify({'message': 'User created', 'user_id': cursor.lastrowid}), 201\n\n"
        "@app.route('/api/auth/login', methods=['POST'])\n"
        "def login():\n"
        "    data = request.get_json()\n"
        "    db = get_db()\n"
        "    user = db.execute('SELECT * FROM users WHERE email = ?', (data.get('username',''),)).fetchone()\n"
        "    if user and check_password_hash(user['password_hash'], data.get('password','')):\n"
        "        token = jwt.encode({'user_id': user['id']}, app.config['SECRET_KEY'], algorithm='HS256')\n"
        "        return jsonify({'token': token, 'user': dict(user)})\n"
        "    return jsonify({'error': 'Invalid credentials'}), 401\n\n"
        "@app.route('/api/" + table + "', methods=['GET'])\n"
        "def get_" + table + "():\n"
        "    db = get_db()\n"
        "    items = db.execute('SELECT * FROM " + table + " ORDER BY created_at DESC').fetchall()\n"
        "    return jsonify([dict(i) for i in items])\n\n"
        "@app.route('/api/" + table + "', methods=['POST'])\n"
        "def create_" + table + "():\n"
        "    data = request.get_json()\n"
        "    db = get_db()\n"
        + validation +
        "    cursor = db.execute('INSERT INTO " + table + " (" + insert_cols + ") VALUES (" + placeholders + ")',\n"
        "                       (" + insert_vals + ",))\n"
        "    db.commit()\n"
        "    return jsonify({'id': cursor.lastrowid, 'message': '" + entity + " created'}), 201\n\n"
        "@app.route('/api/" + table + "/<int:item_id>', methods=['DELETE'])\n"
        "def delete_" + entity.lower() + "(item_id):\n"
        "    db = get_db()\n"
        "    db.execute('DELETE FROM " + table + " WHERE id = ?', (item_id,))\n"
        "    db.commit()\n"
        "    return jsonify({'message': '" + entity + " deleted'})\n"
        + search_route + stats_route +
        "\nif __name__ == '__main__':\n"
        "    with app.app_context():\n"
        "        init_db()\n"
        "    app.run(host='0.0.0.0', port=5000, debug=True)\n"
    )
    return code

def build_frontend(cfg):
    """Single HTML file — no Node, no React, works in any browser"""
    name = cfg.get("name", "App")
    entity = cfg.get("entity", "Record")
    entities = cfg.get("entities", "Records")
    fields = cfg.get("fields", [])
    table = entities.lower().replace(" ", "_")
    nav = cfg.get("nav", [])
    icon = cfg.get("icon", "")
    table_cols = cfg.get("table_cols", fields[:4])
    accent = random.choice(["#2563eb","#7c3aed","#059669","#dc2626","#d97706"])

    # Form fields HTML
    form_fields = ""
    for f in fields:
        form_fields += (
            "<div style=\"margin-bottom:12px\">"
            "<label style=\"display:block;font-size:12px;font-weight:600;margin-bottom:4px;color:#374151\">" + f[1] + "</label>"
            "<input type=\"" + f[2] + "\" id=\"field_" + f[0] + "\" "
            "style=\"width:100%;padding:8px;border:1px solid #d1d5db;border-radius:4px;box-sizing:border-box;font-size:14px\" />"
            "</div>"
        )

    # Table headers
    headers = ""
    for c in table_cols:
        label = c[1] if len(c) > 1 else c[0]
        headers += "<th style=\"padding:10px 12px;text-align:left;font-weight:600;color:#374151\">" + label + "</th>"
    headers += "<th style=\"padding:10px 12px\">Actions</th>"

    # Nav items JS
    nav_items = ""
    for n in nav:
        nav_items += (
            "document.getElementById('nav_" + n[0] + "').onclick = function() { setPage('" + n[0] + "')" + "; };\n"
        )

    nav_html = ""
    for n in nav:
        nav_html += (
            "<div id=\"nav_" + n[0] + "\" class=\"nav-item\" data-page=\"" + n[0] + "\" "
            "style=\"padding:10px 16px;cursor:pointer;border-radius:6px;margin-bottom:4px\">"
            + n[1] + " " + n[2] +
            "</div>"
        )

    # Field names for JS form collection
    field_names_js = "[" + ",".join(['"' + f[0] + '"' for f in fields]) + "]"
    col_names_js = "[" + ",".join(['"' + c[0] + '"' for c in table_cols]) + "]"

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>""" + name + """</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; background: #f8fafc; }
  .nav-item:hover { background: rgba(255,255,255,0.1); }
  .nav-active { background: """ + accent + """ !important; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #f1f5f9; }
  tr:not(:first-child) { border-top: 1px solid #e2e8f0; }
  tr:hover { background: #f8fafc; }
  input, select { outline: none; }
  input:focus { border-color: """ + accent + """ !important; }
  .btn-primary { background: """ + accent + """; color: white; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
  .btn-secondary { background: #e2e8f0; color: #374151; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
  .btn-danger { background: #fee2e2; color: #dc2626; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; }
  .card { background: white; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); overflow: hidden; }
  .toast { position: fixed; top: 16px; right: 16px; padding: 12px 20px; border-radius: 6px; background: #dcfce7; color: #166534; font-size: 14px; display: none; z-index: 999; }
</style>
</head>
<body>
<div style="display:flex;height:100vh;">

  <!-- Sidebar -->
  <div id="topbar" style="display:none;position:fixed;top:0;left:0;right:0;height:50px;background:#1e293b;z-index:200;align-items:center;padding:0 16px;">
    <button onclick="toggleMenu()" style="background:none;border:none;color:white;font-size:26px;cursor:pointer;line-height:1;">&#9776;</button>
    <span style="color:""" + accent + """;font-weight:bold;margin-left:12px;font-size:16px;">""" + icon + " " + name + """</span>
  </div>
  <div id="overlay" onclick="toggleMenu()" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:201;"></div>
  <div id="sidebar" style="width:220px;background:#1e293b;color:white;padding:16px;position:fixed;top:0;bottom:0;left:0;z-index:202;overflow-y:auto;transform:translateX(-100%);transition:transform 0.3s;">
    <div style="font-size:18px;font-weight:bold;margin-bottom:24px;color:""" + accent + """;">""" + icon + " " + name + """</div>
""" + nav_html + """
  </div>

  <!-- Main -->
  <div id="main_content" style="flex:1;padding:24px;overflow:auto;">
    <div id="page_dashboard" class="page">
      <h2 style="margin-bottom:16px;">Dashboard</h2>
      <div class="card" style="padding:24px;">
        <p style="color:#6b7280;">Welcome to """ + name + """. Use the sidebar to navigate.</p>
        <p style="margin-top:12px;color:#6b7280;">Total records: <strong id="dash_count">...</strong></p>
      </div>
    </div>

    <div id="page_""" + (nav[1][0] if len(nav) > 1 else "records") + """" class="page" style="display:none;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <h2>""" + entities + """</h2>
        <button class="btn-primary" onclick="showForm(true)">+ New """ + entity + """</button>
      </div>

      <!-- Form -->
      <div id="record_form" class="card" style="padding:24px;margin-bottom:16px;display:none;">
        <h3 style="margin-bottom:16px;">New """ + entity + """</h3>
""" + form_fields + """
        <div style="display:flex;gap:8px;margin-top:8px;">
          <button class="btn-primary" onclick="saveRecord()">Save</button>
          <button class="btn-secondary" onclick="showForm(false)">Cancel</button>
        </div>
      </div>

      <!-- Table -->
      <div class="card" id="loading" style="padding:24px;text-align:center;color:#9ca3af;">Loading...</div>
      <div class="card" id="table_wrap" style="display:none;">
        <table>
          <thead><tr>""" + headers + """</tr></thead>
          <tbody id="table_body"></tbody>
        </table>
      </div>
    </div>

    <div id="page_reports" class="page" style="display:none;">
      <h2 style="margin-bottom:16px;">Reports</h2>
      <div class="card" style="padding:24px;">
        <p>Total """ + entities.lower() + """: <strong id="report_count">...</strong></p>
      </div>
    </div>

    <div id="page_settings" class="page" style="display:none;">
      <h2 style="margin-bottom:16px;">Settings</h2>
      <div class="card" style="padding:24px;">
        <p style="color:#6b7280;">""" + name + """ v1.0</p>
      </div>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const API = '/api';
const FIELDS = """ + field_names_js + """;
const COLS = """ + col_names_js + """;

function toast(msg, ok) {
  var t = document.getElementById('toast');
  t.textContent = msg;
  t.style.background = ok === false ? '#fee2e2' : '#dcfce7';
  t.style.color = ok === false ? '#991b1b' : '#166534';
  t.style.display = 'block';
  setTimeout(function() { t.style.display = 'none'; }, 3000);
}

function setPage(page) {
  document.querySelectorAll('.page').forEach(function(p) { p.style.display = 'none'; });
  document.querySelectorAll('.nav-item').forEach(function(n) { n.classList.remove('nav-active'); });
  var pg = document.getElementById('page_' + page);
  if (pg) pg.style.display = 'block';
  var nav = document.querySelector('[data-page="' + page + '"]');
  if (nav) nav.classList.add('nav-active');
  if (page === '""" + (nav[1][0] if len(nav) > 1 else "records") + """') loadRecords();
  if (page === 'dashboard') loadDash();
  if (page === 'reports') loadReports();
}

function loadDash() {
  fetch(API + '/""" + table + """').then(function(r) { return r.json(); }).then(function(d) {
    document.getElementById('dash_count').textContent = Array.isArray(d) ? d.length : 0;
  });
}

function loadReports() {
  fetch(API + '/""" + table + """').then(function(r) { return r.json(); }).then(function(d) {
    document.getElementById('report_count').textContent = Array.isArray(d) ? d.length : 0;
  });
}

function loadRecords() {
  document.getElementById('loading').style.display = 'block';
  document.getElementById('table_wrap').style.display = 'none';
  fetch(API + '/""" + table + """').then(function(r) { return r.json(); }).then(function(items) {
    var tbody = document.getElementById('table_body');
    tbody.innerHTML = '';
    if (!Array.isArray(items) || items.length === 0) {
      tbody.innerHTML = '<tr><td colspan="99" style="padding:16px;text-align:center;color:#9ca3af;">No """ + entities.lower() + """ yet. Click + New """ + entity + """ to add one.</td></tr>';
    } else {
      items.forEach(function(row) {
        var tr = document.createElement('tr');
        var cells = COLS.map(function(c) {
          return '<td style="padding:10px 12px;">' + (row[c] || '') + '</td>';
        }).join('');
        cells += '<td style="padding:10px 12px;"><button class="btn-danger" onclick="deleteRecord(' + row.id + ')">Delete</button></td>';
        tr.innerHTML = cells;
        tbody.appendChild(tr);
      });
    }
    document.getElementById('loading').style.display = 'none';
    document.getElementById('table_wrap').style.display = 'block';
  }).catch(function() {
    document.getElementById('loading').textContent = 'Could not connect to backend.';
  });
}

function showForm(show) {
  document.getElementById('record_form').style.display = show ? 'block' : 'none';
  if (!show) FIELDS.forEach(function(f) {
    var el = document.getElementById('field_' + f);
    if (el) el.value = '';
  });
}

function saveRecord() {
  var data = {};
  FIELDS.forEach(function(f) {
    var el = document.getElementById('field_' + f);
    if (el) data[f] = el.value;
  });
  fetch(API + '/""" + table + """', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  }).then(function(r) { return r.json(); }).then(function(d) {
    if (d.id) {
      toast('""" + entity + """ saved!');
      showForm(false);
      loadRecords();
    } else {
      toast(d.error || 'Error saving', false);
    }
  }).catch(function() { toast('Connection error', false); });
}

function deleteRecord(id) {
  if (!confirm('Delete this record?')) return;
  fetch(API + '/""" + table + """/' + id, {method: 'DELETE'}).then(function() {
    toast('Deleted');
    loadRecords();
  });
}

// Mobile menu
function toggleMenu() {
  var sb = document.getElementById('sidebar');
  var ov = document.getElementById('overlay');
  var open = sb.style.transform === 'translateX(0px)' || sb.style.transform === 'translateX(0%)';
  sb.style.transform = open ? 'translateX(-100%)' : 'translateX(0%)';
  ov.style.display = open ? 'none' : 'block';
}

function initLayout() {
  var topbar = document.getElementById('topbar');
  var sidebar = document.getElementById('sidebar');
  var main = document.getElementById('main_content');
  if (window.innerWidth < 768) {
    topbar.style.display = 'flex';
    main.style.marginTop = '50px';
    main.style.marginLeft = '0';
  } else {
    topbar.style.display = 'none';
    sidebar.style.transform = 'translateX(0%)';
    sidebar.style.position = 'relative';
    sidebar.style.flexShrink = '0';
    main.style.marginLeft = '0';
    main.style.marginTop = '0';
  }
}

window.addEventListener('resize', initLayout);
initLayout();

// Nav click handlers
""" + nav_items + """

// Start
setPage('dashboard');
</script>
</body>
</html>"""
    return html

def build_frontend_files(cfg, path):
    """Write single HTML file served by Flask"""
    html = build_frontend(cfg)
    (path / "frontend").mkdir(exist_ok=True)
    (path / "frontend" / "index.html").write_text(html)


class AutonomousOrganism:
    def __init__(self):
        state = load_state()
        self.cycles = state.get("cycles", 0)
        self.projects_created = state.get("projects_created", 0)
        self.running = True

    def generate_app(self, domain_id, cfg):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        app_id = "professional_app_" + timestamp
        path = home / app_id
        path.mkdir(parents=True, exist_ok=True)
        (path / "backend").mkdir(exist_ok=True)
        (path / "frontend" / "src").mkdir(parents=True, exist_ok=True)
        (path / "frontend" / "public").mkdir(exist_ok=True)

        (path / "backend" / "app.py").write_text(build_backend(domain_id, cfg))
        (path / "backend" / "requirements.txt").write_text("flask\nflask-cors\nwerkzeug\npyjwt\n")
        (path / "frontend" / "src" / "App.js").write_text(build_frontend(cfg))
        (path / "frontend" / "src" / "index.js").write_text(
            "import React from 'react';\n"
            "import ReactDOM from 'react-dom/client';\n"
            "import App from './App';\n"
            "const root = ReactDOM.createRoot(document.getElementById('root'));\n"
            "root.render(<React.StrictMode><App /></React.StrictMode>);\n"
        )
        (path / "frontend" / "public" / "index.html").write_text(
            '<!DOCTYPE html><html><head><meta charset="utf-8"/><title>' + cfg["name"] + '</title></head>'
            '<body><div id="root"></div></body></html>\n'
        )
        (path / "frontend" / "package.json").write_text(json.dumps({
            "name": domain_id,
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            },
            "scripts": {"start": "react-scripts start", "build": "react-scripts build"}
        }, indent=2))
        return app_id

    def life_cycle(self):
        while self.running:
            print("\n[" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "]")
            print("=" * 60)
            print("LIFE CYCLE " + str(self.cycles))
            print("=" * 60)

            configs = load_configs()
            domain_ids = list(configs.keys())
            if not domain_ids:
                print("No domain configs found — check " + str(CONFIGS_FILE))
                time.sleep(60)
                continue

            domain_id = domain_ids[self.cycles % len(domain_ids)]
            cfg = configs[domain_id]
            print("Selected: " + cfg.get("icon","") + " " + cfg["name"])
            print("Generating...")

            app_id = self.generate_app(domain_id, cfg)
            self.cycles += 1
            self.projects_created += 1
            save_state({"cycles": self.cycles, "projects_created": self.projects_created})

            print("Generated: " + app_id)
            print("Fields: " + str(len(cfg.get("fields",[]))))
            print("Total cycles: " + str(self.cycles) + " | Projects: " + str(self.projects_created))
            print("Resting 300 seconds...")
            time.sleep(300)

if __name__ == "__main__":
    org = AutonomousOrganism()
    org.life_cycle()
