
import sqlite3
import numpy as np
import re
from src.cube.cube import Cube
from src.env.cube_env import CubeEnv
from src.cube.constants import MOVE_NAMES

def parse_moves(move_str):
    # Remove comments and garbage
    move_str = re.sub(r"//.*", "", move_str)
    move_str = re.sub(r"\(.*?\)", "", move_str).replace("|", "").replace("  ", " ")
    
    # Split handles spaces and newlines
    raw_moves = move_str.split()
    
    parsed = []
    for m in raw_moves:
        if m == "" or m == " " or "//" in m: continue
        
        # Handle wide moves (e.g. r -> x L, r' -> x' L')
        if m.startswith('r'):
             if "'" in m: parsed.extend(['x', "L'"])
             elif "2" in m: parsed.extend(['x2', "L2"])
             else: parsed.extend(['x', "L"])
        elif m.startswith('l'):
             if "'" in m: parsed.extend(["x'", "R'"])
             elif "2" in m: parsed.extend(["x2", "R2"])
             else: parsed.extend(["x'", "R"])
        elif m.startswith('u'):
             if "'" in m: parsed.extend(["y", "D'"])
             elif "2" in m: parsed.extend(["y2", "D2"])
             else: parsed.extend(["y", "D"])
        elif m.startswith('d'):
             if "'" in m: parsed.extend(["y'", "U'"])
             elif "2" in m: parsed.extend(["y2", "U2"])
             else: parsed.extend(["y'", "U"])
        elif m.startswith('f'):
             if "'" in m: parsed.extend(["z", "B'"])
             elif "2" in m: parsed.extend(["z2", "B2"])
             else: parsed.extend(["z", "B"])
        elif m.startswith('b'):
             if "'" in m: parsed.extend(["z'", "F'"])
             elif "2" in m: parsed.extend(["z2", "F2"])
             else: parsed.extend(["z'", "F"])
        elif m in ["M", "M'", "M2"]:
            # M follows L direction
            if m == "M": parsed.extend(["x'", "R", "L'"])
            elif m == "M'": parsed.extend(["x", "R'", "L"])
            elif m == "M2": parsed.extend(["x2", "R2", "L2"])
        else:
            # Handle standard moves, normalize ' to '
            m = m.replace("’", "'")
            # If it's a valid move, use it
            if m in MOVE_NAMES:
                parsed.append(m)
            elif m.lower() in [name.lower() for name in MOVE_NAMES]:
                # find the correct case
                for name in MOVE_NAMES:
                    if name.lower() == m.lower():
                        parsed.append(name)
                        break
    return parsed

def generate_bc_dataset(db_path, limit=1000, stage="full"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Select more columns to allow derivation
    cursor.execute(f"SELECT scramble, solution_raw, cross FROM solves WHERE solution_raw IS NOT NULL AND solution_raw != '' ORDER BY is_expert DESC, solve_id DESC LIMIT ?", (limit,))
    
    states = []
    actions = []
    distances = []
    
    move_to_idx = {name: i for i, name in enumerate(MOVE_NAMES)}
    
    for scramble_str, solution_raw, cross_col in cursor.fetchall():
        scramble_moves = parse_moves(scramble_str)
        
        # Decide which solution string to use
        raw_sol_moves = parse_moves(solution_raw)
        
        target_moves = []
        if stage == "cross":
            if cross_col and len(cross_col.strip()) > 0:
                target_moves = parse_moves(cross_col)
            else:
                # DERIVE CROSS: Apply moves until cross_count == 4
                temp_cube = Cube()
                for m in scramble_moves:
                    try: temp_cube.apply_move(m)
                    except: continue
                
                derived = []
                for m in raw_sol_moves:
                    if temp_cube.cross_count() == 4:
                        break
                    derived.append(m)
                    try: temp_cube.apply_move(m)
                    except: break
                target_moves = derived
        else:
            target_moves = raw_sol_moves
            
        if not target_moves: continue
        
        # Filter solution to only face moves for proper distance counting
        face_moves = [m for m in target_moves if m[0] not in ['x', 'y', 'z']]
        total_steps = len(face_moves)
        if total_steps == 0: continue

        cube = Cube()
        for m in scramble_moves:
            try: cube.apply_move(m)
            except: continue
            
        view = { 'U':'U', 'D':'D', 'L':'L', 'R':'R', 'F':'F', 'B':'B' }
        
        def rotate_view(v, rot):
            new_v = v.copy()
            if rot == 'x':
                new_v['U'], new_v['B'], new_v['D'], new_v['F'] = v['F'], v['U'], v['B'], v['D']
            elif rot == "x'":
                new_v['U'], new_v['F'], new_v['D'], new_v['B'] = v['B'], v['U'], v['F'], v['D']
            elif rot == 'x2':
                new_v['U'], new_v['D'], new_v['F'], new_v['B'] = v['D'], v['U'], v['B'], v['F']
            elif rot == 'y':
                new_v['F'], new_v['R'], new_v['B'], new_v['L'] = v['R'], v['B'], v['L'], v['F']
            elif rot == "y'":
                new_v['F'], new_v['L'], new_v['B'], new_v['R'] = v['L'], v['B'], v['R'], v['F']
            elif rot == 'y2':
                new_v['F'], new_v['B'], new_v['L'], new_v['R'] = v['B'], v['F'], v['R'], v['L']
            elif rot == 'z':
                new_v['U'], new_v['L'], new_v['D'], new_v['R'] = v['L'], v['D'], v['R'], v['U']
            elif rot == "z'":
                new_v['U'], new_v['R'], new_v['D'], new_v['L'] = v['R'], v['D'], v['L'], v['U']
            elif rot == 'z2':
                new_v['U'], new_v['D'], new_v['L'], new_v['R'] = v['D'], v['U'], v['R'], v['L']
            return new_v

        step_idx = 0
        for m in target_moves:
            if m[0] in ['x', 'y', 'z']:
                view = rotate_view(view, m)
                continue 
            
            face = m[0]
            suffix = m[1:] if len(m) > 1 else ""
            physical_face = view.get(face, face)
            physical_move = physical_face + suffix
            
            if physical_move not in move_to_idx: continue
            
            # New Structured Spatial Obs (Piece-wise)
            obs_spatial = np.zeros((20, 5), dtype=np.float32)
            # Corners
            for i in range(8):
                p = cube.corners_pos[i]
                o = cube.corners_ori[i]
                obs_spatial[i] = [0.0, i/7.0, p/7.0, o/2.0, 1.0 if (p==i and o==0) else 0.0]
            # Edges
            for i in range(12):
                p = cube.edges_pos[i]
                o = cube.edges_ori[i]
                obs_spatial[8+i] = [1.0, i/11.0, p/11.0, o/1.0, 1.0 if (p==i and o==0) else 0.0]
            
            states.append(obs_spatial.flatten())
            actions.append(move_to_idx[physical_move])
            distances.append(total_steps - step_idx)
            
            step_idx += 1
            try: cube.apply_move(physical_move)
            except: break
                
    conn.close()
    return np.array(states), np.array(actions), np.array(distances)
