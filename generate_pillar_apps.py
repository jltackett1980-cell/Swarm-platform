#!/usr/bin/env python3
"""
Generate 100 software apps for each of the four pillars
"""
import json
import random
from pathlib import Path

PILLARS = {
    'youth_services': {
        'name': 'FutureKeep',
        'color': '#4ECDC4',
        'problems': ['foster care', 'homeless youth', 'mentorship', 'education', 'job training']
    },
    'elder_services': {
        'name': 'HonorKeep',
        'color': '#A569BD',
        'problems': ['isolation', 'caregiving', 'meal delivery', 'medication', 'companionship']
    },
    'prison_reform': {
        'name': 'SecondChance',
        'color': '#4A2C2C',
        'problems': ['reentry', 'housing', 'employment', 'ID replacement', 'family reconnect']
    },
    'sick_services': {
        'name': 'HealKeep',
        'color': '#E74C3C',
        'problems': ['chronic illness', 'terminal care', 'caregiver support', 'medication', 'hospice']
    },
    'freedom_creation': {
        'name': 'Liberate',
        'color': '#FFD700',
        'problems': ['creative block', 'fear', 'time poverty', 'resource finding', 'community']
    }
}

APP_TYPES = ['finder', 'tracker', 'helper', 'connector', 'guide', 'assistant', 'companion', 'buddy', 'ally', 'support']

print("🔥 GENERATING 100 APPS PER PILLAR")
print("="*60)

total = 0
for pillar, config in PILLARS.items():
    pillar_dir = Path(f'federation/{pillar}_apps')
    pillar_dir.mkdir(exist_ok=True)
    
    print(f"\n📊 {config['name']} — {pillar}")
    
    for i in range(100):
        app_type = random.choice(APP_TYPES)
        problem = random.choice(config['problems'])
        
        app = {
            "domain": f"{pillar}_{app_type}_{i}",
            "name": f"{config['name']} {app_type.title()}",
            "tagline": f"Helping with {problem}",
            "color": config['color'],
            "user": f"person dealing with {problem}",
            "worst_moment": f"struggling with {problem} alone",
            "today_focus": f"What {problem} help do you need today",
            "human_greeting": f"You're not alone. Let's figure out {problem} together.",
            "features": [
                f"{problem}_finder",
                f"{problem}_tracker",
                "offline_first",
                "community_connect",
                "emergency_contact"
            ],
            "pillar": pillar
        }
        
        out = pillar_dir / f"{pillar}_{app_type}_{i:03d}.json"
        out.write_text(json.dumps(app, indent=2))
        total += 1
        
        if i % 10 == 0:
            print(f"  ✅ {i}/100 generated")
    
    print(f"  ✅ Complete — 100 apps for {config['name']}")

print(f"\n🔥 TOTAL: {total} NEW SOFTWARE APPS GENERATED")
