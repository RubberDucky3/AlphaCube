#!/usr/bin/env python3
"""
Pre-generate F2L lookup tables for RubiksSolver.
This takes ~40 seconds but only needs to be done once.
"""
import sys
sys.path.append('RubiksSolver')

import RubiksSolver.solver as sv
import RubiksSolver.move as mv

print("Pre-generating F2L tables (this takes ~40 seconds)...")
print()

# Use a simple scramble to trigger table generation
scramble = "R U R' U'"

# This will create the 5edges_move_table and related prune tables
print("Generating xcross tables (cross + 1 F2L pair)...")
result = sv.solve_F2L(scramble, "", True, False, False, False, 7, False, 1, "test", mv.move_UDLRFB)
print(f"Done! Result: {result}")
print()

print("Tables generated successfully!")
print("Check RubiksSolver/table/ directory for the generated files.")
