import os
import numpy as np
from multiprocessing import Process, shared_memory, Barrier, Value
from .engine import GameOfLifeEngine


def _persistent_worker(shm_in_name, shm_out_name, ph, pw, h, w,
                       r_start, r_end, barrier, steps_val):
    """Long-lived worker: loops until steps_val is set to -1."""
    shm_in = shared_memory.SharedMemory(name=shm_in_name, create=False)
    shm_out = shared_memory.SharedMemory(name=shm_out_name, create=False)
    padded = np.ndarray((ph, pw), dtype=np.int8, buffer=shm_in.buf)
    out = np.ndarray((h, w), dtype=np.bool_, buffer=shm_out.buf)

    while True:
        barrier.wait()  # wait for main to prepare input
        if steps_val.value < 0:
            break

        p = padded[r_start: r_end + 2, :]
        neighbors = (
            p[:-2, :-2] + p[:-2, 1:-1] + p[:-2, 2:] +
            p[1:-1, :-2]               + p[1:-1, 2:] +
            p[2:, :-2]  + p[2:, 1:-1]  + p[2:, 2:]
        )
        curr = p[1:-1, 1:-1]
        out[r_start: r_end, :] = (neighbors == 3) | ((curr == 1) & (neighbors == 2))

        barrier.wait()  # signal main that output is ready

    shm_in.close()
    shm_out.close()


class GameOfLifeParallel(GameOfLifeEngine):
    def __init__(self):
        super().__init__("Parallel (Multiprocessing)")
        self.workers = os.cpu_count()
        self._shm_in = None
        self._shm_out = None
        self._padded = None
        self._out = None
        self._procs = []
        self._barrier = None
        self._steps_val = None
        self._h = None
        self._w = None

    def _init_pool(self, h, w):
        ph, pw = h + 2, w + 2
        self._shm_in = shared_memory.SharedMemory(create=True, size=ph * pw)
        self._shm_out = shared_memory.SharedMemory(create=True, size=h * w)
        self._padded = np.ndarray((ph, pw), dtype=np.int8, buffer=self._shm_in.buf)
        self._padded[:] = 0
        self._out = np.ndarray((h, w), dtype=np.bool_, buffer=self._shm_out.buf)
        self._h, self._w = h, w

        indices = np.array_split(np.arange(h), self.workers)
        chunk_ranges = [(idx[0], idx[-1] + 1) for idx in indices if len(idx) > 0]
        n_workers = len(chunk_ranges)

        self._steps_val = Value('i', 0)
        self._barrier = Barrier(n_workers + 1)  # workers + main

        self._procs = []
        for r_start, r_end in chunk_ranges:
            p = Process(target=_persistent_worker, args=(
                self._shm_in.name, self._shm_out.name,
                ph, pw, h, w, r_start, r_end,
                self._barrier, self._steps_val))
            p.start()
            self._procs.append(p)

    def step(self, grid):
        h, w = grid.current.shape

        if self._shm_in is None or self._h != h or self._w != w:
            self._cleanup_all()
            self._init_pool(h, w)

        self._padded[1:-1, 1:-1] = grid.current

        self._steps_val.value = 1
        self._barrier.wait()  # release workers
        self._barrier.wait()  # wait for workers to finish

        grid.next[:] = self._out
        grid.swap()

    def _cleanup_all(self):
        if self._procs:
            self._steps_val.value = -1
            self._barrier.wait()  # release workers to exit
            for p in self._procs:
                p.join(timeout=5)
            self._procs = []
        for shm in (self._shm_in, self._shm_out):
            if shm is not None:
                shm.close()
                shm.unlink()
        self._shm_in = None
        self._shm_out = None
        self._padded = None
        self._out = None
        self._barrier = None
        self._steps_val = None

    def cleanup(self):
        self._cleanup_all()