#!/usr/bin/env python3
import sys
sys.path.append('RubiksSolver')

import RubiksSolver.solver as sv
import RubiksSolver.move as mv

# Test with example scramble from cross.py (EXACT same code)
scramble = "F2 U L2 F2 D2 U' B2 D2 F2 U' B2 D R F2 D U' B' R' D2 U"
print(f"Testing scramble: {scramble}")
print()

# Use EXACT settings from cross.py example
print("Testing with exact settings from cross.py example...")
scramble = sv.solve_F2L(scramble, "", False, False, False, False, 5, True, 1, "cross", mv.move_UDLRFB)
print(f"Result: {scramble}")
