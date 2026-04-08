import numpy as np
from .engine import GameOfLifeEngine

class GameOfLifeVect(GameOfLifeEngine):
    def __init__(self):
        super().__init__("NumPy (Vectorized)")

    def step(self, grid):
        curr = grid.current.astype(np.int8)
        p = np.pad(curr, 1, mode='constant')
        neighbors = (p[:-2, :-2] + p[:-2, 1:-1] + p[:-2, 2:] +
                     p[1:-1, :-2]              + p[1:-1, 2:] +
                     p[2:, :-2]   + p[2:, 1:-1]  + p[2:, 2:])
        grid.next = (neighbors == 3) | ((curr == 1) & (neighbors == 2))
        grid.swap()