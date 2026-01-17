#!/usr/bin/env python3
import sys
sys.path.append('RubiksSolver')

import RubiksSolver.solver as sv
import RubiksSolver.move as mv

scramble = "F2 U L2 F2 D2 U' B2 D2 F2 U' B2 D R F2 D U' B' R' D2 U"
print(f"Testing: {scramble}")
print()

# Test depth 5 with full_search=False
print("Test: full_search=False, max_length=5")
result = sv.solve_F2L(scramble, "", False, False, False, False, 5, False, 0, "cross", mv.move_UDLRFB)
print(f"Result: '{result}'")
print(f"Result != scramble: {result != scramble + ' '}")
