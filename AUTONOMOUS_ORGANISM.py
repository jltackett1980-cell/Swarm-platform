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
    name = cfg.get("name", "App")
    entity = cfg.get("entity", "Record")
    entities = cfg.get("entities", "Records")
    fields = cfg.get("fields", [])
    table = entities.lower().replace(" ", "_")
    nav = cfg.get("nav", [])
    icon = cfg.get("icon", "")
    table_cols = cfg.get("table_cols", fields[:4])
    accent = random.choice(["#2563eb","#7c3aed","#059669","#dc2626","#d97706"])
    default_page = nav[1][0] if len(nav) > 1 else "dashboard"

    form_fields = ""
    for f in fields:
        form_fields += (
            "        <div style={{marginBottom:8}}>\n"
            "          <label style={{display:'block',fontSize:12,marginBottom:4}}>" + f[1] + "</label>\n"
            "          <input type='" + f[2] + "' style={{width:'100%',padding:'8px',border:'1px solid #e2e8f0',borderRadius:4,boxSizing:'border-box'}}\n"
            "            value={formData['" + f[0] + "'] || ''}\n"
            "            onChange={e => setFormData({...formData, '" + f[0] + "': e.target.value})}/>\n"
            "        </div>\n"
        )

    headers = ""
    for c in table_cols:
        label = c[1] if len(c) > 1 else c[0]
        headers += "              <th style={{padding:'8px',textAlign:'left'}}>" + label + "</th>\n"
    headers += "              <th style={{padding:'8px'}}>Actions</th>\n"

    cells = ""
    for c in table_cols:
        cells += "              <td style={{padding:'8px'}}>{row['" + c[0] + "']}</td>\n"
    cells += "              <td style={{padding:'8px'}}><button onClick={()=>deleteItem(row.id)} style={{background:'#fee2e2',color:'#dc2626',border:'none',padding:'4px 8px',borderRadius:4,cursor:'pointer'}}>Delete</button></td>\n"

    nav_items = ""
    for n in nav:
        nav_items += (
            "        <div style={{padding:'10px 16px',cursor:'pointer',borderRadius:6,\n"
            "          background:page==='" + n[0] + "'?'" + accent + "':'transparent'}}\n"
            "          onClick={()=>setPage('" + n[0] + "')}>\n"
            "          " + n[1] + " " + n[2] + "\n"
            "        </div>\n"
        )

    code = (
        "import React, {useState, useEffect} from 'react';\n\n"
        "const API = 'http://localhost:5000/api';\n\n"
        "function App() {\n"
        "  const [page, setPage] = useState('" + default_page + "');\n"
        "  const [items, setItems] = useState([]);\n"
        "  const [formData, setFormData] = useState({});\n"
        "  const [showForm, setShowForm] = useState(false);\n"
        "  const [loading, setLoading] = useState(false);\n"
        "  const [message, setMessage] = useState('');\n\n"
        "  useEffect(() => { loadItems(); }, [page]);\n\n"
        "  const loadItems = async () => {\n"
        "    setLoading(true);\n"
        "    try {\n"
        "      const res = await fetch(API + '/" + table + "');\n"
        "      const data = await res.json();\n"
        "      setItems(Array.isArray(data) ? data : []);\n"
        "    } catch(e) { setMessage('Connection error'); }\n"
        "    setLoading(false);\n"
        "  };\n\n"
        "  const saveItem = async () => {\n"
        "    try {\n"
        "      const res = await fetch(API + '/" + table + "', {\n"
        "        method: 'POST',\n"
        "        headers: {'Content-Type': 'application/json'},\n"
        "        body: JSON.stringify(formData)\n"
        "      });\n"
        "      const data = await res.json();\n"
        "      if (res.ok) { setMessage('" + entity + " saved!'); setShowForm(false); setFormData({}); loadItems(); }\n"
        "      else { setMessage(data.error || 'Error saving'); }\n"
        "    } catch(e) { setMessage('Connection error'); }\n"
        "  };\n\n"
        "  const deleteItem = async (id) => {\n"
        "    if (!window.confirm('Delete?')) return;\n"
        "    await fetch(API + '/" + table + "/' + id, {method: 'DELETE'});\n"
        "    loadItems();\n"
        "  };\n\n"
        "  return (\n"
        "    <div style={{display:'flex',height:'100vh',fontFamily:'system-ui,sans-serif',background:'#f8fafc'}}>\n"
        "      <div style={{width:220,background:'#1e293b',color:'white',padding:16}}>\n"
        "        <div style={{fontSize:20,fontWeight:'bold',marginBottom:24,color:'" + accent + "'}}>" + icon + " " + name + "</div>\n"
        + nav_items +
        "      </div>\n"
        "      <div style={{flex:1,padding:24,overflow:'auto'}}>\n"
        "        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:16}}>\n"
        "          <h2 style={{margin:0}}>" + entities + "</h2>\n"
        "          <button onClick={()=>setShowForm(true)}\n"
        "            style={{background:'" + accent + "',color:'white',border:'none',padding:'8px 16px',borderRadius:6,cursor:'pointer'}}>\n"
        "            + New " + entity + "\n"
        "          </button>\n"
        "        </div>\n"
        "        {message && <div style={{background:'#dcfce7',padding:8,borderRadius:4,marginBottom:12}}>{message}</div>}\n"
        "        {showForm && (\n"
        "          <div style={{background:'white',padding:24,borderRadius:8,marginBottom:16,boxShadow:'0 2px 8px rgba(0,0,0,0.1)'}}>\n"
        "            <h3 style={{marginTop:0}}>New " + entity + "</h3>\n"
        + form_fields +
        "            <div style={{marginTop:16,display:'flex',gap:8}}>\n"
        "              <button onClick={saveItem} style={{background:'" + accent + "',color:'white',border:'none',padding:'8px 20px',borderRadius:6,cursor:'pointer'}}>Save</button>\n"
        "              <button onClick={()=>setShowForm(false)} style={{background:'#e2e8f0',border:'none',padding:'8px 20px',borderRadius:6,cursor:'pointer'}}>Cancel</button>\n"
        "            </div>\n"
        "          </div>\n"
        "        )}\n"
        "        {loading ? <p>Loading...</p> : (\n"
        "          <div style={{background:'white',borderRadius:8,overflow:'hidden',boxShadow:'0 1px 4px rgba(0,0,0,0.1)'}}>\n"
        "            <table style={{width:'100%',borderCollapse:'collapse'}}>\n"
        "              <thead style={{background:'#f1f5f9'}}><tr>\n"
        + headers +
        "              </tr></thead>\n"
        "              <tbody>\n"
        "                {items.map(row => (\n"
        "                  <tr key={row.id} style={{borderTop:'1px solid #e2e8f0'}}>\n"
        + cells +
        "                  </tr>\n"
        "                ))}\n"
        "                {items.length === 0 && <tr><td colSpan={99} style={{padding:16,textAlign:'center',color:'#94a3b8'}}>No " + entities.lower() + " yet</td></tr>}\n"
        "              </tbody>\n"
        "            </table>\n"
        "          </div>\n"
        "        )}\n"
        "      </div>\n"
        "    </div>\n"
        "  );\n"
        "}\n\n"
        "export default App;\n"
    )
    return code

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
