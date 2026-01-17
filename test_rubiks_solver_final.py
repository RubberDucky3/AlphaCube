import sys
import os
# Add the cloned RubiksSolver repository to sys.path (the outer folder)
repo_path = os.path.abspath('RubiksSolver')
sys.path.append(repo_path)

# Import solve_cross from the inner package
from RubiksSolver.solver import solve_cross

def test_cross():
    scramble = "R' L' U2 D' B U R F B2 U2 B2 R2 U L2 D' F2 U L2 D2 B R2"
    result = solve_cross(scramble, "", max_length=100, full_search=False, sol_index=0, name="test_cross", move_restrict=[])
    print("RubiksSolver cross solution:", result)

if __name__ == "__main__":
    test_cross()
