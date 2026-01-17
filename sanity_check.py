
from src.cube.cube import Cube
from src.cube.constants import MOVE_NAMES

def test_moves():
    c = Cube()
    print(f"Initial Solved: {c.is_solved()}")
    
    # Test all basic faces
    for move in ["U", "D", "L", "R", "F", "B"]:
        c.reset()
        prime = move + "'"
        c.apply_move(move)
        print(f"Applied {move}, Solved? {c.is_solved()}")
        c.apply_move(prime)
        print(f"Applied {prime}, Solved? {c.is_solved()}")
        if not c.is_solved():
            print(f"FAILED: {move} sequence")
            return
            
    # Test rotations
    for rot in ["x", "y", "z"]:
        c.reset()
        prime = rot + "'"
        c.apply_move(rot)
        print(f"Applied {rot}, Solved? {c.is_solved()} (Expect False)")
        c.apply_move(prime)
        print(f"Applied {prime}, Solved? {c.is_solved()} (Expect True)")
        if not c.is_solved():
            print(f"FAILED: Rotation {rot} sequence")
            return
            
    print("ALL BASIC MOVES PASSED SANITY CHECK")

if __name__ == "__main__":
    test_moves()
