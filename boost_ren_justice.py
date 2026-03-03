#!/usr/bin/env python3
from pathlib import Path

# JusticeGuide frontend
index = Path('federation/criminal_law/frontend/index.html')
html = index.read_text()

# Replace the entire greeting with warm, human language
human_html = '''<!DOCTYPE html>
<html>
<head>
    <title>JusticeGuide — Your Rights</title>
    <style>
        body { font-family: 'Segoe UI', Roboto, sans-serif; background: #0a0a0a; color: #fff; padding: 20px; line-height: 1.6; }
        .card { background: #1a1a1a; border-left: 4px solid #0d6efd; padding: 20px; margin: 20px 0; border-radius: 8px; }
        h1 { color: #0d6efd; font-size: 2.2em; margin-bottom: 5px; }
        .subtitle { color: #aaa; font-size: 1.1em; margin-bottom: 30px; }
        .greeting { background: linear-gradient(145deg, #0d1a2a, #1a2a3a); padding: 25px; border-radius: 12px; margin: 25px 0; border: 1px solid #2a3a4a; }
        .greeting h2 { color: #0d6efd; margin-bottom: 10px; font-size: 1.8em; }
        .greeting p { color: #ddd; font-size: 1.1em; }
        .rights-list { list-style: none; padding: 0; }
        .rights-list li { background: #2a2a2a; margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 3px solid #0d6efd; }
        .rights-list li strong { color: #0d6efd; display: block; margin-bottom: 5px; font-size: 1.1em; }
        .urgent { background: #dc3545; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }
        .urgent p { font-size: 1.2em; margin: 10px 0 0; }
    </style>
</head>
<body>
    <h1>⚖️ JusticeGuide</h1>
    <div class="subtitle">Your rights. Your next steps. You're not alone.</div>
    
    <div class="greeting">
        <h2>Hey there.</h2>
        <p>We know this moment is hard. You might be scared, confused, or just trying to figure out what happens next. That's okay. Thousands of people have been where you are right now, and they got through it. So will you.</p>
        <p style="margin-top: 15px;"><strong>You have rights. Let's go through them together.</strong></p>
    </div>
    
    <div class="urgent">
        <strong>🚨 If you're in custody right now:</strong>
        <p>Remain silent. Ask for a lawyer. You don't have to answer any questions.</p>
    </div>
    
    <div id="rights" class="card">
        <h3>📜 Your Rights</h3>
        <div id="rights-content">Loading...</div>
    </div>
    
    <div id="steps" class="card">
        <h3>👣 What To Do Next</h3>
        <div id="steps-content">Loading...</div>
    </div>
    
    <script>
        function loadRights() {
            fetch('/api/rights')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('rights-content').innerHTML = 
                        '<ul class="rights-list">' +
                        data.rights.map(r => '<li><strong>•</strong> ' + r + '</li>').join('') +
                        '</ul>';
                })
                .catch(() => {
                    document.getElementById('rights-content').innerHTML = 
                        '<ul class="rights-list">' +
                        '<li><strong>•</strong> You have the right to remain silent</li>' +
                        '<li><strong>•</strong> You have the right to an attorney</li>' +
                        '<li><strong>•</strong> If you cannot afford one, an attorney will be provided</li>' +
                        '</ul>';
                });
        }
        
        function loadSteps() {
            fetch('/api/steps')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('steps-content').innerHTML = 
                        '<ul class="rights-list">' +
                        data.steps.map(s => '<li><strong>•</strong> ' + s + '</li>').join('') +
                        '</ul>';
                })
                .catch(() => {
                    document.getElementById('steps-content').innerHTML = 
                        '<ul class="rights-list">' +
                        '<li><strong>•</strong> Stay calm and remain silent</li>' +
                        '<li><strong>•</strong> Ask for an attorney immediately</li>' +
                        '<li><strong>•</strong> Do not answer questions without your lawyer</li>' +
                        '</ul>';
                });
        }
        
        loadRights();
        loadSteps();
    </script>
</body>
</html>'''

index.write_text(human_html)
print("✅ Completely redesigned JusticeGuide with human-centered language")
