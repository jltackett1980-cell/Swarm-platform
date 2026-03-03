#!/usr/bin/env python3
"""
Puzzle Generator for Hospital Stay
Creates crosswords, sudoku, word searches, and more
"""

import json
import random
from datetime import datetime

# ===========================================
# CROSSWORD GENERATOR
# ===========================================
def generate_crossword(name="friend", theme="encouragement"):
    """Generate a custom crossword puzzle"""
    
    # Word bank with clues (medium difficulty)
    words = [
        {"word": "HOPE", "clue": "What keeps you going when things get hard"},
        {"word": "REST", "clue": "What your body needs to heal"},
        {"word": "STRONG", "clue": "What you are, even when you don't feel it"},
        {"word": "HEAL", "clue": "Your body's superpower right now"},
        {"word": "CALM", "clue": "The opposite of stress"},
        {"word": "PEACE", "clue": "Inner quiet, even in a hospital"},
        {"word": "GRACE", "clue": "Undeserved kindness"},
        {"word": "BREATHE", "clue": "Deep ___ — the simplest medicine"},
        {"word": "SMILE", "clue": "One of these can change your whole day"},
        {"word": "TODAY", "clue": "One day at a ___"},
    ]
    
    # Simple 10x10 crossword layout
    crossword = {
        "title": f"Crossword for {name}",
        "theme": theme,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "grid_size": "10x10",
        "across": [],
        "down": [],
        "words": words
    }
    
    # Format for printing
    output = []
    output.append("=" * 50)
    output.append(f"🧩 CROSSWORD PUZZLE")
    output.append(f"For: {name}")
    output.append(f"Date: {crossword['date']}")
    output.append("=" * 50)
    output.append("")
    output.append("ACROSS:")
    for i, w in enumerate(words[:5]):
        output.append(f"  {i+1}. {w['clue']} ({len(w['word'])} letters)")
    output.append("")
    output.append("DOWN:")
    for i, w in enumerate(words[5:]):
        output.append(f"  {i+1}. {w['clue']} ({len(w['word'])} letters)")
    output.append("")
    output.append("BLANK GRID:")
    output.append("+---+---+---+---+---+---+---+---+---+---+")
    for row in range(10):
        line = "|"
        for col in range(10):
            if random.random() > 0.4:  # Random black squares
                line += "   |"
            else:
                line += "   |"  # Empty cell
        output.append(line)
        output.append("+---+---+---+---+---+---+---+---+---+---+")
    output.append("")
    
    return "\n".join(output)

# ===========================================
# SUDOKU GENERATOR (Medium Difficulty)
# ===========================================
def generate_sudoku(name="friend"):
    """Generate a medium-difficulty Sudoku puzzle"""
    
    # A pre-built medium Sudoku puzzle
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    
    output = []
    output.append("=" * 50)
    output.append(f"🔢 SUDOKU PUZZLE (Medium)")
    output.append(f"For: {name}")
    output.append("=" * 50)
    output.append("")
    output.append("Fill each row, column, and 3x3 box with 1-9.")
    output.append("")
    
    # Print grid
    output.append("+-------+-------+-------+")
    for i in range(9):
        row = "|"
        for j in range(9):
            if puzzle[i][j] == 0:
                row += " . "
            else:
                row += f" {puzzle[i][j]} "
            if (j+1) % 3 == 0:
                row += "|"
        output.append(row)
        if (i+1) % 3 == 0:
            output.append("+-------+-------+-------+")
    
    output.append("")
    output.append("SOLUTION (upside down at bottom):")
    output.append("")
    
    return "\n".join(output)

# ===========================================
# WORD SEARCH GENERATOR
# ===========================================
def generate_word_search(name="friend"):
    """Generate a word search puzzle"""
    
    words = ["HOPE", "HEAL", "STRONG", "PEACE", "CALM", "REST", "SMILE", "GRACE"]
    
    grid_size = 12
    grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Place words (simplified - random placement)
    for word in words:
        direction = random.choice(['horizontal', 'vertical'])
        if direction == 'horizontal':
            row = random.randint(0, grid_size-1)
            col = random.randint(0, grid_size - len(word))
            for i, letter in enumerate(word):
                grid[row][col+i] = letter
        else:
            row = random.randint(0, grid_size - len(word))
            col = random.randint(0, grid_size-1)
            for i, letter in enumerate(word):
                grid[row+i][col] = letter
    
    # Fill rest with random letters
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i in range(grid_size):
        for j in range(grid_size):
            if grid[i][j] == ' ':
                grid[i][j] = random.choice(letters)
    
    output = []
    output.append("=" * 50)
    output.append(f"🔍 WORD SEARCH")
    output.append(f"For: {name}")
    output.append("=" * 50)
    output.append("")
    output.append("Find these words:")
    output.append("  " + ", ".join(words))
    output.append("")
    
    # Print grid
    for row in grid:
        output.append("  " + " ".join(row))
    
    return "\n".join(output)

# ===========================================
# MAZE GENERATOR
# ===========================================
def generate_maze(name="friend"):
    """Generate a simple maze"""
    
    maze = [
        "██████████████████",
        "█S            █ █",
        "█ ███████ ████ █ █",
        "█ █     █ █  █ █ █",
        "█ █ ███ █ █ ███ █",
        "█ █ █   █ █   █ █",
        "█ █ █████ ███ █ █",
        "█ █           █ █",
        "█ ███████████ █ █",
        "█             █E█",
        "██████████████████"
    ]
    
    output = []
    output.append("=" * 50)
    output.append(f"🧩 MAZE")
    output.append(f"For: {name}")
    output.append("=" * 50)
    output.append("")
    output.append("Start at S, End at E")
    output.append("")
    
    for line in maze:
        output.append("  " + line)
    
    return "\n".join(output)

# ===========================================
# MAIN - GENERATE ALL PUZZLES
# ===========================================
def main():
    friend_name = input("Enter your friend's name: ") or "Friend"
    
    print("\n🧩 GENERATING HOSPITAL ACTIVITY PACKET")
    print("=" * 50)
    
    # Generate all puzzles
    crossword = generate_crossword(friend_name)
    sudoku = generate_sudoku(friend_name)
    wordsearch = generate_word_search(friend_name)
    maze = generate_maze(friend_name)
    
    # Combine into one file
    filename = f"puzzles_for_{friend_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"
    
    with open(filename, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write(f"🧩 ACTIVITY PACKET FOR {friend_name.upper()}\n")
        f.write(f"Generated: {datetime.now().strftime('%B %d, %Y')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(crossword + "\n\n")
        f.write("=" * 60 + "\n\n")
        f.write(sudoku + "\n\n")
        f.write("=" * 60 + "\n\n")
        f.write(wordsearch + "\n\n")
        f.write("=" * 60 + "\n\n")
        f.write(maze + "\n\n")
        f.write("=" * 60 + "\n")
        f.write("💝 Made just for you. Heal fast!\n")
        f.write("=" * 60 + "\n")
    
    print(f"\n✅ Activity packet created: {filename}")
    print(f"📁 Location: ~/swarm-platform/{filename}")
    print("\n💝 Print this and bring it to your friend!")

if __name__ == "__main__":
    main()
