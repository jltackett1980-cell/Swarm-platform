import os, sqlite3, re, csv, io
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, g, Response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-in-production')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'app.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA foreign_keys=ON')
    return db

@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None: db.close()

def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')))''')
    if not db.execute('SELECT id FROM users WHERE email=?', ('demo@app.com',)).fetchone():
        db.execute('INSERT INTO users (email,username,password_hash,role) VALUES (?,?,?,?)',
            ('demo@app.com','Demo Admin',generate_password_hash('demo1234'),'admin'))
    db.commit()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization','').replace('Bearer ','')
        if not token: return jsonify({'error':'Auth required'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            g.user_id = data['user_id']
            g.user_role = data.get('role','user')
        except: return jsonify({'error':'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/health')
def health():
    return jsonify({'status':'healthy','timestamp':datetime.now().isoformat(),'uptime':0})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = (data.get('username') or data.get('email','')).strip().lower()
    pw = data.get('password','')
    if not email or not pw: return jsonify({'error':'Email and password required'}), 400
    user = get_db().execute('SELECT * FROM users WHERE email=? AND active=1', (email,)).fetchone()
    if not user or not check_password_hash(user['password_hash'], pw):
        return jsonify({'error':'Invalid email or password'}), 401
    token = jwt.encode({'user_id':user['id'],'role':user['role']},
        app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token':token,'user':dict(user)})

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email','').strip().lower()
    username = data.get('username','').strip()
    pw = data.get('password','')
    if not email or not username or not pw:
        return jsonify({'error':'All fields required'}), 400
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({'error':'Invalid email'}), 400
    if len(pw) < 8:
        return jsonify({'error':'Password must be 8+ characters'}), 400
    db = get_db()
    if db.execute('SELECT id FROM users WHERE email=?', (email,)).fetchone():
        return jsonify({'error':'Email already registered'}), 409
    cur = db.execute('INSERT INTO users (email,username,password_hash) VALUES (?,?,?)',
        (email, username, generate_password_hash(pw)))
    db.commit()
    return jsonify({'message':'Account created','user_id':cur.lastrowid}), 201

@app.route('/api/auth/me')
@token_required
def me():
    user = get_db().execute(
        'SELECT id,email,username,role,created_at FROM users WHERE id=?',
        (g.user_id,)).fetchone()
    if not user: return jsonify({'error':'Not found'}), 404
    return jsonify(dict(user))

@app.route('/api/users')
@token_required
def get_users():
    users = get_db().execute(
        'SELECT id,email,username,role,active,created_at FROM users ORDER BY created_at DESC'
    ).fetchall()
    return jsonify([dict(u) for u in users])

@app.route('/api/users/<int:uid>', methods=['PUT'])
@token_required
def update_user(uid):
    if g.user_role != 'admin' and g.user_id != uid:
        return jsonify({'error':'Forbidden'}), 403
    data = request.get_json() or {}
    db = get_db()
    if 'username' in data:
        db.execute('UPDATE users SET username=? WHERE id=?', (data['username'], uid))
    if 'role' in data and g.user_role == 'admin':
        db.execute('UPDATE users SET role=? WHERE id=?', (data['role'], uid))
    if 'active' in data and g.user_role == 'admin':
        db.execute('UPDATE users SET active=? WHERE id=?', (1 if data['active'] else 0, uid))
    db.commit()
    return jsonify({'success':True})

@app.route('/api/users/<int:uid>', methods=['DELETE'])
@token_required
def delete_user(uid):
    if g.user_role != 'admin': return jsonify({'error':'Admin only'}), 403
    if uid == g.user_id: return jsonify({'error':'Cannot delete yourself'}), 400
    get_db().execute('UPDATE users SET active=0 WHERE id=?', (uid,))
    get_db().commit()
    return jsonify({'success':True})

@app.route('/api/export/users')
@token_required
def export_users():
    users = get_db().execute(
        'SELECT id,email,username,role,created_at FROM users').fetchall()
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=['id','email','username','role','created_at'])
    w.writeheader()
    w.writerows([dict(u) for u in users])
    return Response(out.getvalue(), mimetype='text/csv',
        headers={'Content-Disposition':'attachment;filename=users.csv'})

if __name__ == '__main__':
    with app.app_context(): init_db()
    print('✅ Server running on http://localhost:5000')
    print('   Demo login: demo@app.com / demo1234')
    app.run(host='0.0.0.0', port=5000, debug=False)
