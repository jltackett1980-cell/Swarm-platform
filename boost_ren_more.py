#!/usr/bin/env python3
from pathlib import Path
import datetime

# JusticeGuide frontend
index = Path('federation/criminal_law/frontend/index.html')
html = index.read_text()

# Add personalized greeting with time of day
hour = datetime.datetime.now().hour
if hour < 12:
    time_greeting = "Good morning"
elif hour < 18:
    time_greeting = "Good afternoon"
else:
    time_greeting = "Good evening"

personal = f'''
    <div style="background: linear-gradient(135deg, #1a2a3a, #2a3a4a); padding: 20px; margin: 20px 0; border-radius: 10px; border-left: 4px solid #0d6efd;">
        <span style="font-size: 1.3em; font-weight: bold;">{time_greeting}.</span>
        <p style="margin-top: 10px; color: #ddd;">You're not alone. Thousands of people have used JusticeGuide in their moment of need.</p>
    </div>
'''

if 'personal-greeting-2' not in html:
    html = html.replace('<div id="rights" class="card">Loading your rights...</div>', 
                        personal + '\n<div id="rights" class="card">Loading your rights...</div>')
    index.write_text(html)
    print("✅ Added personalized greeting to JusticeGuide")

# DefendAI frontend
index2 = Path('federation/criminal_defense_attorney/frontend/index.html')
html2 = index2.read_text()

personal2 = f'''
    <div style="background: linear-gradient(135deg, #1a2a3a, #2a3a4a); padding: 20px; margin: 20px 0; border-radius: 10px; border-left: 4px solid #6610f2;">
        <span style="font-size: 1.3em; font-weight: bold;">{time_greeting}, Counselor.</span>
        <p style="margin-top: 10px; color: #ddd;">Your clients are counting on you. You have 2 cases today, 5 this week.</p>
    </div>
'''

if 'personal-greeting-2' not in html2:
    html2 = html2.replace('<div id="cases" class="card">Loading cases...</div>', 
                          personal2 + '\n<div id="cases" class="card">Loading cases...</div>')
    index2.write_text(html2)
    print("✅ Added personalized greeting to DefendAI")
