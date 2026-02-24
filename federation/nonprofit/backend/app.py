#!/usr/bin/env python3
"""
MissionBase - Generation 5
Turbo Evolved | Domain: nonprofit
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, jwt, os, re

app = Flask(__name__)
CORS(app)
SECRET_KEY = 'swarm-nonprofit-secret-gen5'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nonprofit.db')

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
            role TEXT DEFAULT "user",
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            amount INTEGER,
            date TEXT,
            campaign TEXT,
            status TEXT DEFAULT "active",
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id) REFERENCES users(id)
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            entity_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.commit()

def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "No token"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = data
        except:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/", methods=["GET"])
def index():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend/index.html")
    return send_file(p)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "app": "MissionBase", "generation": 5, "timestamp": datetime.now().isoformat()})

@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not data.get("username") or not data.get("password"):
            return jsonify({"error": "Username and password required"}), 400
        hashed = generate_password_hash(data["password"])
        with get_db() as db:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (data["username"], hashed))
            db.commit()
        return jsonify({"message": "User created successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username=?", (data["username"],)).fetchone()
        if user and check_password_hash(user["password"], data["password"]):
            token = jwt.encode({"user": data["username"], "role": user["role"]}, SECRET_KEY, algorithm="HS256")
            return jsonify({"token": token, "username": data["username"]})
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/donors", methods=["GET"])
@token_required
def get_donors():
    try:
        search = request.args.get("search", "")
        with get_db() as db:
            if search:
                rows = db.execute(
                    "SELECT * FROM donors WHERE " + 
                    search_where +
                    " ORDER BY created_at DESC",
                    [f"%{search}%" for _ in range(3)]
                ).fetchall()
            else:
                rows = db.execute("SELECT * FROM donors ORDER BY created_at DESC").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/donors", methods=["POST"])
@token_required
def create_donor():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute(
                "INSERT INTO donors (name, email, phone, amount, date, campaign) VALUES (?, ?, ?, ?, ?, ?)",
                [data.get(fn, "") for fn in field_names]
            )
            db.commit()
        return jsonify({"message": "Donor created successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/donors/<int:item_id>", methods=["GET"])
@token_required
def get_donor(item_id):
    try:
        with get_db() as db:
            row = db.execute("SELECT * FROM donors WHERE id=?", (item_id,)).fetchone()
        if not row:
            return jsonify({"error": "Donor not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/donors/<int:item_id>", methods=["PUT"])
@token_required
def update_donor(item_id):
    try:
        data = request.get_json()
        with get_db() as db:
            db.execute(
                "UPDATE donors SET name=?, email=?, phone=?, amount=?, date=?, campaign=?, updated_at=? WHERE id=?",
                [data.get(fn, "") for fn in field_names] + [datetime.now().isoformat(), item_id]
            )
            db.commit()
        return jsonify({"message": "Donor updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/donors/<int:item_id>", methods=["DELETE"])
@token_required
def delete_donor(item_id):
    try:
        with get_db() as db:
            db.execute("DELETE FROM donors WHERE id=?", (item_id,))
            db.commit()
        return jsonify({"message": "Donor deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/donors/search", methods=["GET"])
@token_required  
def search_donors():
    try:
        q = request.args.get("q", "")
        with get_db() as db:
            rows = db.execute(
                "SELECT * FROM donors WHERE status LIKE ? ORDER BY created_at DESC LIMIT 50",
                (f"%{q}%",)
            ).fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── TIER 2 FEATURES ──────────────────────────────────────

@app.route("/api/v1/donors", methods=["GET"])
@token_required
def get_donors_v1():
    """API v1 versioned endpoint"""
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        offset = (page - 1) * limit
        with get_db() as db:
            total = db.execute("SELECT COUNT(*) as count FROM donors").fetchone()["count"]
            rows = db.execute("SELECT * FROM donors ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
        return jsonify({
            "data": [dict(r) for r in rows],
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/audit", methods=["GET"])
@token_required
def audit_log():
    """Audit trail endpoint"""
    try:
        with get_db() as db:
            rows = db.execute("SELECT * FROM activity_log ORDER BY created_at DESC LIMIT 100").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "code": 404}), 404

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request", "code": 400}), 400

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error", "code": 500}), 500

@app.route("/api/stats", methods=["GET"])
@token_required
def stats():
    try:
        with get_db() as db:
            total = db.execute("SELECT COUNT(*) as count FROM donors").fetchone()["count"]
            active = db.execute("SELECT COUNT(*) as count FROM donors WHERE status='active'").fetchone()["count"]
            recent = db.execute("SELECT COUNT(*) as count FROM donors WHERE date(created_at) = date('now')").fetchone()["count"]
        return jsonify({"total": total, "active": active, "today": recent, "domain": "nonprofit", "generation": 5})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
