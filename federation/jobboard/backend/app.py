#!/usr/bin/env python3
"""
HireLocal - Generation 3
Turbo Evolved | Domain: jobboard
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, jwt, os, re

app = Flask(__name__)
CORS(app)
SECRET_KEY = 'swarm-jobboard-secret-gen3'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jobboard.db')

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
        db.execute('''CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            salary TEXT,
            type TEXT,
            posted TEXT,
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
    return jsonify({"status": "healthy", "app": "HireLocal", "generation": 3, "timestamp": datetime.now().isoformat()})

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

@app.route("/api/jobs", methods=["GET"])
@token_required
def get_jobs():
    try:
        search = request.args.get("search", "")
        with get_db() as db:
            if search:
                rows = db.execute(
                    "SELECT * FROM jobs WHERE " + 
                    search_where +
                    " ORDER BY created_at DESC",
                    [f"%{search}%" for _ in range(3)]
                ).fetchall()
            else:
                rows = db.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/jobs", methods=["POST"])
@token_required
def create_job():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute(
                "INSERT INTO jobs (title, company, location, salary, type, posted) VALUES (?, ?, ?, ?, ?, ?)",
                [data.get(fn, "") for fn in field_names]
            )
            db.commit()
        return jsonify({"message": "Job created successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/jobs/<int:item_id>", methods=["GET"])
@token_required
def get_job(item_id):
    try:
        with get_db() as db:
            row = db.execute("SELECT * FROM jobs WHERE id=?", (item_id,)).fetchone()
        if not row:
            return jsonify({"error": "Job not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/jobs/<int:item_id>", methods=["PUT"])
@token_required
def update_job(item_id):
    try:
        data = request.get_json()
        with get_db() as db:
            db.execute(
                "UPDATE jobs SET title=?, company=?, location=?, salary=?, type=?, posted=?, updated_at=? WHERE id=?",
                [data.get(fn, "") for fn in field_names] + [datetime.now().isoformat(), item_id]
            )
            db.commit()
        return jsonify({"message": "Job updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/jobs/<int:item_id>", methods=["DELETE"])
@token_required
def delete_job(item_id):
    try:
        with get_db() as db:
            db.execute("DELETE FROM jobs WHERE id=?", (item_id,))
            db.commit()
        return jsonify({"message": "Job deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/jobs/search", methods=["GET"])
@token_required  
def search_jobs():
    try:
        q = request.args.get("q", "")
        with get_db() as db:
            rows = db.execute(
                "SELECT * FROM jobs WHERE status LIKE ? ORDER BY created_at DESC LIMIT 50",
                (f"%{q}%",)
            ).fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats", methods=["GET"])
@token_required
def stats():
    try:
        with get_db() as db:
            total = db.execute("SELECT COUNT(*) as count FROM jobs").fetchone()["count"]
            active = db.execute("SELECT COUNT(*) as count FROM jobs WHERE status='active'").fetchone()["count"]
            recent = db.execute("SELECT COUNT(*) as count FROM jobs WHERE date(created_at) = date('now')").fetchone()["count"]
        return jsonify({"total": total, "active": active, "today": recent, "domain": "jobboard", "generation": 3})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
