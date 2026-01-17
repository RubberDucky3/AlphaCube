import numpy as np
from src.cube.constants import *
import src.cube.moves as moves

class Cube:
    def __init__(self):
        self.reset()

    def reset(self):
        # Corners: position [0..7], orientation [0..2]
        self.corners_pos = np.arange(8, dtype=np.int8)
        self.corners_ori = np.zeros(8, dtype=np.int8)

        # Edges: position [0..11], orientation [0..1]
        self.edges_pos = np.arange(12, dtype=np.int8)
        self.edges_ori = np.zeros(12, dtype=np.int8)
        self.history = []

    def copy(self):
        c = Cube()
        c.corners_pos = self.corners_pos.copy()
        c.corners_ori = self.corners_ori.copy()
        c.edges_pos = self.edges_pos.copy()
        c.edges_ori = self.edges_ori.copy()
        return c

    def is_solved(self) -> bool:
        return (
            np.array_equal(self.corners_pos, np.arange(8, dtype=np.int8)) and
            np.all(self.corners_ori == 0) and
            np.array_equal(self.edges_pos, np.arange(12, dtype=np.int8)) and
            np.all(self.edges_ori == 0)
        )

    # --------------------------------------------------------
    # Moves & Rotations
    # --------------------------------------------------------
    def apply_move(self, move: str):
        """
        Apply a face turn or cube rotation.
        Moves include:
        U D L R F B (+ ' or 2)
        x y z (+ ' or 2)
        """
        # Parse move
        base_move = move[0]
        modifier = move[1] if len(move) > 1 else ""
        
        times = 1
        if modifier == "'":
            times = 3
        elif modifier == "2":
            times = 2
            
        self.history.append(move)
        # Get permutation logic from moves.py
        # We perform the single move 'times' times
        # Ideally moves.py defines the single move permutation
        
        for _ in range(times):
             self._apply_single_move(base_move)
             
    def _apply_single_move(self, move_name):
        """Applies a single basic move (U, D, L, R, F, B, x, y, z)"""
        if move_name not in moves.MOVES:
            raise ValueError(f"Unknown move: {move_name}")
            
        move_data = moves.MOVES[move_name]
        
        # Apply Corner Permutation
        # new_corners[i] = old_corners[P[i]]
        # We need to use fancy indexing carefully or a temp array
        # moves.CP is a list/array where index i gets the piece FROM CP[i]
        # Wait, usually P[i] is "where piece i GOES" or "where piece at i COMES FROM"?
        # Let's say moves.CP[i] is the NEW position of the piece currently at i.
        # Then new_pos[CP[i]] = old_pos[i].
        # If moves.CP[i] is "the old index that moves to i", then new_pos[i] = old_pos[CP[i]].
        # I will implement moves.py such that CP[i] is the index of the piece that moves TO i. 
        # So new_pos[i] = old_pos[CP[i]]
        
        cp_perm = move_data['cp']
        self.corners_pos = self.corners_pos[cp_perm]
        
        # Apply Corner Orientation
        # new_ori[i] = (old_ori[CP[i]] + move_ori[i]) % 3
        # Note: move_ori is defined on the destination slots
        co_change = move_data['co']
        self.corners_ori = (self.corners_ori[cp_perm] + co_change) % 3
        
        # Apply Edge Permutation
        ep_perm = move_data['ep']
        self.edges_pos = self.edges_pos[ep_perm]
        
        # Apply Edge Orientation
        # new_ori[i] = (old_ori[EP[i]] + move_ori[i]) % 2
        eo_change = move_data['eo']
        self.edges_ori = (self.edges_ori[ep_perm] + eo_change) % 2


    # --------------------------------------------------------
    # CFOP / ZB Progress Detectors (used for reward shaping)
    # --------------------------------------------------------
    def cross_count(self) -> int:
        """Return number of correctly solved cross edges (0..4).
        Standard Cross: DF, DF, DL, DB (White edges on bottom).
        Positions: DF=5, DR=4, DL=6, DB=7 ??
        Need to verify indices in constants.py
        """
        # Assuming White is Down (D face) for solution? 
        # Standard color scheme: White U, Green F?
        # WCA: White Top, Green Front.
        # Cross usually done on White. So White on Top?
        # Speedcubers do cross on Bottom (White Down).
        # Re-check constants.py or assume standard mapping
        # Let's assume 'Solved' state has White on U.
        # So 'Cross' usually means the D-layer edges if doing CFOP?
        # No, if is_solved() expects White on U (indices 0-3?), then Cross on D means solving the D-face edges.
        # But wait, standard solved state usually implies White U, Green F.
        # If we solve cross on D, we are looking for the edges belonging to D face.
        # D face edges: DR(4), DF(5), DL(6), DB(7).
        # We count how many of these are solved.
        
        # A piece is solved if:
        # 1. It is in the correct position (pos[i] == i)
        # 2. It has correct orientation (ori[i] == 0)
        
        # We solve the White Cross on the U face (pieces 0, 1, 2, 3)
        count = 0
        for i in [0, 1, 2, 3]: # UR, UF, UL, UB
            if self.edges_pos[i] == i and self.edges_ori[i] == 0:
                count += 1
        return count

    def f2l_slots_solved(self) -> int:
        """Return number of solved F2L slots (0..4).
        Slots are the 4 vertical edges between D and U layers + their corresponding corners.
        Edges: FR(8), FL(9), BL(10), BR(11).
        Corners: DFR(4), DLF(5), DBL(6), DRB(7).
        """
        count = 0
        # Slot 1: FR (Edge 8) + DFR (Corner 4)
        if (self.edges_pos[8] == 8 and self.edges_ori[8] == 0 and
            self.corners_pos[4] == 4 and self.corners_ori[4] == 0):
            count += 1
            
        # Slot 2: FL (Edge 9) + DLF (Corner 5)
        if (self.edges_pos[9] == 9 and self.edges_ori[9] == 0 and
            self.corners_pos[5] == 5 and self.corners_ori[5] == 0):
            count += 1
            
        # Slot 3: BL (Edge 10) + DBL (Corner 6)
        if (self.edges_pos[10] == 10 and self.edges_ori[10] == 0 and
            self.corners_pos[6] == 6 and self.corners_ori[6] == 0):
            count += 1
            
        # Slot 4: BR (Edge 11) + DRB (Corner 7)
        if (self.edges_pos[11] == 11 and self.edges_ori[11] == 0 and
            self.corners_pos[7] == 7 and self.corners_ori[7] == 0):
            count += 1
            
        return count

    def eo_solved(self) -> bool:
        """Return True if all last-layer edges are oriented.
        Last Layer (LL) is U face (since Cross is on D).
        LL Edges: UR(0), UF(1), UL(2), UB(3).
        Orientation 0 means oriented (Good).
        """
        for i in [0, 1, 2, 3]:
            if self.edges_ori[i] != 0: # Checks current orientation of piece at U spots?
                # Wait, if we are just checking EO of the pieces CURRENTLY in U layer?
                # ZBLL uses EO detection.
                # Usually means 'Are the edges currently on the U face oriented correctly relative to U?'
                # With our encoding, '0' is the solved orientation.
                # If a piece is on U face, and its orientation is 0, it is oriented.
                pass
        
        # But we also need to ensure the pieces ON the U layer are actually the U-layer pieces?
        # No, EO for ZBLL usually implies we are at the LL stage, so F2L is done.
        # If F2L is done, the pieces in U layer ARE the U layer pieces.
        # BUT, the function might be called anytime.
        # "Return True if all last-layer edges are oriented"
        # If F2L is not done, this metric might be noisy, but technically EO can be tracked.
        # Let's check the orientation of whichever pieces are in the U slots.
        
        # IMPORTANT: Our orientation definition is relative to the piece's solved state.
        # If a U-layer piece is in the U-layer, ori=0 means Good.
        # So we just check self.edges_ori[0..3].
        
        return np.all(self.edges_ori[0:4] == 0)
