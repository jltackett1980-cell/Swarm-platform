#!/usr/bin/env python3
"""
Self-reflection feedback loop for criminal justice apps
"""
import subprocess
import json
import time
from pathlib import Path

def get_current_scores():
    """Get current scores for both apps"""
    try:
        result = subprocess.run(
            ['python3', 'check_progress.sh'],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except:
        print("⚠️ Could not get scores")

def analyze_wisdom_gaps():
    """Run Python to get wisdom gaps - using simple approach"""
    script = """
from human_score_engine import HumanScoreEngine
from wisdom_score_engine import WisdomScoreEngine
from pathlib import Path
import json

human = HumanScoreEngine()
wisdom = WisdomScoreEngine()
apps = [('criminal_law', 'JusticeGuide'), ('criminal_defense_attorney', 'DefendAI')]

gaps = {}
for domain, name in apps:
    path = Path(f'federation/{domain}')
    w = wisdom.score(path, domain, {})
    breakdown = w.get('breakdown', {})
    
    gaps[name] = {
        'wu_wei': 25 - breakdown.get('wu_wei', {}).get('score', 0),
        'ren': 25 - breakdown.get('ren', {}).get('score', 0),
        'dukkha_relief': 25 - breakdown.get('dukkha_relief', {}).get('score', 0),
        'integrity': 25 - breakdown.get('integrity', {}).get('score', 0)
    }
print(json.dumps(gaps))
"""
    
    try:
        result = subprocess.run(
            ['python3', '-c', script],
            capture_output=True,
            text=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error analyzing gaps: {e}")
        return {}

print("🔄 FEEDBACK LOOP ROUND 2")
print("="*50)

for cycle in range(1, 31):  # 30 cycles for deeper evolution
    print(f"\n📊 CYCLE {cycle}/30 - {time.strftime('%H:%M:%S')}")
    
    # Check current scores
    get_current_scores()
    
    # Analyze gaps
    gaps = analyze_wisdom_gaps()
    if gaps:
        for app, dims in gaps.items():
            print(f"\n{app} gaps:")
            print(f"  wu_wei: +{dims['wu_wei']}/25")
            print(f"  ren: +{dims['ren']}/25")
            print(f"  dukkha_relief: +{dims['dukkha_relief']}/25")
            print(f"  integrity: +{dims['integrity']}/25")
            
            # Target any gap > 5
            for dim, gap in dims.items():
                if gap > 5:
                    print(f"🎯 Targeting {dim} (+{gap})")
                    subprocess.run(
                        f"python3 device_forge.py --cycles 3 --focus {dim} > /dev/null 2>&1",
                        shell=True
                    )
    
    # Run science engine
    subprocess.run("python3 science_engine.py --cycles 2 > /dev/null 2>&1", shell=True)
    
    # Run meta-evolver
    subprocess.run("python3 meta_evolver.py > /dev/null 2>&1", shell=True)
    
    time.sleep(2)

print("\n✅ FEEDBACK LOOP ROUND 2 COMPLETE")
