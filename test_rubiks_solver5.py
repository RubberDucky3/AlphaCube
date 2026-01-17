import sys
import os
# Add the inner RubiksSolver package directory to sys.path
script_dir = os.path.dirname(__file__)
inner_path = os.path.abspath(os.path.join(script_dir, 'RubiksSolver', 'RubiksSolver'))
sys.path.append(inner_path)

# Import the solve_cross function directly
from solver import solve_cross

def test_cross():
    scramble = "R' L' U2 D' B U R F B2 U2 B2 R2 U L2 D' F2 U L2 D2 B R2"
    result = solve_cross(scramble, "", max_length=100, full_search=False, sol_index=0, name="test_cross", move_restrict=[])
    print("RubiksSolver cross solution:", result)

if __name__ == "__main__":
    test_cross()
