#!/bin/bash
# Swarm Platform Installer
# One command setup for any small business

SWARM_DIR="/data/data/com.termux/files/home/swarm-platform"
CONFIGS="$HOME/organism_templates/domain_configs.json"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   SWARM PLATFORM INSTALLER           ║"
echo "║   Built for small business           ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check dependencies
echo "Checking dependencies..."
pip install flask flask-cors werkzeug pyjwt --quiet --break-system-packages 2>/dev/null
echo "✅ Dependencies ready"
echo ""

# Show available industries
echo "What type of business are you setting up?"
echo ""

# Read domains from config
python3 -c "
import json, sys
configs = json.loads(open('$CONFIGS').read())
domains = list(configs.items())
for i, (k, v) in enumerate(domains):
    print(f'  {i+1:2}. {v[\"icon\"]} {v[\"name\"]}')
" 2>/dev/null

echo ""
read -p "Enter number: " CHOICE
echo ""

# Get selected domain
DOMAIN=$(python3 -c "
import json
configs = json.loads(open('$CONFIGS').read())
domains = list(configs.items())
idx = int('$CHOICE') - 1
if 0 <= idx < len(domains):
    k, v = domains[idx]
    print(k)
" 2>/dev/null)

APP_NAME=$(python3 -c "
import json
configs = json.loads(open('$CONFIGS').read())
domains = list(configs.items())
idx = int('$CHOICE') - 1
if 0 <= idx < len(domains):
    k, v = domains[idx]
    print(v['name'])
" 2>/dev/null)

if [ -z "$DOMAIN" ]; then
    echo "Invalid choice. Run install.sh again."
    exit 1
fi

echo "Setting up $APP_NAME..."
echo ""

# Find the champion for this domain
CHAMPION_DIR="$HOME/ORGANISM_ARMY/champions/$DOMAIN"

if [ ! -d "$CHAMPION_DIR/backend" ]; then
    echo "No champion yet for $APP_NAME — generating one now..."
    python3 -c "
import sys, json
sys.path.insert(0, '$SWARM_DIR')
from AUTONOMOUS_ORGANISM import build_backend, build_frontend, load_configs
from pathlib import Path
import os

configs = load_configs()
cfg = configs.get('$DOMAIN')
if not cfg:
    print('Domain not found')
    sys.exit(1)

out = Path('$CHAMPION_DIR')
(out / 'backend').mkdir(parents=True, exist_ok=True)
(out / 'frontend' / 'src').mkdir(parents=True, exist_ok=True)
(out / 'frontend' / 'public').mkdir(parents=True, exist_ok=True)

(out / 'backend' / 'app.py').write_text(build_backend('$DOMAIN', cfg))
(out / 'backend' / 'requirements.txt').write_text('flask\nflask-cors\nwerkzeug\npyjwt\n')
(out / 'frontend' / 'src' / 'App.js').write_text(build_frontend(cfg))
(out / 'frontend' / 'src' / 'index.js').write_text(
    \"import React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport App from './App';\n\"
    \"const root = ReactDOM.createRoot(document.getElementById('root'));\n\"
    \"root.render(<React.StrictMode><App /></React.StrictMode>);\n\"
)
(out / 'frontend' / 'public' / 'index.html').write_text(
    '<!DOCTYPE html><html><head><meta charset=\"utf-8\"/><title>' + cfg['name'] + '</title></head>'
    '<body><div id=\"root\"></div></body></html>'
)
print('Generated')
"
fi

# Install to a clean app directory
APP_DIR="$HOME/${DOMAIN}_app"
mkdir -p "$APP_DIR"
cp -r "$CHAMPION_DIR/backend" "$APP_DIR/"
cp -r "$CHAMPION_DIR/frontend" "$APP_DIR/"

echo "✅ $APP_NAME installed to $APP_DIR"
echo ""

# Start the backend
cd "$APP_DIR/backend"
python3 -c "
import sqlite3, sys
sys.path.insert(0, '.')
" 2>/dev/null

echo "Starting $APP_NAME backend..."
python3 -u "$APP_DIR/backend/app.py" > "$HOME/${DOMAIN}.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$HOME/${DOMAIN}.pid"
sleep 2

# Check it started
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend running on http://localhost:5000"
else
    echo "❌ Backend failed to start — check $HOME/${DOMAIN}.log"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   $APP_NAME is ready!         "
echo "║                                      ║"
echo "║   API:  http://localhost:5000        ║"
echo "║   Health: http://localhost:5000/api/health"
echo "║                                      ║"
echo "║   To stop: kill \$(cat ~/${DOMAIN}.pid)"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Test it now:"
echo "  curl http://localhost:5000/api/health"
echo ""
