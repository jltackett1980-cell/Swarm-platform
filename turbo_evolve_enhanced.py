#!/usr/bin/env python3
"""
Enhanced evolution with adaptive parameters and stagnation recovery
"""

import json
import random
import numpy as np
from datetime import datetime
from collections import deque
import signal
import sys
import time
import argparse

class AdaptiveEvolution:
    def __init__(self, initial_mutation_rate=0.5, initial_tournament_size=15):
        self.mutation_rate = initial_mutation_rate
        self.tournament_size = initial_tournament_size
        self.crossover_rate = 0.9
        self.elitism = 10
        
        # Stagnation tracking
        self.stagnation_counter = 0
        self.best_score_so_far = 0
        self.best_genome_so_far = None
        self.score_history = deque(maxlen=100)
        self.generation_best_history = deque(maxlen=50)
        self.diversity_history = deque(maxlen=30)
        
        # Recovery strategies
        self.recovery_attempts = 0
        self.last_recovery_generation = 0
        self.strategy_history = []
        self.recovery_modes = ['hyper_mutation', 'diversity_injection', 'tournament_shrink', 'random_immigrants']
        
        # Checkpointing
        self.checkpoint_interval = 100
        self.last_checkpoint = 0
        
        # Log file
        self.log_file = f"evolution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.evolution_data = []
        
    def update(self, generation, current_best_score, current_best_genome, population_diversity=None):
        """
        Update evolution parameters based on progress
        Returns: (mutation_rate, tournament_size, crossover_rate, action_taken)
        """
        action = "none"
        
        # Track progress
        self.score_history.append(current_best_score)
        self.generation_best_history.append(current_best_score)
        if population_diversity:
            self.diversity_history.append(population_diversity)
        
        # Check for improvement
        if current_best_score > self.best_score_so_far:
            improvement = current_best_score - self.best_score_so_far
            self.best_score_so_far = current_best_score
            self.best_genome_so_far = current_best_genome.copy() if current_best_genome is not None else None
            self.stagnation_counter = 0
            self.recovery_attempts = 0
            
            # Reward improvement with slight parameter adjustment
            if improvement > 5:  # Significant improvement
                self.mutation_rate = max(0.1, self.mutation_rate * 0.95)  # Slightly reduce mutation
                self.tournament_size = min(20, self.tournament_size + 1)  # Slightly increase selection pressure
                action = f"improved_by_{improvement}"
        else:
            self.stagnation_counter += 1
        
        # Calculate progress rate over last 20 generations
        if len(self.generation_best_history) >= 20:
            recent = list(self.generation_best_history)[-20:]
            progress_rate = (recent[-1] - recent[0]) / 20.0 if recent[0] > 0 else 0
            
            # Stagnation detection with multiple levels
            if self.stagnation_counter > 50 and progress_rate < 0.1:
                action = self._apply_recovery_strategy(generation, severity="medium")
            elif self.stagnation_counter > 100 and progress_rate < 0.05:
                action = self._apply_recovery_strategy(generation, severity="high")
            elif self.stagnation_counter > 200:
                action = self._apply_recovery_strategy(generation, severity="extreme")
        
        # Diversity-based adaptation
        if len(self.diversity_history) >= 10:
            avg_diversity = sum(self.diversity_history) / len(self.diversity_history)
            if avg_diversity < 0.1:  # Low diversity
                self.mutation_rate = min(0.9, self.mutation_rate * 1.2)
                action = "diversity_boost"
        
        # Log data
        self._log_generation(generation, current_best_score, action)
        
        # Checkpoint
        if generation - self.last_checkpoint >= self.checkpoint_interval:
            self._save_checkpoint(generation)
            self.last_checkpoint = generation
        
        return self.mutation_rate, self.tournament_size, self.crossover_rate, action

    def _apply_recovery_strategy(self, generation, severity="medium"):
        """Apply different recovery strategies based on severity"""
        self.recovery_attempts += 1
        self.last_recovery_generation = generation
        
        # Cycle through recovery modes
        mode = self.recovery_modes[self.recovery_attempts % len(self.recovery_modes)]
        
        if severity == "medium":
            if mode == "hyper_mutation":
                self.mutation_rate = min(0.8, self.mutation_rate * 1.5)
                self.crossover_rate = 0.7
                action = "recovery_hyper_mutation"
            elif mode == "diversity_injection":
                self.mutation_rate = 0.6
                self.tournament_size = max(5, self.tournament_size - 3)
                action = "recovery_diversity_injection"
            elif mode == "tournament_shrink":
                self.tournament_size = max(3, self.tournament_size - 2)
                action = "recovery_tournament_shrink"
            else:  # random_immigrants
                self.mutation_rate = 0.7
                self.crossover_rate = 0.6
                action = "recovery_random_immigrants"
                
        elif severity == "high":
            self.mutation_rate = 0.8
            self.tournament_size = 5
            self.crossover_rate = 0.5
            action = "recovery_high_perturbation"
            
        else:  # extreme
            self.mutation_rate = 0.9
            self.tournament_size = 3
            self.crossover_rate = 0.3
            self.elitism = 2
            action = "recovery_extreme_reset"
        
        self.strategy_history.append({
            'generation': generation,
            'action': action,
            'mutation_rate': self.mutation_rate,
            'tournament_size': self.tournament_size,
            'crossover_rate': self.crossover_rate,
            'elitism': self.elitism,
            'severity': severity
        })
        
        print(f"🔄 RECOVERY [{severity}]: {action} (μ={self.mutation_rate:.2f}, τ={self.tournament_size})")
        
        return action

    def _log_generation(self, generation, score, action):
        """Log generation data"""
        log_entry = {
            'generation': generation,
            'score': float(score) if score else 0,
            'best_score_so_far': float(self.best_score_so_far),
            'mutation_rate': self.mutation_rate,
            'tournament_size': self.tournament_size,
            'crossover_rate': self.crossover_rate,
            'elitism': self.elitism,
            'stagnation_counter': self.stagnation_counter,
            'recovery_attempts': self.recovery_attempts,
            'action': action,
            'timestamp': datetime.now().isoformat()
        }
        self.evolution_data.append(log_entry)
        
        # Write to file periodically
        if generation % 10 == 0:
            try:
                with open(self.log_file, 'w') as f:
                    json.dump(self.evolution_data, f, indent=2)
            except:
                pass  # Fail silently if write fails

    def _save_checkpoint(self, generation):
        """Save checkpoint"""
        checkpoint = {
            'generation': generation,
            'best_score': self.best_score_so_far,
            'best_genome': self.best_genome_so_far,
            'mutation_rate': self.mutation_rate,
            'tournament_size': self.tournament_size,
            'crossover_rate': self.crossover_rate,
            'elitism': self.elitism,
            'stagnation_counter': self.stagnation_counter,
            'recovery_attempts': self.recovery_attempts,
            'recovery_modes_used': [s['action'] for s in self.strategy_history[-5:]] if self.strategy_history else [],
            'timestamp': datetime.now().isoformat()
        }
        
        checkpoint_file = f'checkpoint_gen_{generation}.json'
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)
            print(f"💾 Checkpoint saved to {checkpoint_file} (best: {self.best_score_so_far:.2f})")
        except Exception as e:
            print(f"⚠️ Checkpoint save failed: {e}")

    def load_checkpoint(self, checkpoint_file):
        """Load from checkpoint"""
        try:
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
            
            self.best_score_so_far = data['best_score']
            self.best_genome_so_far = data['best_genome']
            self.mutation_rate = data['mutation_rate']
            self.tournament_size = data['tournament_size']
            self.crossover_rate = data['crossover_rate']
            self.elitism = data['elitism']
            self.stagnation_counter = data['stagnation_counter']
            self.recovery_attempts = data['recovery_attempts']
            
            print(f"📦 Loaded checkpoint from generation {data['generation']}")
            print(f"   Best score: {self.best_score_so_far}")
            print(f"   Parameters: μ={self.mutation_rate:.2f}, τ={self.tournament_size}, χ={self.crossover_rate:.2f}")
            
            return data['generation']
        except Exception as e:
            print(f"⚠️ Failed to load checkpoint: {e}")
            return 0

    def print_status(self, generation, current_best):
        """Print current status with nice formatting"""
        # Calculate progress
        progress = ""
        if len(self.generation_best_history) >= 20:
            recent = list(self.generation_best_history)[-20:]
            if recent[0] > 0:
                progress_rate = (recent[-1] - recent[0]) / 20.0
                progress = f" | Δ/gen: {progress_rate:+.3f}"
        
        # Diversity info
        diversity = ""
        if self.diversity_history:
            avg_div = sum(self.diversity_history[-10:]) / min(10, len(self.diversity_history))
            diversity = f" | Div: {avg_div:.3f}"
        
        # Recent action
        recent_action = ""
        if self.strategy_history:
            recent_action = f" | Last: {self.strategy_history[-1]['action'][:12]}"
        
        # Recovery count
        recovery_info = f" | Rec: {self.recovery_attempts}"
        
        # Progress bar for stagnation
        stagnation_bar = ""
        if self.stagnation_counter > 0:
            bar_length = min(20, self.stagnation_counter // 5)
            stagnation_bar = f" | Stag: [{'#' * bar_length}{'.' * (20 - bar_length)}]"
        
        status = f"""
╔══════════════════════════════════════════════════════════════════════╗
║  GEN: {generation:6d} | BEST: {current_best:7.2f} | ALL-TIME: {self.best_score_so_far:7.2f}{progress}  ║
║  μ: {self.mutation_rate:.4f} | τ: {self.tournament_size:2d} | χ: {self.crossover_rate:.2f} | ε: {self.elitism:2d}{diversity}  ║
║  STAG: {self.stagnation_counter:4d}{stagnation_bar}{recovery_info}{recent_action}  ║
╚══════════════════════════════════════════════════════════════════════╝
"""
        print(status)


# Enhanced evolution main function
def enhanced_evolution(args):
    """Main evolution loop with adaptive parameters"""
    
    # Initialize adaptive evolution
    adaptive = AdaptiveEvolution(
        initial_mutation_rate=args.mutation_rate,
        initial_tournament_size=args.tournament_size
    )
    
    # Load from checkpoint if specified
    start_generation = 1
    if args.load_checkpoint:
        start_generation = adaptive.load_checkpoint(args.load_checkpoint) + 1
        print(f"▶️ Resuming from generation {start_generation}")
    
    print(f"🚀 Starting ENHANCED evolution with adaptive parameters")
    print(f"   Generations: {args.generations} (starting from {start_generation})")
    print(f"   Population: {args.population}")
    print(f"   Islands: {args.num_islands}")
    print(f"   Target: {args.max_score}")
    print(f"   Log file: {adaptive.log_file}")
    print("")
    
    # Signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Saving final checkpoint before exit...")
        adaptive._save_checkpoint(current_generation)
        print(f"📊 Evolution data saved to {adaptive.log_file}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Main evolution loop
    current_best = adaptive.best_score_so_far
    current_generation = start_generation - 1
    
    # Track best for reporting
    last_print_score = 0
    last_recovery_gen = 0
    
    for generation in range(start_generation, args.generations + 1):
        current_generation = generation
        
        # Simulate evolution progress (REPLACE WITH YOUR ACTUAL EVOLUTION CODE)
        # This is where your genome evaluation and evolution happens
        current_best = simulate_evolution_step(
            generation, 
            adaptive.mutation_rate,
            adaptive.tournament_size,
            adaptive.crossover_rate,
            adaptive.best_score_so_far
        )
        
        # Calculate population diversity (REPLACE WITH ACTUAL DIVERSITY MEASURE)
        # This should measure how genetically diverse your population is
        diversity = random.uniform(0.05, 0.4)  # Placeholder
        
        # Update adaptive parameters
        mutation_rate, tournament_size, crossover_rate, action = adaptive.update(
            generation, 
            current_best, 
            None,  # current_best_genome - replace with actual genome
            diversity
        )
        
        # Print status
        if (generation % args.print_interval == 0 or 
            action != "none" or 
            current_best > last_print_score + 1):
            adaptive.print_status(generation, current_best)
            last_print_score = current_best
        
        # Check if target reached
        if current_best >= args.max_score:
            print(f"\n🎉🎉🎉 TARGET REACHED! Score {current_best:.2f} at generation {generation}")
            adaptive._save_checkpoint(generation)
            break
        
        # Small delay to make output readable (remove for maximum performance)
        if args.slow_mode and generation % 100 == 0:
            time.sleep(0.1)
    
    print(f"\n✅ Evolution complete. Best score: {adaptive.best_score_so_far:.2f}")
    print(f"📊 Evolution log: {adaptive.log_file}")
    
    # Save final checkpoint
    adaptive._save_checkpoint(current_generation)
    
    return adaptive.best_score_so_far


def simulate_evolution_step(generation, mutation_rate, tournament_size, crossover_rate, current_best):
    """
    REPLACE THIS FUNCTION WITH YOUR ACTUAL EVOLUTION LOGIC
    
    This is a placeholder that simulates evolution progress.
    Your actual implementation should:
    1. Evaluate your population
    2. Perform selection, crossover, mutation
    3. Return the best score from this generation
    """
    
    # This is a simulation that shows adaptive parameters working
    # It creates a challenging fitness landscape with plateaus
    
    # Base difficulty - harder to improve as score increases
    base = 275  # Your current champion
    
    # Create plateaus at certain scores to test adaptation
    plateaus = [280, 300, 325, 350, 375, 400, 420]
    
    # Current progress
    if current_best < 280:
        # Easy progress
        improvement_prob = 0.3
        max_improvement = 2
    elif current_best < 300:
        improvement_prob = 0.2
        max_improvement = 1.5
    elif current_best < 350:
        improvement_prob = 0.1
        max_improvement = 1.0
    elif current_best < 400:
        improvement_prob = 0.05
        max_improvement = 0.8
    else:
        improvement_prob = 0.01
        max_improvement = 0.5
    
    # Higher mutation helps escape plateaus
    if any(abs(current_best - p) < 2 for p in plateaus):
        improvement_prob *= (1 + mutation_rate)
        if generation % 100 == 0:
            print(f"🧗 At plateau {min(p for p in plateaus if abs(current_best - p) < 2)} - pushing with μ={mutation_rate:.2f}")
    
    # Determine if we improve
    if random.random() < improvement_prob:
        improvement = random.uniform(0.1, max_improvement)
        new_score = current_best + improvement
    else:
        # Sometimes regress slightly to simulate exploration
        if random.random() < 0.05:  # 5% chance of regression
            new_score = current_best - random.uniform(0, 0.5)
        else:
            new_score = current_best
    
    return max(base, new_score)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Enhanced Evolution with Adaptive Parameters')
    parser.add_argument('--generations', type=int, default=10000, help='Number of generations')
    parser.add_argument('--population', type=int, default=500, help='Population size')
    parser.add_argument('--mutation-rate', type=float, default=0.5, help='Initial mutation rate')
    parser.add_argument('--tournament-size', type=int, default=15, help='Tournament size')
    parser.add_argument('--crossover-rate', type=float, default=0.9, help='Crossover rate')
    parser.add_argument('--num-islands', type=int, default=8, help='Number of islands')
    parser.add_argument('--max-score', type=float, default=430, help='Target score')
    parser.add_argument('--print-interval', type=int, default=10, help='How often to print status')
    parser.add_argument('--load-checkpoint', type=str, help='Load from checkpoint file')
    parser.add_argument('--slow-mode', action='store_true', help='Add delays for readability')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    enhanced_evolution(args)
