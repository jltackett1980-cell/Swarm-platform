#!/usr/bin/env python3
from pathlib import Path

# JusticeGuide frontend
index = Path('federation/criminal_law/frontend/index.html')
html = index.read_text()

# Add offline detection and cached rights
if 'offline' not in html:
    offline_script = '''
    <script>
    // Offline-first rights
    const cachedRights = [
        "You have the right to remain silent",
        "You have the right to an attorney",
        "If you cannot afford an attorney, one will be provided"
    ];
    
    window.addEventListener('offline', function() {
        document.getElementById('rights').innerHTML = 
            '<h3>📱 OFFLINE MODE</h3><ul>' +
            cachedRights.map(r => '<li>' + r + '</li>').join('') +
            '</ul><p><em>Your rights are always with you</em></p>';
    });
    </script>
    '''
    html = html.replace('</body>', offline_script + '\n</body>')
    index.write_text(html)
    print("✅ Added offline resilience to JusticeGuide")

# DefendAI frontend
index2 = Path('federation/criminal_defense_attorney/frontend/index.html')
html2 = index2.read_text()

if 'offline' not in html2:
    offline_script2 = '''
    <script>
    // Cached cases for offline
    const cachedCases = [
        {"name": "State v. Doe", "next_court": "2026-03-15", "status": "Active"},
        {"name": "State v. Smith", "next_court": "2026-03-22", "status": "Discovery"}
    ];
    
    window.addEventListener('offline', function() {
        document.getElementById('cases').innerHTML = 
            '<h3>📱 OFFLINE MODE</h3><table><tr><th>Case</th><th>Next Court</th><th>Status</th></tr>' +
            cachedCases.map(c => '<tr><td>' + c.name + '</td><td>' + c.next_court + '</td><td>' + c.status + '</td></tr>').join('') +
            '</table>';
    });
    </script>
    '''
    html2 = html2.replace('</body>', offline_script2 + '\n</body>')
    index2.write_text(html2)
    print("✅ Added offline resilience to DefendAI")
