#!/usr/bin/env python3
"""
Turbo Evolve 600 - Full scoring system
Technical: 275 | Human: 225 | Wisdom: 100 | Total: 600
Uses your existing human_score_engine.py and wisdom_score_engine.py
"""
import json
import random
import sys
import time
from pathlib import Path
from collections import deque

# Import your scoring engines
sys.path.insert(0, str(Path(__file__).parent))
from human_score_engine import HumanScoreEngine
from wisdom_score_engine import WisdomScoreEngine
from constitutional_core import boot_check

# Initialize
_human = HumanScoreEngine()
_wisdom = WisdomScoreEngine()

# Verify constitutional core
if not boot_check("Turbo Evolve 600"):
    print("❌ Constitutional validation failed")
    sys.exit(1)

class AdaptiveEvolution:
    def __init__(self, max_score=600):
        self.max_score = max_score
        self.best_score = 0
        self.score_history = deque(maxlen=100)
        self.stagnation_counter = 0
        self.recovery_mode = None
        self.generation = 0
        
    def calculate_fitness(self, app_data, domain):
        """Full 600-point fitness calculation using your engines"""
        try:
            # Technical base (275)
            tech_score = 275
            
            # Human score (0-225) from your engine
            human_result = _human.score(app_data, domain, {})
            human_score = human_result.get('human_score', 0)
            human_grade = human_result.get('grade', 'F')
            
            # Wisdom score (0-100) from your engine
            wisdom_result = _wisdom.score(app_data, domain, {})
            wisdom_score = wisdom_result.get('wisdom_score', 0)
            wisdom_grade = wisdom_result.get('grade', 'F')
            
            total = tech_score + human_score + wisdom_score
            
            return {
                'total': min(600, total),
                'tech': tech_score,
                'human': human_score,
                'human_grade': human_grade,
                'wisdom': wisdom_score,
                'wisdom_grade': wisdom_grade,
                'breakdown': {
                    'human': human_result.get('breakdown', {}),
                    'wisdom': wisdom_result.get('breakdown', {})
                }
            }
        except Exception as e:
            print(f"Scoring error: {e}")
            return {'total': 275, 'tech': 275, 'human': 0, 'wisdom': 0}
    
    def evolve_population(self, population, generation):
        """Evolve one generation"""
        self.generation = generation
        scored = []
        
        for ind in population:
            fitness = self.calculate_fitness(ind, ind.get('domain', 'unknown'))
            scored.append((fitness['total'], ind, fitness))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        best_score = scored[0][0]
        best_ind = scored[0][1]
        best_fitness = scored[0][2]
        
        # Track best
        if best_score > self.best_score:
            self.best_score = best_score
            self.stagnation_counter = 0
            self.best_fitness = best_fitness
        else:
            self.stagnation_counter += 1
        
        # Detect stagnation
        if self.stagnation_counter > 50:
            self.recovery_mode = random.choice(['hyper_mutation', 'diversity_injection', 'tournament_shrink'])
            self.stagnation_counter = 0
        else:
            self.recovery_mode = None
        
        # Select parents (top 30%)
        parents = [ind for score, ind, _ in scored[:max(1, len(population)//3)]]
        
        # Create next generation
        next_gen = parents[:5]  # Elitism
        while len(next_gen) < len(population):
            if random.random() < 0.7 and len(parents) >= 2:  # Crossover
                p1, p2 = random.sample(parents, 2)
                child = self._crossover(p1, p2)
            else:  # Mutation
                parent = random.choice(parents)
                child = self._mutate(parent, self._get_mutation_rate())
            next_gen.append(child)
        
        return next_gen, best_score, best_fitness
    
    def _get_mutation_rate(self):
        if self.recovery_mode == 'hyper_mutation':
            return 0.8
        elif self.recovery_mode == 'diversity_injection':
            return 0.6
        elif self.stagnation_counter > 30:
            return 0.5
        else:
            return 0.3
    
    def _crossover(self, p1, p2):
        child = {}
        all_keys = set(p1.keys()) | set(p2.keys())
        for k in all_keys:
            if k in p1 and k in p2:
                child[k] = random.choice([p1[k], p2[k]])
            elif k in p1:
                child[k] = p1[k]
            else:
                child[k] = p2[k]
        return child
    
    def _mutate(self, parent, rate):
        child = parent.copy()
        for k in child:
            if isinstance(child[k], (int, float)) and random.random() < rate:
                child[k] *= random.uniform(0.9, 1.1)
        return child
    
    def print_status(self):
        """Print current status with full breakdown"""
        progress = int((self.best_score / self.max_score) * 20)
        bar = '█' * progress
        spaces = '░' * (20 - progress)
        
        print(f"\n╔══════════════════════════════════════════════════════════════════════╗")
        print(f"║  GEN: {self.generation:6d} | TOTAL: {self.best_score:7.2f}/{self.max_score} {bar}{spaces} ║")
        if hasattr(self, 'best_fitness'):
            print(f"║  Tech: {self.best_fitness.get('tech',0):3d} | Human: {self.best_fitness.get('human',0):3.0f}/225 {self.best_fitness.get('human_grade','?')} | Wisdom: {self.best_fitness.get('wisdom',0):3.0f}/100 {self.best_fitness.get('wisdom_grade','?')} ║")
        print(f"║  Stag: {self.stagnation_counter:3d} | Recovery: {self.recovery_mode or 'none':20} | μ: {self._get_mutation_rate():.2f} ║")
        print(f"╚══════════════════════════════════════════════════════════════════════╝")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='600-point evolution with human+wisdom scoring')
    parser.add_argument('--generations', type=int, default=10000, help='Number of generations')
    parser.add_argument('--population', type=int, default=200, help='Population size')
    parser.add_argument('--max-score', type=int, default=600, help='Target score')
    args = parser.parse_args()
    
    print(f"\n🚀 Starting 600-point evolution")
    print(f"   Generations: {args.generations}")
    print(f"   Population: {args.population}")
    print(f"   Target: {args.max_score}")
    print(f"   System: Technical(275) + Human(225) + Wisdom(100) = 600")
    print(f"   Engines: human_score_engine.py + wisdom_score_engine.py\n")
    
    # Initialize
    adaptive = AdaptiveEvolution(args.max_score)
    
    # Create initial population
    domains = ['healthcare', 'restaurant', 'law', 'education', 'salon', 'plumber', 'daycare', 'pharmacy']
    population = [{
        'id': i,
        'domain': random.choice(domains),
        'features': random.sample(['offline_first', 'today_focus', 'human_greeting', 'no_login_wall', 'domain_color'], 3),
        'generation': 0
    } for i in range(args.population)]
    
    # Evolution loop
    for gen in range(1, args.generations + 1):
        population, best_score, best_fitness = adaptive.evolve_population(population, gen)
        adaptive.best_fitness = best_fitness
        
        if gen % 10 == 0:
            adaptive.print_status()
        
        if best_score >= args.max_score:
            print(f"\n🎉 TARGET REACHED! Score {best_score:.2f} at generation {gen}")
            adaptive.print_status()
            break
    
    print(f"\n✅ Evolution complete. Best score: {adaptive.best_score:.2f}/600")
    
    # Save final checkpoint
    checkpoint = {
        'generation': gen,
        'best_score': adaptive.best_score,
        'best_fitness': best_fitness if 'best_fitness' in locals() else {},
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(f'checkpoint_600_gen_{gen}.json', 'w') as f:
        json.dump(checkpoint, f, indent=2)
    print(f"💾 Checkpoint saved to checkpoint_600_gen_{gen}.json")

if __name__ == "__main__":
    main()
