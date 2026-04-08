import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from .engine import GameOfLifeEngine

class GameOfLifeParallel(GameOfLifeEngine):
    def __init__(self):
        super().__init__("Parallel (Multithreading)")
        self.workers = os.cpu_count()
        self.executor = ThreadPoolExecutor(max_workers=self.workers)

    @staticmethod
    def _process_chunk(chunk_with_padding):
        """Standard vectorized logic on a horizontal slice"""
        p = chunk_with_padding.astype(np.int8)
        neighbors = (
            p[:-2, :-2] + p[:-2, 1:-1] + p[:-2, 2:] +
            p[1:-1, :-2]               + p[1:-1, 2:] +
            p[2:, :-2]  + p[2:, 1:-1]  + p[2:, 2:]
        )
        curr = p[1:-1, 1:-1]
        return (neighbors == 3) | ((curr == 1) & (neighbors == 2))

    def step(self, grid):
        h, w = grid.current.shape
        # Pad globally so workers don't have to worry about edges
        padded_full = np.pad(grid.current, ((1, 1), (1, 1)), mode='constant')
        
        # Split row indices into N parts for N workers
        chunk_indices = np.array_split(np.arange(h), self.workers)
        
        futures = []
        for idx_range in chunk_indices:
            if len(idx_range) == 0: continue
            r_start, r_end = idx_range[0], idx_range[-1]
            
            # Slice: [start_row : end_row + padding]
            # Since pad adds 1 row at top, r_start maps to r_start in pad.
            # We need 3 rows of context for each chunk (top neighbor, self, bottom neighbor)
            chunk = padded_full[r_start : r_end + 3, :]
            futures.append(self.executor.submit(self._process_chunk, chunk))

        # Reassemble the chunks into the full grid
        results = [f.result() for f in futures]
        grid.next = np.vstack(results)
        grid.swap()

    def cleanup(self):
        self.executor.shutdown(wait=False)