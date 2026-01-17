import sys
import os
import time

# Structure adjustment for imports
repo_path = os.path.abspath('RubiksSolver')
sys.path.append(repo_path)

import RubiksSolver.solver as sv
import RubiksSolver.move as mv

def extract_moves(new_state, prev_state):
    if not new_state: return "No solution"
    prefix = prev_state.strip()
    full = new_state.strip()
    if full.startswith(prefix):
        return full[len(prefix):].strip()
    return "No solution"

def solve_step(scramble, solved_slots, target_slot, depth):
    flags = [False, False, False, False]
    for s in solved_slots:
        if s == "BL": flags[0] = True
        elif s == "BR": flags[1] = True
        elif s == "FR": flags[2] = True
        elif s == "FL": flags[3] = True
    if target_slot == "BL": flags[0] = True
    elif target_slot == "BR": flags[1] = True
    elif target_slot == "FR": flags[2] = True
    elif target_slot == "FL": flags[3] = True
    return sv.solve_F2L(scramble, "", flags[0], flags[1], flags[2], flags[3], depth, False, 1, f"F2L_{target_slot}", mv.move_UDLRFB)

scramble = "L' D R2 D2 L2 F2 U2 B R2 F2 L2 R2 D U R2 F' D R' D'"
print(f"Testing Scramble: {scramble}")

start_total = time.time()

print("Solving Cross...")
cross_state = sv.solve_F2L(scramble, "z2", False, False, False, False, 8, False, 1, "cross", mv.move_UDLRFB)
current_state = cross_state
unsolved_slots = ["BL", "BR", "FR", "FL"]
solved_slots = []

print("\nStarting Greedy F2L Solve...")

while unsolved_slots:
    found_easy = False
    for slot in unsolved_slots:
        t_start = time.time()
        try_state = solve_step(current_state, solved_slots, slot, 8)
        moves = extract_moves(try_state, current_state)
        t_end = time.time()
        if moves and moves != "No solution" and moves != "":
            print(f"  [EASY] Found solution for {slot} in {t_end - t_start:.2f}s: {moves}")
            current_state = try_state
            solved_slots.append(slot)
            unsolved_slots.remove(slot)
            found_easy = True
            break
    
    if not found_easy and unsolved_slots:
        slot = unsolved_slots[0]
        print(f"  [HARD] No easy pair found. Deep searching for {slot}...")
        t_start = time.time()
        hard_state = solve_step(current_state, solved_slots, slot, 15)
        moves = extract_moves(hard_state, current_state)
        t_end = time.time()
        print(f"  [HARD] Solved {slot} in {t_end - t_start:.2f}s: {moves}")
        current_state = hard_state
        solved_slots.append(slot)
        unsolved_slots.remove(slot)

end_total = time.time()
print(f"\nTotal Greedy F2L elapsed: {end_total - start_total:.2f}s")
print(f"Final Path order: {' -> '.join(solved_slots)}")
