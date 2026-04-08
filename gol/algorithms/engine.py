import time
from ui import hide_cursor, show_cursor, print_frame

class GameOfLifeEngine:
    def __init__(self, name):
        self.name = name

    def step(self, grid):
        raise NotImplementedError

    def simulate(self, grid, steps: int, visual_interval: float = None):
        steps = int(steps)
        if visual_interval is not None:
            hide_cursor()
            print('\x1b[2J', end='')

        start_time = time.perf_counter()
        try:
            for i in range(1, steps + 1):
                self.step(grid)
                if visual_interval is not None:
                    # Sync happens here in subclasses if needed
                    self.sync_to_host(grid)
                    print_frame(grid, i, steps)
                    if visual_interval > 0:
                        time.sleep(visual_interval / 1000.0)
        finally:
            if visual_interval is not None:
                show_cursor()

        self.sync_to_host(grid) # Final sync
        total_ms = (time.perf_counter() - start_time) * 1000.0
        print(f"{self.name}: {steps} steps | Total: {total_ms:.2f}ms | Avg: {total_ms/steps:.4f}ms/step")
        return total_ms

    def sync_to_host(self, grid):
        """Optional: Overridden by GPU to pull data back to RAM."""
        pass

    def cleanup(self):
        pass