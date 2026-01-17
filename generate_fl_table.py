#!/usr/bin/env python3
"""
Generate the FL (front-left) F2L pair prune table.
This will create edge6/16/18/20/22_corner21_prune_table
"""
import sys
sys.path.append('RubiksSolver')

import RubiksSolver.solver as sv
import RubiksSolver.move as mv

print("Generating FL pair prune table...")
print("This will take approximately 60-120 seconds...")
print()

# Use a scramble that requires all 4 pairs
scramble = "R U R' U'"

# Solve cross first
current_state = sv.solve_F2L(scramble, "", False, False, False, False, 8, False, 1, "cross", mv.move_UDLRFB)
print(f"Cross solved: {current_state}")

# Solve BL
current_state = sv.solve_F2L(current_state, "", True, False, False, False, 7, False, 1, "F2L_BL", mv.move_UDLRFB)
print(f"BL solved: {current_state}")

# Solve BR
current_state = sv.solve_F2L(current_state, "", True, True, False, False, 7, False, 1, "F2L_BR", mv.move_UDLRFB)
print(f"BR solved: {current_state}")

# Solve FR
current_state = sv.solve_F2L(current_state, "", True, True, True, False, 7, False, 1, "F2L_FR", mv.move_UDLRFB)
print(f"FR solved: {current_state}")

# Solve FL - this will trigger table generation
print()
print("Generating FL prune table (this takes ~60s)...")
current_state = sv.solve_F2L(current_state, "", True, True, True, True, 7, False, 1, "F2L_FL", mv.move_UDLRFB)
print(f"FL solved: {current_state}")

print()
print("FL prune table generated successfully!")
print("Check RubiksSolver/table/ directory for edge6*_corner21_prune_table")
