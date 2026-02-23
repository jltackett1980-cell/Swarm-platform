#!/usr/bin/env python3
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, jwt, os

app = Flask(__name__)
CORS(app)
SECRET_KEY = 'swarm-daycare-secret'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'daycare.db')

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
        db.execute('''CREATE TABLE IF NOT EXISTS children (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age REAL,
            parent TEXT,
            phone TEXT,
            allergies TEXT,
            schedule TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.commit()

@app.route('/', methods=['GET'])
def index():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../frontend/index.html')
    return send_file(p)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'app': 'TinyTrack', 'timestamp': datetime.now().isoformat()})

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        hashed = generate_password_hash(data['password'])
        with get_db() as db:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (data['username'], hashed))
            db.commit()
        return jsonify({'message': 'User created'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username=?", (data['username'],)).fetchone()
        if user and check_password_hash(user['password'], data['password']):
            token = jwt.encode({'user': data['username']}, SECRET_KEY, algorithm='HS256')
            return jsonify({'token': token})
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/children', methods=['GET'])
def get_children():
    try:
        with get_db() as db:
            rows = db.execute("SELECT * FROM children ORDER BY created_at DESC").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/children', methods=['POST'])
def create_children():
    try:
        data = request.get_json()
        with get_db() as db:
            cursor = db.execute(
                "INSERT INTO children (name, age, parent, phone, allergies, schedule) VALUES (?, ?, ?, ?, ?, ?)",
                (data.get('name'), data.get('age'), data.get('parent'), data.get('phone'), data.get('allergies'), data.get('schedule'),)
            )
            db.commit()
        return jsonify({'id': cursor.lastrowid, 'message': 'Created'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/children/<int:item_id>', methods=['GET'])
def get_children_item(item_id):
    try:
        with get_db() as db:
            row = db.execute("SELECT * FROM children WHERE id=?", (item_id,)).fetchone()
        if not row:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/children/<int:item_id>', methods=['PUT'])
def update_children(item_id):
    try:
        data = request.get_json()
        sets = ", ".join([f"{k}=?" for k in data.keys()])
        vals = list(data.values()) + [item_id]
        with get_db() as db:
            db.execute(f"UPDATE children SET {sets} WHERE id=?", vals)
            db.commit()
        return jsonify({'message': 'Updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/children/<int:item_id>', methods=['DELETE'])
def delete_children(item_id):
    try:
        with get_db() as db:
            db.execute("DELETE FROM children WHERE id=?", (item_id,))
            db.commit()
        return jsonify({'message': 'Deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/children/search', methods=['GET'])
def search_children():
    try:
        q = request.args.get('q', '')
        with get_db() as db:
            rows = db.execute(
                "SELECT * FROM children WHERE name LIKE ?",
                (f'%{q}%',)
            ).fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    init_db()
    print(f'Starting TinyTrack on http://localhost:5000')
    app.run(debug=False, host='0.0.0.0', port=5000)
