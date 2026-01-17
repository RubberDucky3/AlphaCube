import sys
import os
from flask import Flask, request, render_template, jsonify

# Ensure the RubiksSolver repository is on sys.path
# Based on the structure: /Users/jeromefrancis/Desktop/AlphaCube/RubiksSolver
# The library uses absolute imports like 'import RubiksSolver.search'
repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'RubiksSolver'))
sys.path.append(repo_path)

# Import solver using the exact absolute names the library expects
import RubiksSolver.solver as sv
import RubiksSolver.move as mv

# --- Table Caching (Monkey-Patching) ---
import RubiksSolver.create_table as ct
_TABLE_CACHE = {}

def get_cached_table(func, *args):
    # Convert unhashable types (like array.array or list) to hashable IDs
    # Since these tables are constants in this context, id() is safe.
    safe_args = []
    for a in args:
        if isinstance(a, (str, int, float, bool, type(None))):
            safe_args.append(a)
        else:
            # Use type name and id for unhashable objects
            safe_args.append(f"{type(a).__name__}_{id(a)}")
    
    key = (func.__name__, tuple(safe_args))
    if key not in _TABLE_CACHE:
        print(f"[CACHE] Loading table for {func.__name__} {safe_args}...")
        _TABLE_CACHE[key] = func(*args)
    return _TABLE_CACHE[key]

# Wrap all heavy table loaders
original_edge = ct.create_edge_move_table
ct.create_edge_move_table = lambda: get_cached_table(original_edge)

original_corner = ct.create_corner_move_table
ct.create_corner_move_table = lambda: get_cached_table(original_corner)

original_multi2 = ct.create_multi_move_table2
ct.create_multi_move_table2 = lambda *args: get_cached_table(original_multi2, *args)

original_prune2 = ct.create_prune_table2
ct.create_prune_table2 = lambda *args: get_cached_table(original_prune2, *args)

original_ma = ct.create_ma_table
ct.create_ma_table = lambda: get_cached_table(original_ma)
# ----------------------------------------

import subprocess
import os

# --- High-Performance C++ Solver Integration ---
CPP_SOLVER_PATH = os.path.join(os.path.dirname(__file__), "RubiksSolverCpp", "solver_bridge")

# --- Move Transformation for Rotations ---
def transform_moves(moves_str, rotation):
    if not rotation or rotation == "":
        return moves_str
    
    # Mapping: Which BASE face occupies the position targeted by the SOLVER?
    # y (CW): Front is Base R, Right is Base B, Back is Base L, Left is Base F
    if rotation == "y": 
        mapping = {"F":"R", "R":"B", "B":"L", "L":"F", "U":"U", "D":"D"}
    # y' (CCW): Front is Base L, Left is Base B, Back is Base R, Right is Base F
    elif rotation == "y'": 
        mapping = {"F":"L", "L":"B", "B":"R", "R":"F", "U":"U", "D":"D"}
    # y2 (180): Front is Base B, Back is Base F, Left is Base R, Right is Base L
    elif rotation == "y2": 
        mapping = {"F":"B", "B":"F", "L":"R", "R":"L", "U":"U", "D":"D"}
    else:
        return moves_str
        
    moves = moves_str.split()
    new_moves = []
    for m in moves:
        face = m[0]
        suffix = m[1:]
        new_face = mapping.get(face, face)
        new_moves.append(new_face + suffix)
    return " ".join(new_moves)

def get_y_delta(current_rot, target_rot):
    # Map rotations to degrees
    rot_map = {"":0, "y":90, "y2":180, "y'":270}
    reverse_map = {0:"", 90:"y", 180:"y2", 270:"y'"}
    
    curr = rot_map.get(current_rot, 0)
    target = rot_map.get(target_rot, 0)
    
    delta = (target - curr) % 360
    return reverse_map.get(delta, f"y_error_{delta}")

_SOLVER_CACHE = {}

def call_cpp_solver(scramble, rotation="", bl=0, br=0, fr=0, fl=0, max_length=15, sol_num=1, restrict="UDLRFB"):
    cache_key = (scramble, rotation, bl, br, fr, fl, max_length, restrict)
    if cache_key in _SOLVER_CACHE:
        return _SOLVER_CACHE[cache_key]
        
    cmd = [
        CPP_SOLVER_PATH,
        scramble,
        rotation,
        str(int(bl)),
        str(int(br)),
        str(int(fr)),
        str(int(fl)),
        str(max_length),
        str(sol_num),
        restrict
    ]
    try:
        cwd = os.path.join(os.path.dirname(__file__), "RubiksSolverCpp")
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, cwd=cwd, timeout=12)
        lines = result.strip().split('\n')
        sol = ""
        for line in lines:
            if ":" in line:
                sol = line.split(":", 1)[1].strip()
                # Strip the rotation prefix if it exists
                if rotation and sol.startswith(rotation + " "):
                    sol = sol[len(rotation):].strip()
                break
        
        _SOLVER_CACHE[cache_key] = sol
        return sol
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Search timed out at depth {max_length}")
        return "TIMEOUT"
    except Exception as e:
        print(f"[CPP ERROR] {e}")
        return "ERROR"

# --- Ergonomic Move Optimization ---
def find_best_ergonomic_solution(state, bl, br, fr, fl, depth, restrict_b=True):
    rotations = ["", "y", "y'", "y2"]
    best_sol_moves = None # Just the moves
    best_target_rot = None # The rotation used ("" or "y" etc)
    best_internal = None # Transformed to base
    best_score = 999
    
    restrict = "UDLRF" if restrict_b else "UDLRFB"
    
    for rot in rotations:
        sol = call_cpp_solver(state, rot, bl, br, fr, fl, depth, 1, restrict)
        if sol and sol not in ["already solved", "ERROR", "TIMEOUT"]:
            moves_list = sol.split()
            count = len(moves_list)
            
            penalty = 0
            if rot == "y2": penalty = 5
            elif rot != "": penalty = 3
            
            b_count = sum(1 for m in moves_list if m.startswith('B'))
            penalty += b_count * 3
            
            score = count + penalty
            if score < best_score:
                best_score = score
                best_sol_moves = sol
                best_target_rot = rot
                best_internal = transform_moves(sol, rot)
                
    return best_sol_moves, best_target_rot, best_internal

# ---------------------------------------------

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    data = request.get_json()
    scramble = data.get('scramble', '')
    if not scramble:
        return jsonify({'error': 'No scramble provided'}), 400

    scramble = " ".join(scramble.split())
    _SOLVER_CACHE.clear()

    try:
        # 1. Yellow Cross Solution
        cross_moves = call_cpp_solver(scramble, "", 0, 0, 0, 0, 8, 1, "UDLRF")
        if cross_moves in ["ERROR", "TIMEOUT"]:
            return jsonify({'error': 'C++ Cross solver failed or timed out'}), 500
            
        current_state_str = (scramble + " " + cross_moves).strip()
        active_orientation = "" # Base

        # Greedy F2L Solve with Progressive Deepening and Ergonomic Selection
        import itertools
        unsolved_slots = ["BL", "BR", "FR", "FL"]
        results = {
            'scramble': scramble,
            'cross_solution': cross_moves,
            'f2l_bl': "No solution",
            'f2l_br': "No solution",
            'f2l_fr': "No solution",
            'f2l_fl': "No solution",
            'solve_order': []
        }
        solved_flags = {"BL": False, "BR": False, "FR": False, "FL": False}

        # Refined depth stages
        depth_stages = [9, 11, 13, 14] 
        
        def update_already_solved():
            nonlocal current_state_str
            detected_any = False
            for slot in list(unsolved_slots):
                flags = solved_flags.copy()
                flags[slot] = True
                check = call_cpp_solver(current_state_str, "", flags["BL"], flags["BR"], flags["FR"], flags["FL"], 0, 1)
                if check == "already solved":
                    results[f'f2l_{slot.lower()}'] = "Already Solved"
                    if not any(slot in info for info in results['solve_order']):
                        results['solve_order'].append(f"{slot} (Auto)")
                    solved_flags[slot] = True
                    unsolved_slots.remove(slot)
                    detected_any = True
            return detected_any

        update_already_solved()

        while unsolved_slots:
            best_sol_moves = None
            best_target_rot = None
            best_internal = None
            best_combo = None
            found_at_depth = None

            found = False
            for d in depth_stages:
                # Try multi-slotting (3 or 2 slots) only at lower depths to save time
                if d <= 12:
                    nums_to_try = range(min(3, len(unsolved_slots)), 1, -1)
                else:
                    nums_to_try = [] # Only try 1 slot at high depth
                
                # Check for 1 slot at all depths
                nums_to_try = list(nums_to_try) + [1]
                
                for num_to_solve in nums_to_try:
                    for combo in itertools.combinations(unsolved_slots, num_to_solve):
                        flags = solved_flags.copy()
                        for slot in combo:
                            flags[slot] = True
                        
                        sol_moves, target_rot, internal = find_best_ergonomic_solution(
                            current_state_str, 
                            flags["BL"], flags["BR"], flags["FR"], flags["FL"], 
                            d, restrict_b=True
                        )
                        
                        if sol_moves:
                            best_sol_moves = sol_moves
                            best_target_rot = target_rot
                            best_internal = internal
                            best_combo = combo
                            found_at_depth = d
                            found = True
                            break
                    if found: break
                if found: break

            # 2. Last Resort (Try any single slot, allow B moves, highest depth)
            if not found:
                for slot in unsolved_slots:
                    flags = solved_flags.copy()
                    flags[slot] = True
                    sol = call_cpp_solver(current_state_str, "", flags["BL"], flags["BR"], flags["FR"], flags["FL"], 15, 1, "UDLRFB")
                    if sol and sol not in ["ERROR", "TIMEOUT", "already solved"]:
                        best_sol_moves = sol
                        best_target_rot = "" # Last resort assumes base
                        best_internal = sol 
                        best_combo = [slot]
                        found_at_depth = 15
                        found = True
                        break

            if found:
                # Calculate relative rotation from active_orientation to best_target_rot
                y_prefix = get_y_delta(active_orientation, best_target_rot)
                human_instruction = (y_prefix + " " + best_sol_moves).strip()
                active_orientation = best_target_rot # Update active orientation
                
                type_label = "Multi" if len(best_combo) > 1 else ("Easy" if found_at_depth <= 9 else ("Medium" if found_at_depth <= 12 else "Deep"))
                
                slot_info = " + ".join(best_combo)
                results['solve_order'].append(f"{slot_info} ({type_label})")
                
                primary_slot = best_combo[0]
                results[f'f2l_{primary_slot.lower()}'] = human_instruction
                for extra_slot in best_combo[1:]:
                    results[f'f2l_{extra_slot.lower()}'] = "Already Solved"
                
                print(f"[STEP {len(results['solve_order'])}] Solved: {slot_info} via {human_instruction} (Internal: {best_internal})")
                current_state_str = (current_state_str + " " + best_internal).strip()
                for slot in best_combo:
                    solved_flags[slot] = True
                    if slot in unsolved_slots:
                        unsolved_slots.remove(slot)
                
                update_already_solved()
            else:
                print(f"[FAIL] No solution found for targets: {unsolved_slots}")
                break

        return jsonify(results)

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error: {error_detail}")
        return jsonify({'error': f'Solver error: {str(e)}'}), 500

if __name__ == '__main__':
    # Run on localhost port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
