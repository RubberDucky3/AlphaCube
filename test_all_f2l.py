#!/usr/bin/env python3
import sys
sys.path.append('RubiksSolver')

import RubiksSolver.solver as sv
import RubiksSolver.move as mv

scramble = "R U R' U'"
print(f"Testing: {scramble}")
print()

# Step 1: Solve cross
print("Step 1: Solving cross...")
current_state = sv.solve_F2L(scramble, "", False, False, False, False, 8, False, 1, "cross", mv.move_UDLRFB)
cross_moves = current_state[len(scramble):].strip() if current_state.startswith(scramble) else "No solution"
print(f"Cross: {cross_moves}")
print(f"State after cross: {current_state}")
print()

# Step 2: Solve BL pair (back left)
print("Step 2: Solving BL pair...")
current_state = sv.solve_F2L(current_state, "", True, False, False, False, 7, False, 1, "F2L_BL", mv.move_UDLRFB)
bl_moves = current_state[len(scramble + " " + cross_moves):].strip() if current_state else "No solution"
print(f"BL pair: {bl_moves}")
print(f"State after BL: {current_state}")
print()

# Step 3: Solve BR pair (back right)
print("Step 3: Solving BR pair...")
current_state = sv.solve_F2L(current_state, "", True, True, False, False, 7, False, 1, "F2L_BR", mv.move_UDLRFB)
br_moves = current_state[len(scramble + " " + cross_moves + " " + bl_moves):].strip() if current_state else "No solution"
print(f"BR pair: {br_moves}")
print(f"State after BR: {current_state}")
print()

# Step 4: Solve FR pair (front right)
print("Step 4: Solving FR pair...")
current_state = sv.solve_F2L(current_state, "", True, True, True, False, 7, False, 1, "F2L_FR", mv.move_UDLRFB)
fr_moves = current_state[len(scramble + " " + cross_moves + " " + bl_moves + " " + br_moves):].strip() if current_state else "No solution"
print(f"FR pair: {fr_moves}")
print(f"State after FR: {current_state}")
print()

# Step 5: Solve FL pair (front left)
print("Step 5: Solving FL pair...")
current_state = sv.solve_F2L(current_state, "", True, True, True, True, 7, False, 1, "F2L_FL", mv.move_UDLRFB)
fl_moves = current_state[len(scramble + " " + cross_moves + " " + bl_moves + " " + br_moves + " " + fr_moves):].strip() if current_state else "No solution"
print(f"FL pair: {fl_moves}")
print(f"State after FL: {current_state}")
print()

print("Summary:")
print(f"Cross: {cross_moves}")
print(f"BL: {bl_moves}")
print(f"BR: {br_moves}")
print(f"FR: {fr_moves}")
print(f"FL: {fl_moves}")
