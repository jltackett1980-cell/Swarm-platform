#!/usr/bin/env python3
from pathlib import Path

# JusticeGuide frontend
index = Path('federation/criminal_law/frontend/index.html')
html = index.read_text()

if 'personal-greeting' not in html:
    greeting = '''
    <div style="background: #1a2a3a; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
        <span style="font-size: 1.2em;">⚖️ You matter. Let's get through this together.</span>
    </div>
    '''
    html = html.replace('<h1>⚖️ JusticeGuide</h1>', '<h1>⚖️ JusticeGuide</h1>\n' + greeting)
    index.write_text(html)
    print("✅ Added human greeting to JusticeGuide")

# DefendAI frontend
index2 = Path('federation/criminal_defense_attorney/frontend/index.html')
html2 = index2.read_text()

if 'personal-greeting' not in html2:
    greeting2 = '''
    <div style="background: #1a2a3a; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
        <span style="font-size: 1.2em;">👨‍⚖️ Your clients trust you. We're here to help.</span>
    </div>
    '''
    html2 = html2.replace('<h1>👨‍⚖️ DefendAI</h1>', '<h1>👨‍⚖️ DefendAI</h1>\n' + greeting2)
    index2.write_text(html2)
    print("✅ Added human greeting to DefendAI")
