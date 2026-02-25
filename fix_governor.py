#!/usr/bin/env python3
import re

# Read the file
with open('GOVERNOR.py', 'r') as f:
    content = f.read()

# Find the problematic pattern and fix it
# Look for: html_file.exists():...elif app_js.exists():
pattern = r'(if html_file\.exists\(\):.*?\n)(.*?)(elif app_js\.exists\(\):.*?\n)'
replacement = r'\1\2    elif app_js.exists():\n        frontend_content = app_js.read_text()\n'
fixed_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('GOVERNOR.py', 'w') as f:
    f.write(fixed_content)

print("✅ Fixed GOVERNOR.py")
