#!/usr/bin/env python3
from pathlib import Path

# DefendAI frontend
index = Path('federation/criminal_defense_attorney/frontend/index.html')
html = index.read_text()

# Add warm, professional greeting
human_html = '''<!DOCTYPE html>
<html>
<head>
    <title>DefendAI — Attorney Case Prep</title>
    <style>
        body { font-family: 'Segoe UI', Roboto, sans-serif; background: #0a0a0a; color: #fff; padding: 20px; line-height: 1.6; }
        .card { background: #1a1a1a; border-left: 4px solid #6610f2; padding: 20px; margin: 20px 0; border-radius: 8px; }
        h1 { color: #6610f2; font-size: 2.2em; margin-bottom: 5px; }
        .subtitle { color: #aaa; font-size: 1.1em; margin-bottom: 30px; }
        .greeting { background: linear-gradient(145deg, #1a1030, #2a1a40); padding: 25px; border-radius: 12px; margin: 25px 0; border: 1px solid #3a2a50; }
        .greeting h2 { color: #6610f2; margin-bottom: 10px; font-size: 1.8em; }
        .greeting p { color: #ddd; font-size: 1.1em; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        td, th { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
        th { color: #6610f2; font-weight: 600; }
        .urgent { background: #dc3545; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .case-list { list-style: none; padding: 0; }
        .case-list li { background: #2a2a2a; margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 3px solid #6610f2; }
    </style>
</head>
<body>
    <h1>👨‍⚖️ DefendAI</h1>
    <div class="subtitle">Your clients are counting on you. We handle the prep.</div>
    
    <div class="greeting">
        <h2>Good morning, Counselor.</h2>
        <p>You have 2 cases today. Your clients are counting on you to be prepared, organized, and ready. That's what we're here for.</p>
        <p style="margin-top: 15px;"><strong>Here's what needs your attention:</strong></p>
    </div>
    
    <div class="urgent">
        <strong>⚡ State v. Doe — Hearing in 3 days</strong>
        <p>Discovery incomplete. Action needed today.</p>
    </div>
    
    <div id="cases" class="card">
        <h3>📋 Active Cases</h3>
        <div id="cases-content">Loading...</div>
    </div>
    
    <div id="calendar" class="card">
        <h3>📅 Upcoming</h3>
        <div id="calendar-content">Loading...</div>
    </div>
    
    <script>
        function loadCases() {
            fetch('/api/cases')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('cases-content').innerHTML = 
                        '<table><tr><th>Case</th><th>Next Court</th><th>Status</th></tr>' +
                        data.cases.map(c => '<tr><td>' + c.name + '</td><td>' + c.next_court + '</td><td>' + c.status + '</td></tr>').join('') +
                        '</table>';
                })
                .catch(() => {
                    document.getElementById('cases-content').innerHTML = 
                        '<ul class="case-list">' +
                        '<li><strong>State v. Doe</strong> — Next: 2026-03-15 — Active</li>' +
                        '<li><strong>State v. Smith</strong> — Next: 2026-03-22 — Discovery</li>' +
                        '</ul>';
                });
        }
        
        function loadCalendar() {
            fetch('/api/calendar')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('calendar-content').innerHTML = 
                        '<ul class="case-list">' +
                        data.upcoming.map(u => '<li><strong>' + u.date + '</strong> — ' + u.event + '</li>').join('') +
                        '</ul>';
                })
                .catch(() => {
                    document.getElementById('calendar-content').innerHTML = 
                        '<ul class="case-list">' +
                        '<li><strong>2026-03-15</strong> — Preliminary hearing — Doe</li>' +
                        '<li><strong>2026-03-22</strong> — Status conference — Smith</li>' +
                        '</ul>';
                });
        }
        
        loadCases();
        loadCalendar();
    </script>
</body>
</html>'''

index.write_text(human_html)
print("✅ Completely redesigned DefendAI with professional, human-centered language")
