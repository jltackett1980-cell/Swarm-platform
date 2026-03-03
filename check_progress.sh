#!/bin/bash
echo "📊 CRIMINAL JUSTICE PROGRESS — $(date)"
echo "========================================"
python3 -c "
from human_score_engine import HumanScoreEngine
from wisdom_score_engine import WisdomScoreEngine
from pathlib import Path

human = HumanScoreEngine()
wisdom = WisdomScoreEngine()

for domain, name in [('criminal_law', 'JusticeGuide'), ('criminal_defense_attorney', 'DefendAI')]:
    path = Path(f'federation/{domain}')
    h = human.score(path, domain, {}).get('human_score', 0)
    w = wisdom.score(path, domain, {}).get('wisdom_score', 0)
    total = 275 + h + w
    w_result = wisdom.score(path, domain, {})
    wu = w_result.get('breakdown', {}).get('wu_wei', {}).get('score', 0)
    re = w_result.get('breakdown', {}).get('ren', {}).get('score', 0)
    du = w_result.get('breakdown', {}).get('dukkha_relief', {}).get('score', 0)
    in_ = w_result.get('breakdown', {}).get('integrity', {}).get('score', 0)
    
    bar = '█' * (total // 12)
    print(f'{name:15} {total:3}/600 {bar}  W:{wu:2} R:{re:2} D:{du:2} I:{in_:2}')
"
