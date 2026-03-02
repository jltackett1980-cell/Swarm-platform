#!/usr/bin/env python3
"""
500-generation focused evolution for criminal justice apps
"""
import subprocess
import time
from datetime import datetime

print("🔥 CRIMINAL JUSTICE EVOLUTION — 500 GENERATIONS")
print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
print("="*60)

for gen in range(1, 501):
    if gen % 10 == 0 or gen == 1:
        print(f"\n📊 GENERATION {gen}/500")
    
    # Run science engine (5 cycles per generation)
    subprocess.run("python3 science_engine.py --cycles 5 > /dev/null 2>&1", shell=True)
    
    # Run device forge (2 cycles per generation)
    subprocess.run("python3 device_forge.py --cycles 2 > /dev/null 2>&1", shell=True)
    
    # Run meta-evolver every 10 generations
    if gen % 10 == 0:
        subprocess.run("python3 meta_evolver.py > /dev/null 2>&1", shell=True)
        
        # Check scores
        cmd = '''
python3 -c "
from human_score_engine import HumanScoreEngine
from wisdom_score_engine import WisdomScoreEngine
from pathlib import Path

human = HumanScoreEngine()
wisdom = WisdomScoreEngine()
apps = [('criminal_law', 'JusticeGuide'), ('criminal_defense_attorney', 'DefendAI')]

for domain, name in apps:
    path = Path(f'federation/{domain}')
    h = human.score(path, domain, {}).get('human_score', 0)
    w = wisdom.score(path, domain, {}).get('wisdom_score', 0)
    total = 275 + h + w
    bar = '█' * (total // 12)
    print(f'  GEN {gen:3} | {name:15} {total}/600 {bar}'
)
"
'''
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
    
    # Brief pause
    time.sleep(1)

print(f"\n✅ COMPLETE at {datetime.now().strftime('%H:%M:%S')}")
