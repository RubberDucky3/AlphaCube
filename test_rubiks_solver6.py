import sys
import os
# Add the path to the cloned RubiksSolver repository so we can import its modules
repo_path = os.path.abspath('RubiksSolver')
sys.path.append(repo_path)

# Now import the solver module
from RubiksSolver.RubiksSolver import solver as rs

def test_cross():
    scramble = "R' L' U2 D' B U R F B2 U2 B2 R2 U L2 D' F2 U L2 D2 B R2"
    # Solve the white cross using RubiksSolver
    result = rs.solve_cross(scramble, "", max_length=100, full_search=False, sol_index=0, name="test_cross", move_restrict=[])
    print("RubiksSolver cross solution:", result)

if __name__ == "__main__":
    test_cross()
