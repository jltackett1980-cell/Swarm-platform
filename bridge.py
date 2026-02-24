#!/usr/bin/env python3
"""
SWARM BRIDGE - Merges swarm champion (SQLite+auth) with Digital Organism structure (React+K8s)
"""
import os, json, re, shutil
from datetime import datetime
from pathlib import Path

HOME = Path.home()
CHAMPIONS_DIR = HOME / "ORGANISM_ARMY" / "champions"
DIGITAL_PROJECTS = HOME / "Digital_Organism_Complete" / "PROJECTS"
BRIDGE_OUTPUT = HOME / "bridge_output"

def get_champion_domains():
    """List all crowned champions"""
    domains = []
    for d in CHAMPIONS_DIR.iterdir():
        if d.is_dir() and (d / "champion.json").exists():
            with open(d / "champion.json") as f:
                info = json.load(f)
            if info.get("score", 0) >= 150:
                domains.append((d.name, info, d))
    return domains

def extract_schema(app_py_path):
    """Extract table definitions from swarm app.py"""
    content = open(app_py_path).read()
    tables = re.findall(r"CREATE TABLE IF NOT EXISTS (\w+) \((.*?)\)\s*'''", content, re.DOTALL)
    return tables

def extract_secret_key(app_py_path):
    content = open(app_py_path).read()
    match = re.search(r"SECRET_KEY = '(.+?)'", content)
    return match.group(1) if match else "swarm-bridge-secret"

def sqlite_to_node_schema(tables):
    """Convert SQLite CREATE TABLE to better-sqlite3 Node.js setup"""
    lines = ["const Database = require('better-sqlite3');",
             "const db = new Database('app.db');",
             "",
             "// Initialize schema",
             "db.exec(`"]
    for table_name, cols in tables:
        lines.append(f"  CREATE TABLE IF NOT EXISTS {table_name} ({cols});")
    lines.append("`);")
    lines.append("")
    lines.append("module.exports = db;")
    return "\n".join(lines)

def get_best_digital_template():
    """Find the most complete Digital Organism project to use as template"""
    best = None
    best_count = 0
    for d in DIGITAL_PROJECTS.iterdir():
        if not d.is_dir():
            continue
        file_count = sum(1 for _ in d.rglob("*") if _.is_file())
        if file_count > best_count:
            best_count = file_count
            best = d
    return best

def build_merged_server_js(app_py_path, secret_key, tables, domain_name, app_name):
    """Build a Node.js server.js using swarm's schema but Digital Organism's structure"""
    
    table_names = [t[0] for t in tables if t[0] != 'users']
    main_entity = table_names[0] if table_names else "items"
    
    return f"""const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const Database = require('better-sqlite3');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;
const SECRET_KEY = '{secret_key}';

// Database setup
const db = new Database(path.join(__dirname, '{domain_name}.db'));
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  {"".join(f'''CREATE TABLE IF NOT EXISTS {t} ({c});''' for t,c in tables if t != 'users')}
`);

// Middleware
app.use(cors());
app.use(helmet());
app.use(morgan('combined'));
app.use(express.json());

// Auth middleware
function authMiddleware(req, res, next) {{
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({{ error: 'No token' }});
  try {{
    req.user = jwt.verify(token, SECRET_KEY);
    next();
  }} catch(e) {{
    res.status(401).json({{ error: 'Invalid token' }});
  }}
}}

// Health check
app.get('/health', (req, res) => {{
  res.json({{ status: 'healthy', app: '{app_name}', timestamp: new Date().toISOString() }});
}});

// Auth routes
app.post('/api/auth/register', async (req, res) => {{
  try {{
    const {{ username, password }} = req.body;
    const hashed = await bcrypt.hash(password, 10);
    const stmt = db.prepare('INSERT INTO users (username, password) VALUES (?, ?)');
    stmt.run(username, hashed);
    res.json({{ message: 'User created' }});
  }} catch(e) {{
    res.status(400).json({{ error: e.message }});
  }}
}});

app.post('/api/auth/login', async (req, res) => {{
  try {{
    const {{ username, password }} = req.body;
    const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);
    if (!user || !(await bcrypt.compare(password, user.password)))
      return res.status(401).json({{ error: 'Invalid credentials' }});
    const token = jwt.sign({{ username }}, SECRET_KEY, {{ expiresIn: '24h' }});
    res.json({{ token }});
  }} catch(e) {{
    res.status(500).json({{ error: e.message }});
  }}
}});

// CRUD routes for {main_entity}
app.get('/api/{main_entity}', authMiddleware, (req, res) => {{
  try {{
    const rows = db.prepare('SELECT * FROM {main_entity} ORDER BY created_at DESC').all();
    res.json(rows);
  }} catch(e) {{
    res.status(500).json({{ error: e.message }});
  }}
}});

app.post('/api/{main_entity}', authMiddleware, (req, res) => {{
  try {{
    const fields = Object.keys(req.body);
    const values = Object.values(req.body);
    const sql = `INSERT INTO {main_entity} (${{fields.join(', ')}}) VALUES (${{fields.map(() => '?').join(', ')}})`;
    const result = db.prepare(sql).run(...values);
    res.json({{ id: result.lastInsertRowid, ...req.body }});
  }} catch(e) {{
    res.status(400).json({{ error: e.message }});
  }}
}});

app.get('/api/{main_entity}/:id', authMiddleware, (req, res) => {{
  try {{
    const row = db.prepare('SELECT * FROM {main_entity} WHERE id = ?').get(req.params.id);
    if (!row) return res.status(404).json({{ error: 'Not found' }});
    res.json(row);
  }} catch(e) {{
    res.status(500).json({{ error: e.message }});
  }}
}});

app.put('/api/{main_entity}/:id', authMiddleware, (req, res) => {{
  try {{
    const fields = Object.keys(req.body);
    const values = Object.values(req.body);
    const sql = `UPDATE {main_entity} SET ${{fields.map(f => f + ' = ?').join(', ')}} WHERE id = ?`;
    db.prepare(sql).run(...values, req.params.id);
    res.json({{ message: 'Updated' }});
  }} catch(e) {{
    res.status(400).json({{ error: e.message }});
  }}
}});

app.delete('/api/{main_entity}/:id', authMiddleware, (req, res) => {{
  try {{
    db.prepare('DELETE FROM {main_entity} WHERE id = ?').run(req.params.id);
    res.json({{ message: 'Deleted' }});
  }} catch(e) {{
    res.status(500).json({{ error: e.message }});
  }}
}});

app.get('/api/stats', authMiddleware, (req, res) => {{
  try {{
    const total = db.prepare('SELECT COUNT(*) as count FROM {main_entity}').get();
    res.json({{ total: total.count, domain: '{domain_name}' }});
  }} catch(e) {{
    res.status(500).json({{ error: e.message }});
  }}
}});

app.listen(PORT, () => console.log(`{app_name} running on port ${{PORT}}`));
"""

def bridge_champion(domain_name, champion_info, champion_dir):
    """Merge one swarm champion with Digital Organism structure"""
    app_py = champion_dir / "backend" / "app.py"
    if not app_py.exists():
        print(f"  ⚠️  No app.py for {domain_name}")
        return False

    template = get_best_digital_template()
    if not template:
        print(f"  ⚠️  No Digital Organism template found")
        return False

    app_name = champion_info.get("name", domain_name)
    score = champion_info.get("score", 0)
    
    print(f"\n  🔗 Bridging: {app_name} (score: {score})")
    
    # Output directory
    # Skip if already bridged today
    existing = list(BRIDGE_OUTPUT.glob(f"{domain_name}_*"))
    if existing:
        print(f"  ⏭️  {domain_name} already bridged, skipping")
        return True
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = BRIDGE_OUTPUT / f"{domain_name}_{ts}"
    
    # Copy Digital Organism template structure
    shutil.copytree(template, out_dir, ignore=shutil.ignore_patterns("node_modules", ".git"))
    
    # Extract swarm schema
    tables = extract_schema(app_py)
    secret_key = extract_secret_key(app_py)
    
    # Write merged server.js
    server_js = build_merged_server_js(app_py, secret_key, tables, domain_name, app_name)
    (out_dir / "backend" / "server.js").write_text(server_js)
    
    # Update package.json to add better-sqlite3
    pkg_path = out_dir / "backend" / "package.json"
    if pkg_path.exists():
        pkg = json.loads(pkg_path.read_text())
        pkg.setdefault("dependencies", {})["better-sqlite3"] = "^9.0.0"
        pkg["name"] = domain_name.lower().replace(" ", "-")
        pkg_path.write_text(json.dumps(pkg, indent=2))
    
    # Write bridge metadata
    meta = {
        "domain": domain_name,
        "name": app_name,
        "swarm_score": score,
        "swarm_generation": champion_info.get("generation", 1),
        "template": template.name,
        "bridged_at": datetime.now().isoformat(),
        "tables": [t[0] for t in tables],
        "bridge_version": "1.0"
    }
    (out_dir / "BRIDGE_METADATA.json").write_text(json.dumps(meta, indent=2))
    
    print(f"  ✅ Output: {out_dir}")
    print(f"  📊 Tables merged: {[t[0] for t in tables]}")
    return True

def main():
    print("\n" + "="*60)
    print("  SWARM BRIDGE v1.0")
    print("  Merging swarm champions with Digital Organism structure")
    print("="*60)
    
    BRIDGE_OUTPUT.mkdir(exist_ok=True)
    
    domains = get_champion_domains()
    print(f"\n  Found {len(domains)} crowned champions (score 185)")
    
    success = 0
    for domain_name, info, path in domains:  # Start with 3 as test
        if bridge_champion(domain_name, info, path):
            success += 1
    
    print(f"\n  ✅ Bridged {success} champions")
    print(f"  📁 Output: {BRIDGE_OUTPUT}")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
