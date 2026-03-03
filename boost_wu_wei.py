#!/usr/bin/env python3
from pathlib import Path

# JusticeGuide frontend
index = Path('federation/criminal_law/frontend/index.html')
html = index.read_text()

# Add one-tap actions and instant feedback
if 'one-tap' not in html:
    new_html = html.replace(
        '<div id="rights" class="card">Loading your rights...</div>',
        '<div id="rights" class="card" onclick="loadRights()">⚡ Tap to load your rights instantly</div>'
    )
    index.write_text(new_html)
    print("✅ Added one-tap to JusticeGuide")

# DefendAI frontend
index2 = Path('federation/criminal_defense_attorney/frontend/index.html')
html2 = index2.read_text()

if 'quick-action' not in html2:
    new_html2 = html2.replace(
        '<div id="cases" class="card">Loading cases...</div>',
        '<div id="cases" class="card" onclick="loadCases()">📋 Click to load active cases</div>'
    )
    index2.write_text(new_html2)
    print("✅ Added one-tap to DefendAI")
