#!/usr/bin/env python3
import sys
sys.path.append('RubiksSolver')
from RubiksSolver.solver import solve_cross, solve_F2L

# Test with a simple scramble
scramble = "R U R' U'"
print(f'Testing scramble: {scramble}')
print('=' * 50)

# Test cross solve
print('\nSolving cross...')
cross_sol = solve_cross(scramble, '', 8, False, 0, 'test_cross', [])
print(f'Cross solution: {cross_sol}')
print()

# Test F2L solve
print('Solving F2L (cross + all 4 pairs)...')
f2l_sol = solve_F2L(scramble, '', True, True, True, True, 20, False, 0, 'test_f2l', [])
print(f'F2L solution: {f2l_sol}')
print()

# Test with a more complex scramble
scramble2 = "F R U' R' U' R U R' F' R U R' U' R' F R F'"
print(f'\nTesting complex scramble: {scramble2}')
print('=' * 50)

print('\nSolving cross...')
cross_sol2 = solve_cross(scramble2, '', 8, False, 0, 'test_cross2', [])
print(f'Cross solution: {cross_sol2}')
print()

print('Solving F2L (cross + all 4 pairs)...')
f2l_sol2 = solve_F2L(scramble2, '', True, True, True, True, 20, False, 0, 'test_f2l2', [])
print(f'F2L solution: {f2l_sol2}')
