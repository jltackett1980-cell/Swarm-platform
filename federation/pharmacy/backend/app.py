import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-me')
app.config['DATABASE'] = 'app.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS users ("
               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
               "email TEXT UNIQUE NOT NULL,"
               "username TEXT UNIQUE NOT NULL,"
               "password_hash TEXT NOT NULL,"
               "role TEXT DEFAULT 'user',"
               "created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
               ")")
    db.commit()
    db.execute("CREATE TABLE IF NOT EXISTS medications ("
               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
               "name TEXT NOT NULL,"
               "details TEXT,"
               "status TEXT DEFAULT 'active',"
               "created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
               ")")
    db.execute("CREATE TABLE IF NOT EXISTS prescriptions ("
               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
               "name TEXT NOT NULL,"
               "details TEXT,"
               "status TEXT DEFAULT 'active',"
               "created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
               ")")
    db.execute("CREATE TABLE IF NOT EXISTS patients ("
               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
               "name TEXT NOT NULL,"
               "details TEXT,"
               "status TEXT DEFAULT 'active',"
               "created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
               ")")
    db.commit()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    db = get_db()
    
    if db.execute('SELECT id FROM users WHERE email = ?', (data['email'],)).fetchone():
        return jsonify({'error': 'Email exists'}), 409
    
    password_hash = generate_password_hash(data['password'])
    cursor = db.execute('INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)',
                       (data['email'], data.get('username', data['email']), password_hash))
    db.commit()
    return jsonify({'message': 'User created', 'user_id': cursor.lastrowid}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db()
    
    user = db.execute('SELECT * FROM users WHERE email = ?', (data['username'],)).fetchone()
    if user and check_password_hash(user['password_hash'], data['password']):
        token = jwt.encode({'user_id': user['id']}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token, 'user': dict(user)})
    return jsonify({'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)


@app.route('/api/medications', methods=['GET'])
def get_medications():
    db = get_db()
    items = db.execute('SELECT * FROM medications').fetchall()
    return jsonify([dict(i) for i in items])

@app.route('/api/medications', methods=['POST'])
def create_medications():
    data = request.get_json()
    db = get_db()
    cursor = db.execute('INSERT INTO medications (name, details) VALUES (?, ?)',
                       (data.get('name'), data.get('details')))
    db.commit()
    return jsonify({'id': cursor.lastrowid, 'message': 'Created'}), 201

@app.route('/api/prescriptions', methods=['GET'])
def get_prescriptions():
    db = get_db()
    items = db.execute('SELECT * FROM prescriptions').fetchall()
    return jsonify([dict(i) for i in items])

@app.route('/api/prescriptions', methods=['POST'])
def create_prescriptions():
    data = request.get_json()
    db = get_db()
    cursor = db.execute('INSERT INTO prescriptions (name, details) VALUES (?, ?)',
                       (data.get('name'), data.get('details')))
    db.commit()
    return jsonify({'id': cursor.lastrowid, 'message': 'Created'}), 201

@app.route('/api/refills', methods=['GET'])
def get_refills():
    db = get_db()
    items = db.execute('SELECT * FROM refills').fetchall()
    return jsonify([dict(i) for i in items])

@app.route('/api/refills', methods=['POST'])
def create_refills():
    data = request.get_json()
    db = get_db()
    cursor = db.execute('INSERT INTO refills (name, details) VALUES (?, ?)',
                       (data.get('name'), data.get('details')))
    db.commit()
    return jsonify({'id': cursor.lastrowid, 'message': 'Created'}), 201
