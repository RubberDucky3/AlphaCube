# f2lsolver_cfop_cross.py

import pycuber as pc

# ---------- ASCII Print Function ----------
def print_pycube_ascii(cube, highlight_white_cross=False):
    def flatten(face):
        return [str(sticker) for row in face for sticker in row]

    faces = {face: flatten(getattr(cube, face)) for face in ['U','D','F','B','R','L']}

    def highlight(color, pos):
        if highlight_white_cross and color == 'W' and pos in [1,3,5,7]:
            return f"*W*"
        return color

    # U face
    print("      ", faces['U'][0], faces['U'][1], faces['U'][2])
    print("      ", faces['U'][3], faces['U'][4], faces['U'][5])
    print("      ", faces['U'][6], faces['U'][7], faces['U'][8])

    # Middle layer: L F R B
    for i in range(3):
        print(faces['L'][i*3], faces['L'][i*3+1], faces['L'][i*3+2],
              faces['F'][i*3], faces['F'][i*3+1], faces['F'][i*3+2],
              faces['R'][i*3], faces['R'][i*3+1], faces['R'][i*3+2],
              faces['B'][i*3], faces['B'][i*3+1], faces['B'][i*3+2])

    # D face
    print("      ", highlight(faces['D'][0],0), highlight(faces['D'][1],1), highlight(faces['D'][2],2))
    print("      ", highlight(faces['D'][3],3), highlight(faces['D'][4],4), highlight(faces['D'][5],5))
    print("      ", highlight(faces['D'][6],6), highlight(faces['D'][7],7), highlight(faces['D'][8],8))
    print()

# ---------- White Cross Detection ----------
def white_cross_solved(cube):
    def flatten(face):
        return [str(sticker) for row in face for sticker in row]

    faces = {face: flatten(getattr(cube, face)) for face in ['U','D','F','B','R','L']}

    return (
        faces['D'][1] == 'W' and faces['F'][7] == 'G' and
        faces['D'][3] == 'W' and faces['L'][7] == 'O' and
        faces['D'][5] == 'W' and faces['R'][7] == 'R' and
        faces['D'][7] == 'W' and faces['B'][7] == 'B'
    )

# ---------- Helper: Edge Mapping ----------
EDGE_TARGETS = {
    'F': {'d_index':1,'side_index':7,'side_center':'G'},
    'R': {'d_index':5,'side_index':7,'side_center':'R'},
    'B': {'d_index':7,'side_index':7,'side_center':'B'},
    'L': {'d_index':3,'side_index':7,'side_center':'O'}
}

# U-layer positions of edges for easy search (U face indices)
U_EDGE_POSITIONS = {
    'F': (6,1), # U6-F1
    'R': (8,1), # U8-R1
    'B': (2,1), # U2-B1
    'L': (0,1)  # U0-L1
}

# ---------- CFOP White Cross Solver ----------
def solve_white_cross(cube):
    """Solve the white cross on a pycuber Cube.
    Uses a deterministic CFOP-style algorithm with a per-slot iteration limit to avoid infinite loops.
    Returns the list of moves applied.
    """
    moves_done = []
    # Iterate over each target edge (F, R, B, L)
    for slot, target in EDGE_TARGETS.items():
        iteration = 0
        max_iterations = 200
        while True:
            iteration += 1
            if iteration > max_iterations:
                print(f"Reached max iteration limit for {slot} edge, aborting.")
                break
            # Gather current faces
            faces = {face: [str(sticker) for row in getattr(cube, face) for sticker in row]
                     for face in ['U','D','F','B','R','L']}
            # Check if this edge is already solved
            if faces['D'][target['d_index']] == 'W' and faces[slot][target['side_index']] == target['side_center']:
                break
            # Step 1: white sticker on U layer
            u_idx, side_idx = U_EDGE_POSITIONS[slot]
            if faces['U'][u_idx] == 'W':
                # Rotate U until side color matches
                for _ in range(4):
                    faces = {face: [str(sticker) for row in getattr(cube, face) for sticker in row]
                             for face in ['U','D','F','B','R','L']}
                    if faces[slot][side_idx] == target['side_center']:
                        move = slot + "2"
                        cube(move)
                        moves_done.append(move)
                        print(f"Inserted {slot}-white edge from U layer")
                        print_pycube_ascii(cube, highlight_white_cross=True)
                        break
                    else:
                        cube("U")
                        moves_done.append("U")
                continue
            # Step 2: white edge on side face
            side_faces = ['F','R','B','L']
            found = False
            for s_face in side_faces:
                for idx in [1,3,5,7]:
                    if faces[s_face][idx] == 'W':
                        # Bring it to U layer
                        if s_face == 'F':
                            cube("F U F'")
                            moves_done.extend(["F","U","F'"])
                        elif s_face == 'R':
                            cube("R U R'")
                            moves_done.extend(["R","U","R'"])
                        elif s_face == 'B':
                            cube("B U B'")
                            moves_done.extend(["B","U","B'"])
                        elif s_face == 'L':
                            cube("L U L'")
                            moves_done.extend(["L","U","L'"])
                        print(f"Moved {s_face}-white edge to U layer")
                        print_pycube_ascii(cube, highlight_white_cross=True)
                        found = True
                        break
                if found:
                    break
            if found:
                continue
            # Step 3: white edge on D layer but misoriented
            if faces['D'][target['d_index']] == 'W' and faces[slot][target['side_index']] != target['side_center']:
                cube(f"{slot}' U2 {slot}")
                moves_done.extend([f"{slot}'", "U2", slot])
                print(f"Flipped {slot}-white edge from D layer")
                print_pycube_ascii(cube, highlight_white_cross=True)
                continue
        # end while for this slot
    return moves_done

# ---------- Main ----------
if __name__ == "__main__":
    cube = pc.Cube()

    scramble = "R' L' U2 D' B U R F B2 U2 B2 R2 U L2 D' F2 U L2 D2 B R2"
    print(f"Applying scramble: {scramble}\n")

    print("Cube before scramble:")
    print_pycube_ascii(cube, highlight_white_cross=True)

    cube(scramble)

    print("Cube after scramble:")
    print_pycube_ascii(cube, highlight_white_cross=True)

    if not white_cross_solved(cube):
        print("Solving white cross...\n")
        moves = solve_white_cross(cube)
        print("White cross moves applied:", " ".join(moves))
    else:
        print("White cross already solved!")

    print("Final cube state:")
    print_pycube_ascii(cube, highlight_white_cross=True)
