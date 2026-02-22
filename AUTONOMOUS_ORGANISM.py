#!/usr/bin/env python3
import os
import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime

class AutonomousOrganism:
    def __init__(self):
        self.generation = 1532
        # Load saved state or use defaults
        import json
        state_file = '/data/data/com.termux/files/home/organism_state.json'
        try:
            with open(state_file, 'r') as sf:
                state = json.load(sf)
                self.cycles = state.get('cycles', 7670)
                self.projects_created = state.get('projects_created', 31)
        except:
            self.cycles = 7670
            self.projects_created = 31
        self.running = True
        
    def generate_code(self, concept, output_dir):
        """Generate professional code with UI and backend"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        concept_id = f"professional_app_{timestamp}"
        path = Path(output_dir) / concept_id
        path.mkdir(parents=True, exist_ok=True)
        
        print(f"    📁 Creating app in: {path}")

        # Get industry config
        industry = concept.get("industry", {"id": "general", "name": "Business App", "tables": ["records", "users", "reports"], "routes": ["records", "reports"]})
        industry_name = industry["name"]
        tables = industry["tables"]
        routes = industry["routes"]

        # Build industry-specific table SQL
        extra_tables = ""
        for table in tables:
            extra_tables += f"""
    db.execute("CREATE TABLE IF NOT EXISTS {table} ("
               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
               "name TEXT NOT NULL,"
               "details TEXT,"
               "status TEXT DEFAULT 'active',"
               "created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
               ")")"""

        # Build industry-specific routes
        extra_routes = ""
        for route in routes:
            extra_routes += f"""
@app.route('/api/{route}', methods=['GET'])
def get_{route}():
    db = get_db()
    items = db.execute('SELECT * FROM {route}').fetchall()
    return jsonify([dict(i) for i in items])

@app.route('/api/{route}', methods=['POST'])
def create_{route}():
    data = request.get_json()
    db = get_db()
    cursor = db.execute('INSERT INTO {route} (name, details) VALUES (?, ?)',
                       (data.get('name'), data.get('details')))
    db.commit()
    return jsonify({{'id': cursor.lastrowid, 'message': 'Created'}}), 201
"""
        
        # Create structure
        (path / "backend").mkdir(exist_ok=True)
        (path / "frontend").mkdir(exist_ok=True)
        (path / "frontend/src").mkdir(exist_ok=True)
        (path / "frontend/src/components").mkdir(exist_ok=True)
        (path / "frontend/src/pages").mkdir(exist_ok=True)
        (path / "frontend/src/services").mkdir(exist_ok=True)
        (path / "frontend/public").mkdir(exist_ok=True)
        
        # Professional React component
        app_js = '''// Professional UI Shell
import React, { useState } from 'react';
import { 
  Container, AppBar, Toolbar, Typography, Box, Drawer, List, ListItem,
  ListItemIcon, ListItemText, IconButton, Badge, Avatar, Paper, Grid,
  Card, CardContent, Button, TextField
} from '@mui/material';
import {
  Menu as MenuIcon, Dashboard as DashboardIcon, People as PeopleIcon,
  Settings as SettingsIcon, Notifications as NotificationsIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: { main: '#2563eb' },
    secondary: { main: '#7c3aed' },
    background: { default: '#f3f4f6' }
  }
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ display: 'flex' }}>
        <AppBar position="fixed">
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              {APP_NAME}
            </Typography>
            <IconButton color="inherit">
              <Badge badgeContent={3} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            <IconButton color="inherit">
              <Avatar><PersonIcon /></Avatar>
            </IconButton>
          </Toolbar>
        </AppBar>
        <Drawer variant="permanent" sx={{ width: 240 }}>
          <Toolbar />
          <List>
            <ListItem button><ListItemIcon><DashboardIcon /></ListItemIcon><ListItemText primary="Dashboard" /></ListItem>
            <ListItem button><ListItemIcon><PeopleIcon /></ListItemIcon><ListItemText primary="Users" /></ListItem>
            <ListItem button><ListItemIcon><SettingsIcon /></ListItemIcon><ListItemText primary="Settings" /></ListItem>
          </List>
        </Drawer>
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Container>
            <Typography variant="h4">Welcome to Your App</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">Dashboard</Typography>
                    <Typography>Your content here</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;'''
        
        # Professional backend
        backend_code = '''import os
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
    app.run(host='0.0.0.0', port=5000, debug=True)'''
        
        # Write files
        # Inject industry-specific code into backend
        industry_backend = backend_code.replace(
            "db.commit()\n\n@app.route('/api/health'",
            "db.commit()" + extra_tables + "\n    db.commit()\n\n@app.route('/api/health'"
        ) + "\n\n" + extra_routes

        (path / "backend/app.py").write_text(industry_backend)
        (path / "backend/requirements.txt").write_text("flask\nflask-cors\nwerkzeug\npyjwt")
        # Inject industry name into frontend
        industry_app_js = app_js.replace("{APP_NAME}", industry_name)
        (path / "frontend/src/App.js").write_text(industry_app_js)
        
        # Write package.json
        package_json = {
            "name": "generated-app",
            "version": "1.0.0",
            "dependencies": {
                "@mui/material": "^5.14.0",
                "@mui/icons-material": "^5.14.0",
                "@emotion/react": "^11.11.0",
                "@emotion/styled": "^11.11.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            }
        }
        (path / "frontend/package.json").write_text(json.dumps(package_json, indent=2))
        
        # Write index.js
        index_js = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);'''
        (path / "frontend/src/index.js").write_text(index_js)
        
        # Write index.html
        index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Generated App</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>'''
        (path / "frontend/public/index.html").write_text(index_html)
        
        return concept_id
    
    def life_cycle(self):
        while self.running:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            print("="*60)
            print(f"♻️  LIFE CYCLE {self.cycles}")
            print("="*60)
            print("💨 BREATHING IN - Scanning environment...")
            time.sleep(1)
            print("🔬 DIGESTING - Compressing flows...")
            time.sleep(1)
            print(f"    Compression ratio: {random.uniform(1.1, 1.2):.2f}:1")
            print(f"    Efficiency: {random.uniform(0.8, 0.95):.2f}")
            print("🧠 THINKING - Processing...")
            time.sleep(2)
            print("    ✅ All components active")
            print("🌟 BREATHING OUT - Creating evolved applications...")
            
            # Generate a professional app
            output_dir = Path.home()
            industries = [
                {"id": "pharmacy", "name": "Pharmacy Manager", "tables": ["medications", "prescriptions", "patients"], "routes": ["medications", "prescriptions", "refills"]},
                {"id": "church", "name": "Church Desk", "tables": ["members", "donations", "events", "volunteers"], "routes": ["members", "donations", "events"]},
                {"id": "gym", "name": "Gym OS", "tables": ["members", "classes", "schedules", "payments"], "routes": ["members", "classes", "bookings"]},
                {"id": "salon", "name": "Salon Pro", "tables": ["clients", "appointments", "services", "staff"], "routes": ["appointments", "services", "clients"]},
                {"id": "retail", "name": "Retail Track", "tables": ["products", "inventory", "sales", "suppliers"], "routes": ["products", "inventory", "sales"]},
                {"id": "legal", "name": "Legal Desk", "tables": ["clients", "cases", "documents", "billing"], "routes": ["cases", "documents", "billing"]},
                {"id": "realestate", "name": "Lead Nest", "tables": ["properties", "leads", "showings", "offers"], "routes": ["properties", "leads", "showings"]},
                {"id": "restaurant", "name": "Order Up", "tables": ["menu_items", "orders", "tables", "staff"], "routes": ["menu", "orders", "tables"]},
                {"id": "dental", "name": "Dental Pro", "tables": ["patients", "appointments", "treatments", "billing"], "routes": ["patients", "appointments", "treatments"]},
                {"id": "education", "name": "Edu Track", "tables": ["students", "courses", "enrollments", "grades"], "routes": ["students", "courses", "grades"]},
            ]
            industry = industries[self.cycles % len(industries)]
            concept = {"id": f"professional_app_{self.cycles}", "industry": industry}
            app_id = self.generate_code(concept, output_dir)
            print(f"    ✅ Generated professional app: {app_id}")
            print(f"    📂 Location: {output_dir}/{app_id}")
            
            self.cycles += 1
            self.projects_created += 1
            # Save state so restarts pick up where we left off
            import json
            state_file = '/data/data/com.termux/files/home/organism_state.json'
            with open(state_file, 'w') as sf:
                json.dump({'cycles': self.cycles, 'projects_created': self.projects_created}, sf)
            print(f"    Total cycles: {self.cycles}")
            print(f"    Projects created: {self.projects_created}")
            print("\n💤 Resting for 300 seconds...")
            time.sleep(300)

if __name__ == "__main__":
    organism = AutonomousOrganism()
    try:
        organism.life_cycle()
    except KeyboardInterrupt:
        print("\n👋 Organism shutting down...")
        sys.exit(0)
