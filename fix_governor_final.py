#!/usr/bin/env python3
import re

with open('GOVERNOR.py', 'r') as f:
    lines = f.readlines()

# Find the score_app function and replace it
in_score_app = False
new_lines = []
inside_function = False
function_lines = []

for i, line in enumerate(lines):
    if 'def score_app' in line and not in_score_app:
        in_score_app = True
        inside_function = True
        # Add the new function header and start collecting
        new_lines.append(line)
    elif in_score_app and inside_function:
        if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            # End of function reached
            inside_function = False
            in_score_app = False
            # Add our enhanced function body
            new_lines.append('    """Enhanced scoring function with human-centric criteria"""\n')
            new_lines.append('    score = 0\n')
            new_lines.append('    breakdown = {\n')
            new_lines.append('        "domain_fields": 0, "routes": 0, "auth": 0,\n')
            new_lines.append('        "relationships": 0, "validation": 0, "search": 0,\n')
            new_lines.append('        "api_calls": 0, "ui_fields": 0, "forms": 0,\n')
            new_lines.append('        "loading_states": 0, "responsive": 0, "notifications": 0,\n')
            new_lines.append('        "api_versioning": 0, "rate_limiting": 0, "pagination": 0,\n')
            new_lines.append('        "audit_trail": 0, "error_handling": 0,\n')
            new_lines.append('        "persona_alignment": 0,\n')
            new_lines.append('        "pain_resolution": 0,\n')
            new_lines.append('        "lead_with": 0,\n')
            new_lines.append('        "one_tap_actions": 0,\n')
            new_lines.append('        "offline_capability": 0,\n')
            new_lines.append('        "mobile_ux": 0,\n')
            new_lines.append('        "no_cruft": 0,\n')
            new_lines.append('        "tone_alignment": 0\n')
            new_lines.append('    }\n')
            new_lines.append('    \n')
            new_lines.append('    path = Path(path)\n')
            new_lines.append('    backend = path / "backend" / "app.py"\n')
            new_lines.append('    html_file = path / "frontend" / "index.html"\n')
            new_lines.append('    app_js = path / "frontend" / "src" / "App.js"\n')
            new_lines.append('    manifest_file = path / "frontend" / "manifest.json"\n')
            new_lines.append('    css_files = list((path / "frontend" / "src").glob("*.css"))\n')
            new_lines.append('    \n')
            new_lines.append('    frontend_content = ""\n')
            new_lines.append('    if html_file.exists():\n')
            new_lines.append('        frontend_content = html_file.read_text()\n')
            new_lines.append('    elif app_js.exists():\n')
            new_lines.append('        frontend_content = app_js.read_text()\n')
            new_lines.append('    \n')
            new_lines.append('    domain_name = "unknown"\n')
            new_lines.append('    if domain_config:\n')
            new_lines.append('        domain_name = domain_config.get("name", "unknown")\n')
            new_lines.append('    insight = HUMAN_INSIGHTS.get(domain_name, {})\n')
            new_lines.append('    \n')
            new_lines.append('    # [REST OF THE FUNCTION...]\n')
            new_lines.append('    # (I'll add the complete function body if this works)\n')
            new_lines.append('    \n')
            new_lines.append('    return 0, {}\n')
            new_lines.append(line)
        else:
            # Skip old function lines
            pass
    else:
        new_lines.append(line)

with open('GOVERNOR_fixed.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Created fixed version")
