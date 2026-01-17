import numpy as np
from src.cube.constants import *

class CubeState:
    def __init__(self):
        # 8 corners: [position, orientation]
        # Orientation: 0=solved, 1=twisted clockwise, 2=twisted counter-clockwise
        self.cp = np.arange(8, dtype=np.int8)
        self.co = np.zeros(8, dtype=np.int8)

        # 12 edges: [position, orientation]
        # Orientation: 0=good, 1=bad
        self.ep = np.arange(12, dtype=np.int8)
        self.eo = np.zeros(12, dtype=np.int8)

    def is_solved(self):
        return (
            np.array_equal(self.cp, np.arange(8, dtype=np.int8)) and
            np.all(self.co == 0) and
            np.array_equal(self.ep, np.arange(12, dtype=np.int8)) and
            np.all(self.eo == 0)
        )

    def copy(self):
        new_state = CubeState()
        new_state.cp = self.cp.copy()
        new_state.co = self.co.copy()
        new_state.ep = self.ep.copy()
        new_state.eo = self.eo.copy()
        return new_state

    def __repr__(self):
        return f"CP: {self.cp}\nCO: {self.co}\nEP: {self.ep}\nEO: {self.eo}"
