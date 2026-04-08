import numpy as np
from .engine import GameOfLifeEngine


class GameOfLifePure(GameOfLifeEngine):
    def __init__(self):
        super().__init__("Pure Python (Sparse)")

    def step(self, grid):
        h, w = grid.current.shape

        # Collect live cell coordinates with a single NumPy call, then work
        # in pure Python from here.  For sparse patterns this reduces the
        # per-step work from O(total_cells) to O(live_cells).
        live_coords = np.argwhere(grid.current)
        live_set = {(int(r), int(c)) for r, c in live_coords}

        # Build the candidate set: every live cell plus all its neighbours.
        # Only candidates can change state this step.
        candidates = set()
        for (r, c) in live_set:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w:
                        candidates.add((nr, nc))

        # Evaluate Conway rules for each candidate
        new_live = set()
        for (r, c) in candidates:
            n = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    if (r + dr, c + dc) in live_set:
                        n += 1
            if (r, c) in live_set:
                if n == 2 or n == 3:
                    new_live.add((r, c))
            else:
                if n == 3:
                    new_live.add((r, c))

        grid.next.fill(False)
        for (r, c) in new_live:
            grid.next[r, c] = True
        grid.swap()
