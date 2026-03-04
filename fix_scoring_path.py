#!/usr/bin/env python3
import re

with open('turbo_evolve_600_real.py', 'r') as f:
    content = f.read()

# Fix the scoring calls to use paths, not dicts
old_scoring = '''            human_result = _human.score(app_data, domain, {})
            human_score = human_result.get('human_score', 0)
            
            wisdom_result = _wisdom.score(app_data, domain, {})
            wisdom_score = wisdom_result.get('wisdom_score', 0)'''

new_scoring = '''            # Create a temporary app path for scoring
            # In a real implementation, you'd need to save the app to a file
            # For now, we'll use a mock path
            app_path = f"/tmp/app_{app_data.get('id', 'unknown')}.json"
            
            # Save app data to temp file
            with open(app_path, 'w') as f:
                json.dump(app_data, f)
            
            human_result = _human.score(app_path, domain, {})
            human_score = human_result.get('human_score', 0)
            
            wisdom_result = _wisdom.score(app_path, domain, {})
            wisdom_score = wisdom_result.get('wisdom_score', 0)
            
            # Clean up temp file
            import os
            try:
                os.unlink(app_path)
            except:
                pass'''

content = content.replace(old_scoring, new_scoring)

with open('turbo_evolve_600_fixed.py', 'w') as f:
    f.write(content)

print("✅ Fixed scoring to use file paths instead of dicts")
