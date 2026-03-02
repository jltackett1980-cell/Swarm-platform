#!/usr/bin/env python3
"""
Focused evolution for criminal justice apps
"""
import subprocess
import time
from pathlib import Path

print("🔥 EVOLVING CRIMINAL JUSTICE APPS")
print("="*50)

for gen in range(1, 101):
    print(f"\n📊 GENERATION {gen}/100")
    
    # Run science engine focused on criminal justice
    subprocess.run("python3 science_engine.py --cycles 5", shell=True)
    
    # Run device forge to generate related devices
    subprocess.run("python3 device_forge.py --cycles 2", shell=True)
    
    # Run meta-evolver to update rules
    subprocess.run("python3 meta_evolver.py", shell=True)
    
    # Check scores every 10 generations
    if gen % 10 == 0:
        print("\n📈 PROGRESS CHECK:")
        cmd = '''
python3 -c "
from human_score_engine import HumanScoreEngine
from wisdom_score_engine import WisdomScoreEngine
from pathlib import Path

apps = [('criminal_law', 'JusticeGuide'), ('criminal_defense_attorney', 'DefendAI')]
human = HumanScoreEngine()
wisdom = WisdomScoreEngine()

for domain, name in apps:
    path = Path(f'federation/{domain}')
    h = human.score(path, domain, {}).get('human_score', 0)
    w = wisdom.score(path, domain, {}).get('wisdom_score', 0)
    total = 275 + h + w
    bar = '█' * (total // 12)
    print(f'  {name:15} {total}/600 {bar}'
)
"
'''
        subprocess.run(cmd, shell=True)
    
    time.sleep(2)

print("\n✅ CRIMINAL JUSTICE EVOLUTION COMPLETE")
