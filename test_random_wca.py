import sys
import os
import random
import pycuber as pc

# Add the cloned RubiksSolver repository to sys.path
repo_path = os.path.abspath('RubiksSolver')
sys.path.append(repo_path)

# Import solve_cross from RubiksSolver
from RubiksSolver.solver import solve_cross

# Simple random WCA scramble generator (20 moves)
MOVES = ["R", "R'", "R2", "L", "L'", "L2", "U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2"]

def random_wca_scramble(length=20):
    scramble = []
    prev_face = ''
    for _ in range(length):
        move = random.choice([m for m in MOVES if m[0] != prev_face])
        scramble.append(move)
        prev_face = move[0]
    return ' '.join(scramble)

def test_random():
    scramble = random_wca_scramble(20)
    print("Random WCA scramble (20 moves):", scramble)
    # Apply scramble to a pycuber cube (optional verification)
    cube = pc.Cube()
    cube(scramble)
    result = solve_cross(scramble, "", max_length=100, full_search=False, sol_index=0, name="random_test", move_restrict=[])
    print("RubiksSolver cross solution:", result)

if __name__ == "__main__":
    test_random()
