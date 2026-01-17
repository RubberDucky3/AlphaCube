import sys
import os
import time

# Structure adjustment for imports
repo_path = os.path.abspath('RubiksSolver')
sys.path.append(repo_path)

import RubiksSolver.solver as sv
import RubiksSolver.move as mv

scramble = "L' D R2 D2 L2 F2 U2 B R2 F2 L2 R2 D U R2 F' D R' D'"
print(f"Testing scramble: {scramble}")

start = time.time()

print("\nSolving Cross (Depth 8)...")
cross_state = sv.solve_F2L(scramble, "z2", False, False, False, False, 8, False, 1, "cross", mv.move_UDLRFB)
print(f"Cross State: {cross_state}")

print("\nSolving F2L #1 (Depth 10)...")
f2l1_state = sv.solve_F2L(cross_state, "", True, False, False, False, 10, False, 1, "F2L#1", mv.move_UDLRFB)
print(f"F2L#1 State: {f2l1_state}")

print("\nSolving F2L #2 (Depth 13)...")
f2l2_state = sv.solve_F2L(f2l1_state, "", True, False, False, True, 13, False, 1, "F2L#2", mv.move_UDLRFB)
print(f"F2L#2 State: {f2l2_state}")

end = time.time()
print(f"\nTotal elapsed: {end - start:.2f}s")
