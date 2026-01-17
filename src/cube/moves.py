import numpy as np

# Indices for reference from constants.py (conceptually)
# Corners: 0:URF, 1:UFL, 2:ULB, 3:UBR, 4:DFR, 5:DLF, 6:DBL, 7:DRB
# Edges:   0:UR, 1:UF, 2:UL, 3:UB, 4:DR, 5:DF, 6:DL, 7:DB, 8:FR, 9:FL, 10:BL, 11:BR

# Identity Permutation
ID_CP = np.arange(8)
ID_EP = np.arange(12)
ID_CO = np.zeros(8, dtype=np.int8)
ID_EO = np.zeros(12, dtype=np.int8)

# Move Definitions
# format: 'MOVE': {'cp': [indices], 'co': [offsets], 'ep': [indices], 'eo': [offsets]}
# P[i] is the source index for destination i.
# new_pos[i] = old_pos[P[i]]

MOVES = {}

# =============================================================================
# FACE TURNS
# =============================================================================

# U Move (Up)
# URF(0) -> UFL(1) -> ULB(2) -> UBR(3) -> URF(0)
# Cycles: Corners (0 1 2 3), Edges (0 1 2 3)
# CP: dest 0 gets source 3, dest 1 gets 0, dest 2 gets 1, dest 3 gets 2
# CO: No change on U turn
# EP: dest 0 gets source 3, etc.
# EO: No change on U turn
MOVES['U'] = {
    'cp': np.array([3, 0, 1, 2, 4, 5, 6, 7]),
    'co': np.zeros(8, dtype=np.int8),
    'ep': np.array([3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11]),
    'eo': np.zeros(12, dtype=np.int8)
}

# D Move (Down)
# CW from bottom: DFR(4) -> DRB(7) -> DBL(6) -> DLF(5) -> DFR(4)
# dest 7 gets 4, dest 6 gets 7, dest 5 gets 6, dest 4 gets 5
MOVES['D'] = {
    'cp': np.array([0, 1, 2, 3, 5, 6, 7, 4]),
    'co': np.zeros(8, dtype=np.int8),
    'ep': np.array([0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11]),
    'eo': np.zeros(12, dtype=np.int8)
}

# L Move (Left)
# Cycles: Corners (1 5 6 2) -> UFL(1)->DLF(5)->DBL(6)->ULB(2)->UFL(1)
# Edges: (2 5 6 10) -> UL(2)->DL(6)->BL(10)? No, UL(2)->FL(9)?
# Edges on L face: UL(2), FL(9), DL(6), BL(10).
# L turn CW:
# UL(2) -> FL(9) -> DL(6) -> BL(10) -> UL(2)
# CP: dest 1 gets 2, dest 5 gets 1, dest 6 gets 5, dest 2 gets 6
# CO: L/R turns change orientation of corners.
# UFL(1): starts U-facing. Moves to DLF(5). On L turn, U sticker goes to F? No, L sticker.
# Wait, L turn implies rotation around L axis.
# Standard: U/D turns preserve corner orientation. F/B/L/R turns change it.
# Usually: +1 CW, +2 CCW.
# Cycle (1 5 6 2).
# 1->5: Twist +1 ?
# 5->6: Twist +1 ?
# 6->2: Twist +1 ?
# 2->1: Twist +1 ? -> Sum 4? No.
# Standard algs say: 
# 1(UFL) -> 5(DLF) : CW (+1). U sticker goes to F (which is 'side' for D corners. D is 'good').
# 5(DLF) -> 6(DBL) : CCW (-1 aka +2).
# 6(DBL) -> 2(ULB) : CW (+1).
# 2(ULB) -> 1(UFL) : CCW (-1 aka +2).
# Sum: 1 + 2 + 1 + 2 = 6 = 0 mod 3. Correct.
MOVES['L'] = {
    'cp': np.array([0, 2, 6, 3, 4, 1, 5, 7]), # 1<-2, 5<-1, 6<-5, 2<-6
    'co': np.array([0, 2, 1, 0, 0, 1, 2, 0]), # Dest 1 gets +2? 
    # Logic: New orientation at dest i = (Old orientation at src + Twist) % 3
    # Wait, co array here is 'Twist applied to the piece landing at i'.
    # Piece at 2 moves to 1. 2->1 is Twist +2. So at dest 1, we add +2.
    # Piece at 1 moves to 5. 1->5 is Twist +1. So at dest 5, we add +1.
    # Piece at 5 moves to 6. 5->6 is Twist +2. So at dest 6, we add +2.
    # Piece at 6 moves to 2. 6->2 is Twist +1. So at dest 2, we add +1.
    # Indices: 0 1 2 3 4 5 6 7
    # Values:  0 2 1 0 0 1 2 0
    'ep': np.array([0, 1, 6, 3, 4, 5, 10, 7, 8, 2, 9, 11]), # 2<-6? No.
    # Cycle: 2(UL) -> 9(FL) -> 6(DL) -> 10(BL) -> 2(UL)
    # dest 2 gets 10. dest 9 gets 2. dest 6 gets 9. dest 10 gets 6.
    # My array above: dest 2 (idx 2) has 6? NO.
    # Let's fix.
    # dest 2 gets 10.
    # dest 9 gets 2.
    # dest 6 gets 9.
    # dest 10 gets 6.
    # Fixed array below.
    # EO: L/R moves do NOT flip edges if using standard FB-LR definition?
    # Actually, it depends on the reference frame.
    # "Good" edge logic (ZZ method): U/D/L/R moves are good. F/B are bad.
    # So L should be 0 change.
    'eo': np.zeros(12, dtype=np.int8) 
}
# Correction for L 'ep':
# Old: 0 1 2 3 4 5 6 7 8 9 10 11
# New: 0 1 10 3 4 5 9 7 8 2 6 11
MOVES['L']['ep'] = np.array([0, 1, 10, 3, 4, 5, 9, 7, 8, 2, 6, 11])


# R Move (Right)
# Cycles: Corners (0 3 7 4) -> URF(0)->UBR(3)->DRB(7)->DFR(4)->URF(0)
# 0->3: Twist +1? (U sticker goes to B, which is 'side' for U). No. 
# URF(0) U sticker is Top. Moves to UBR(3). UBR U sticker is Top.
# R turn rotates R face.
# Piece at 0(URF) rotates to 3(UBR)?
# Clockwise R:
# 0(URF) -> 3(UBR) (CCW? No)
# Let's visualize R face.
# TR(3-UBR)  TL(0-URF)  <-- This is looking from Right?
# Let's use standard cycle: URF(0) -> UBR(3) -> DRB(7) -> DFR(4) -> URF(0).
# Twist:
# 0->3: Twist +1 (CW) - NO. Geometric check.
# U sticker on 0 is U. After R turn, it goes to B face of 3. B is 'side'. Twist +1.
# 3->7: Twist +2 (CCW).
# 7->4: Twist +1.
# 4->0: Twist +2.
# Dest 3 gets piece 0 (+1). Dest 7 gets 3 (+2). Dest 4 gets 7 (+1). Dest 0 gets 4 (+2).
MOVES['R'] = {
    'cp': np.array([4, 1, 2, 0, 7, 5, 6, 3]), # 0<-4, 3<-0, 7<-3, 4<-7
    'co': np.array([2, 0, 0, 1, 1, 0, 0, 2]),
    # Edges: UR(0) -> BR(11) -> DR(4) -> FR(8) -> UR(0)
    # dest 0 gets 8. dest 11 gets 0. dest 4 gets 11. dest 8 gets 4.
    'ep': np.array([8, 1, 2, 3, 11, 5, 6, 7, 4, 9, 10, 0]),
    'eo': np.zeros(12, dtype=np.int8)
}


# F Move (Front)
# Cycles: Corners (1 0 4 5) -> UFL->URF->DFR->DLF->UFL
# 0(URF)->4(DFR): Twist +1
# 4(DFR)->5(DLF): Twist +2
# 5(DLF)->1(UFL): Twist +1
# 1(UFL)->0(URF): Twist +2
# Dest 4 gets 0 (+1). Dest 5 gets 4 (+2). Dest 1 gets 5 (+1). Dest 0 gets 1 (+2).
# Edges: UF(1) -> FR(8) -> DF(5) -> FL(9) -> UF(1)
# dest 1 gets 9. dest 8 gets 1. dest 5 gets 8. dest 9 gets 5.
# EO: F/B turns flips edges (val 1).
MOVES['F'] = {
    'cp': np.array([1, 5, 2, 3, 0, 4, 6, 7]), # 0<-1, 4<-0, 5<-4, 1<-5
    'co': np.array([2, 1, 0, 0, 1, 2, 0, 0]),
    'ep': np.array([0, 9, 2, 3, 4, 8, 6, 7, 1, 5, 10, 11]),
    'eo': np.array([0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0]) # 1, 8, 5, 9 get flip
}

# B Move (Back)
# Cycles: Corners (3 2 6 7) -> UBR->ULB->DBL->DRB->UBR
# 3->2: +1?
# 2->6: +2?
# 6->7: +1?
# 7->3: +2?
# Dest 2 gets 3 (+1). Dest 6 gets 2 (+2). Dest 7 gets 6 (+1). Dest 3 gets 7 (+2).
# Edges: UB(3) -> BL(10) -> DB(7) -> BR(11) -> UB(3)
# Dest 3 gets 11. Dest 10 gets 3. Dest 7 gets 10. Dest 11 gets 7.
# EO: B flips edges.
MOVES['B'] = {
    'cp': np.array([0, 1, 3, 7, 4, 5, 2, 6]), # 2<-3, 6<-2, 7<-6, 3<-7
    'co': np.array([0, 0, 1, 2, 0, 0, 2, 1]),
    'ep': np.array([0, 1, 2, 11, 4, 5, 6, 10, 8, 9, 3, 7]),
    'eo': np.array([0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1])
}

# =============================================================================
# CUBE ROTATIONS
# =============================================================================

# x Rotation (Follows R)
# Entire cube rotates like R.
# Corners: (0 3 7 4) AND (1 2 6 5)
# R-layer cycle: 0->3->7->4->0 (Same as R)
# L-layer cycle: 1->2->6->5->1 (Same dir as R)
# Twist logic same as R.
# Edges: (0 11 4 8) (R-def) AND (2 10 6 9) (L-def but parallel) AND (1 3 7 5) (M slice)
# EO: No EO change on rotation.
MOVES['x'] = {
    'cp': np.array([4, 5, 1, 0, 7, 6, 2, 3]), # 0<-4, 3<-0... 1<-5, 2<-1, 6<-2, 5<-6
    'co': np.array([2, 1, 2, 1, 1, 2, 1, 2]),
    'ep': np.array([8, 3, 10, 7, 11, 1, 9, 5, 4, 2, 6, 0]),
    # 0<-8 NO. Cycle 0->3->7->4->0? No that's R face.
    # R face edges: 0->11->4->8->0. Dest 0 gets 8? No, dest 0 gets 8 is R'
    # Checking R move again: R cycle 0->11->4->8->0 is NOT what I wrote.
    # My R ep: dest 0 gets 8.
    # If 0->11, dest 11 gets 0.
    # If 11->4, dest 4 gets 11.
    # If 4->8, dest 8 gets 4.
    # If 8->0, dest 0 gets 8. 
    # Yes, this matches.
    # So x matches R for R-layer edges.
    # M slice: UF(1) -> UB(3) -> DB(7) -> DF(5) -> UF(1) ?
    # x rotation: Up face becomes Back? No, x follows R.
    # R puts Up face to Back. So UF -> UB ? No.
    # U -> B. F -> U. D -> F. B -> D.
    # UF(1) -> UB(3) [Up-Front to Back-Up?? No. Front-Up to Up-Back?]
    # UF is 'Edge on Up face, Front side'.
    # After x, 'Up' face is now 'Back'. 'Front' face is now 'Up'.
    # So piece at UF (Up-Front) physically moves to Back-Up (BU = UB(3)).
    # Wait, UF is (1). UB is (3).
    # If UF piece moves to UB, then dest 3 gets 1.
    # My array: dest 3 gets 7?
    # Let's retry M slice.
    # Faces: U->B, B->D, D->F, F->U.
    # UF(1) is between U and F.
    # Becomes between B and U (UB=3).
    # UB(3) is between U and B.
    # Becomes between B and D (DB=7).
    # DB(7) is between D and B.
    # Becomes between F and D (DF=5).
    # DF(5) is between D and F.
    # Becomes between F and U (UF=1).
    # So Cycle: 1->3->7->5->1.
    # Dest 3 gets 1. Dest 7 gets 3. Dest 5 gets 7. Dest 1 gets 5.
    
    # L Face edges (follow L' direction? No, L and R rotate same way in x).
    # L cycle: UL(2)->BL(10)->DL(6)->FL(9)->UL(2). (Compare L: 2->9->6->10->2).
    # x implies 2->10->6->9->2.
    # Dest 10 gets 2. Dest 6 gets 10. Dest 9 gets 6. Dest 2 gets 9.
    
    # Let's rebuild 'ep'.
    # 0 gets 8. 1 gets 5. 2 gets 9. 3 gets 1. 4 gets 11. 5 gets 7.
    # 6 gets 10. 7 gets 3. 8 gets 4. 9 gets 6. 10 gets 2. 11 gets 0.
    # Array: [8, 5, 9, 1, 11, 7, 10, 3, 4, 6, 2, 0]
    
    'eo': np.zeros(12, dtype=np.int8) 
}
MOVES['x']['ep'] = np.array([8, 5, 9, 1, 11, 7, 10, 3, 4, 6, 2, 0])

# y Rotation (Follows U)
# Corners: (0 1 2 3) and (4 5 6 7)
# Edges: (0 1 2 3) and (4 5 6 7) and (8 9 10 11)
# Simply U and D' (D prime moves same way as U). And E slice.
MOVES['y'] = {
    'cp': np.array([3, 0, 1, 2, 7, 4, 5, 6]),
    'co': np.zeros(8, dtype=np.int8),
    'ep': np.array([3, 0, 1, 2, 7, 4, 5, 6, 11, 8, 9, 10]),
    'eo': np.zeros(12, dtype=np.int8)
}

# z Rotation (Follows F)
# Faces: U->L, L->D, D->R, R->U.
# Corners: (1 0 4 5) F-layer. (2 3 7 6) B-layer.
# Edges: (1 8 5 9) F-layer. (3 10 7 11) B-layer? No check S slice. (0 2 6 4) M? No.
# F-layer edges cyclic: UF(1)->FL(9)->DF(5)->FR(8)->UF(1). (Note: F turn is 1->8->5->9).
# z follows F! So normal F cycle: 1->8->5->9->1.
# Dest 8 gets 1. Dest 5 gets 8. Dest 9 gets 5. Dest 1 gets 9.
# B-layer: UB(3)->BL(10)->DB(7)->BR(11)->UB(3) ? 
# z rotates entire cube CW from Front.
# UB(3) (up-back) -> LB (left-back) = BL(10)?
# Yes. U->L.
# BL(10) -> DB(7).
# DB(7) -> BR(11).
# BR(11) -> UB(3).
# Cycle 3->10->7->11->3.
# Dest 10 gets 3. Dest 7 gets 10. Dest 11 gets 7. Dest 3 gets 11.
# S slice (Middle Z): UR(0) -> UL(2) -> DL(6) -> DR(4) -> UR(0)?
# U->L. UR (Up-Right) -> LF (Left-Front?? No).
# UR(0) is on U and R. 
# After z: U->L, R->U.
# So UR -> LU = UL(2).
# UL(2) (U, L) -> L->D, U->L (oops).
# U->L, L->D. So UL -> LD = DL(6).
# DL(6) -> DR(4).
# DR(4) -> UR(0).
# Cycle 0->2->6->4->0.
# Dest 2 gets 0. Dest 6 gets 2. Dest 4 gets 6. Dest 0 gets 4.
# z Rotation (Follows F)
# Faces: U->R, R->D, D->L, L->U.
# Corners: F-layer (1->0->4->5), B-layer (2->3->7->6)
MOVES['z'] = {
    'cp': np.array([1, 5, 6, 2, 0, 4, 7, 3]),
    'co': np.array([1, 2, 1, 2, 2, 1, 2, 1]),
    # Edges: F(1->8->5->9), B(3->11->7->10), S(0->4->6->2)
    # dest 8 gets 1, dest 5 gets 8, dest 9 gets 5, dest 1 gets 9
    # dest 11 gets 3, dest 7 gets 11, dest 10 gets 7, dest 3 gets 10
    # dest 4 gets 0, dest 6 gets 4, dest 2 gets 6, dest 0 gets 2
    'ep': np.array([2, 9, 6, 10, 0, 8, 4, 11, 1, 5, 7, 3]),
    'eo': np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
}
