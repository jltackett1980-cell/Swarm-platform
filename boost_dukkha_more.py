#!/usr/bin/env python3
from pathlib import Path

# JusticeGuide frontend
index = Path('federation/criminal_law/frontend/index.html')
html = index.read_text()

# Add immediate relief banner
relief = '''
    <div style="background: #dc3545; color: white; padding: 15px; margin: 20px 0; border-radius: 5px; text-align: center;">
        <strong>🚨 IF YOU'RE IN CUSTODY RIGHT NOW:</strong> 
        <p style="margin-top: 10px;">Remain silent. Ask for a lawyer. These rights download instantly — even without internet.</p>
    </div>
'''

if 'relief-banner' not in html:
    html = html.replace('<div id="rights" class="card">', relief + '\n<div id="rights" class="card">')
    index.write_text(html)
    print("✅ Added relief banner to JusticeGuide")

# DefendAI frontend
index2 = Path('federation/criminal_defense_attorney/frontend/index.html')
html2 = index2.read_text()

relief2 = '''
    <div style="background: #dc3545; color: white; padding: 15px; margin: 20px 0; border-radius: 5px;">
        <strong>⚡ URGENT: State v. Doe hearing in 3 days</strong>
        <p>Discovery incomplete. Action needed today.</p>
    </div>
'''

if 'relief-banner' not in html2:
    html2 = html2.replace('<div id="cases" class="card">', relief2 + '\n<div id="cases" class="card">')
    index2.write_text(html2)
    print("✅ Added urgency to DefendAI")
