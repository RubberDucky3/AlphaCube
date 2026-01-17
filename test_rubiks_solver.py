import pycuber as pc
import RubiksSolver.solver as rs

def test_cross():
    cube = pc.Cube()
    scramble = "R' L' U2 D' B U R F B2 U2 B2 R2 U L2 D' F2 U L2 D2 B R2"
    cube(scramble)
    # Use RubiksSolver to solve the white cross from this state.
    # The solve_cross function expects a scramble that leads to the current state.
    result = rs.solve_cross(scramble, "", max_length=100, full_search=False, sol_index=0, name="test_cross", move_restrict=[])
    print("RubiksSolver cross solution:", result)

if __name__ == "__main__":
    test_cross()
