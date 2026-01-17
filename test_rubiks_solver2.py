import sys
import os
# Ensure the RubiksSolver package is on the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'RubiksSolver'))

# Now import the solver
import RubiksSolver.RubiksSolver.solver as rs

def test_cross():
    scramble = "R' L' U2 D' B U R F B2 U2 B2 R2 U L2 D' F2 U L2 D2 B R2"
    # Use RubiksSolver to solve the white cross from this scramble
    result = rs.solve_cross(scramble, "", max_length=100, full_search=False, sol_index=0, name="test_cross", move_restrict=[])
    print("RubiksSolver cross solution:", result)

if __name__ == "__main__":
    test_cross()
