#!/usr/bin/env python3
import re

# Read the file
with open('GOVERNOR.py', 'r') as f:
    content = f.read()

# Find the score_app function and replace it with enhanced version
enhanced_function = '''
def score_app(path, domain_config=None):
    """Enhanced scoring function with human-centric criteria"""
    score = 0
    breakdown = {
        "domain_fields": 0, "routes": 0, "auth": 0,
        "relationships": 0, "validation": 0, "search": 0,
        "api_calls": 0, "ui_fields": 0, "forms": 0,
        "loading_states": 0, "responsive": 0, "notifications": 0,
        "api_versioning": 0, "rate_limiting": 0, "pagination": 0,
        "audit_trail": 0, "error_handling": 0,
        "persona_alignment": 0,
        "pain_resolution": 0,
        "lead_with": 0,
        "one_tap_actions": 0,
        "offline_capability": 0,
        "mobile_ux": 0,
        "no_cruft": 0,
        "tone_alignment": 0
    }
    
    path = Path(path)
    backend = path / "backend" / "app.py"
    html_file = path / "frontend" / "index.html"
    app_js = path / "frontend" / "src" / "App.js"
    manifest_file = path / "frontend" / "manifest.json"
    css_files = list((path / "frontend" / "src").glob("*.css"))
    
    frontend_content = ""
    if html_file.exists():
        frontend_content = html_file.read_text()
    elif app_js.exists():
        frontend_content = app_js.read_text()
    
    domain_name = "unknown"
    if domain_config:
        domain_name = domain_config.get("name", "unknown")
    insight = HUMAN_INSIGHTS.get(domain_name, {})
    
    # ORIGINAL BACKEND SCORING
    if backend.exists():
        try:
            content = backend.read_text()
            
            if domain_config:
                expected = [f[0] for f in domain_config.get("fields", [])]
                reserved = {"name", "details", "status", "id", "created_at"}
                real = [f for f in expected if f not in reserved]
                if real:
                    found = sum(1 for f in real if f in content)
                    breakdown["domain_fields"] = int((found / len(real)) * 60)
            
            routes = len(re.findall(r"@app\.route\(", content))
            breakdown["routes"] = min(routes * 5, 30)
            
            auth = 0
            if "jwt" in content.lower():
                auth += 10
            if "login" in content and "password" in content:
                auth += 10
            breakdown["auth"] = auth
            
            if "JOIN" in content.upper() or "FOREIGN KEY" in content.upper():
                breakdown["relationships"] = 20
            elif content.count("CREATE TABLE") > 2:
                breakdown["relationships"] = 10
            
            if "try:" in content and "except" in content:
                breakdown["validation"] = 5
            if "get_json()" in content and "400" in content:
                breakdown["validation"] = 10
            
            if "LIKE" in content or "search" in content.lower():
                breakdown["search"] = 10
                
        except Exception as e:
            print(f"WARNING: Could not score backend: {e}")
    
    # ORIGINAL FRONTEND SCORING
    if frontend_content:
        try:
            if "fetch(" in frontend_content:
                breakdown["api_calls"] += 10
            if "axios" in frontend_content:
                breakdown["api_calls"] += 10
            
            if domain_config:
                expected = [f[0] for f in domain_config.get("fields", [])]
                found_ui = sum(1 for f in expected if f in frontend_content)
                breakdown["ui_fields"] = int((found_ui / len(expected)) * 15) if expected else 0
            
            if "<form" in frontend_content or "form>" in frontend_content:
                breakdown["forms"] = 10
            
            if "loading" in frontend_content.lower() or "spinner" in frontend_content.lower():
                breakdown["loading_states"] = 10
            
            if "viewport" in frontend_content or "@media" in frontend_content:
                breakdown["responsive"] = 10
            
            if "toast" in frontend_content or "alert" in frontend_content:
                breakdown["notifications"] = 10
            
            if "/api/v1" in frontend_content or "/v1/" in frontend_content:
                breakdown["api_versioning"] = 10
            
            if "X-RateLimit" in frontend_content:
                breakdown["rate_limiting"] = 10
            
            if ".slice" in frontend_content or ".limit" in frontend_content:
                breakdown["pagination"] = 10
            
            if "audit" in frontend_content.lower() or "log" in frontend_content.lower():
                breakdown["audit_trail"] = 10
            
            if "try" in frontend_content and "catch" in frontend_content:
                breakdown["error_handling"] = 10
                
        except Exception as e:
            print(f"WARNING: Could not score frontend: {e}")
    
    # HUMAN-CENTRIC SCORING
    # 1. PERSONA ALIGNMENT (30 pts)
    persona_score = 0
    who = insight.get("who", "").lower()
    
    if "nurse" in who or "coordinator" in who:
        if "patient lookup" in frontend_content.lower() or "search" in frontend_content.lower():
            persona_score += 10
        if "today" in frontend_content.lower() or "appointment" in frontend_content.lower():
            persona_score += 10
        if "quick" in frontend_content.lower() and "onclick=" in frontend_content:
            persona_score += 10
    elif "owner" in who or "cook" in who or "manager" in who:
        if "order" in frontend_content.lower() and "table" in frontend_content.lower():
            persona_score += 10
        if "kitchen" in frontend_content.lower() or "status" in frontend_content.lower():
            persona_score += 10
        if "large" in frontend_content.lower() or "big button" in frontend_content.lower():
            persona_score += 10
    elif "pharmacist" in who:
        if "prescription" in frontend_content.lower() or "rx" in frontend_content.lower():
            persona_score += 10
        if "ready" in frontend_content.lower() and "pending" in frontend_content.lower():
            persona_score += 10
        if "queue" in frontend_content.lower() or "waiting" in frontend_content.lower():
            persona_score += 10
    
    breakdown["persona_alignment"] = min(30, persona_score)
    
    # 2. PAIN RESOLUTION (30 pts)
    pain_score = 0
    pain = insight.get("pain", "").lower()
    
    if "cannot find" in pain or "looking for" in pain:
        if "search" in frontend_content.lower() and "filter" in frontend_content.lower():
            pain_score += 15
        if "recent" in frontend_content.lower() or "history" in frontend_content.lower():
            pain_score += 15
    elif "rush" in pain or "busy" in pain or "behind" in pain:
        if "quick" in frontend_content.lower() and ("click" in frontend_content.lower() or "tap" in frontend_content.lower()):
            pain_score += 15
        if "shortcut" in frontend_content.lower() or "fast" in frontend_content.lower():
            pain_score += 15
    
    breakdown["pain_resolution"] = min(30, pain_score)
    
    # Calculate total
    total = 0
    for key, value in breakdown.items():
        if key != "total":
            total += value
    
    breakdown["total"] = total
    return total, breakdown
'''

# Replace the function
import re
pattern = r'def score_app.*?return.*?\n\n'
fixed_content = re.sub(pattern, enhanced_function, content, flags=re.DOTALL)

with open('GOVERNOR_fixed.py', 'w') as f:
    f.write(fixed_content)

print("✅ Created fixed GOVERNOR.py")
