import numpy as np
from typing import Optional
import ui


class Grid:
    def __init__(self, width: int, height: int, data: Optional[np.ndarray] = None):
        self.width = int(width)
        self.height = int(height)
        if data is None:
            self.current = np.zeros((self.height, self.width), dtype=bool)
        else:
            arr = np.array(data, dtype=bool)
            if arr.shape != (self.height, self.width):
                raise ValueError("data shape does not match (height,width)")
            self.current = arr
        self.next = np.zeros_like(self.current)

    def set_cell(self, row: int, col: int, value: bool = True):
        if 0 <= row < self.height and 0 <= col < self.width:
            self.current[row, col] = bool(value)

    def get_cell(self, row: int, col: int) -> bool:
        if 0 <= row < self.height and 0 <= col < self.width:
            return bool(self.current[row, col])
        return False

    def swap(self):
        self.current, self.next = self.next, self.current
        self.next.fill(False)

    def live_count(self) -> int:
        return int(self.current.sum())

    def __str__(self) -> str:
        lines = []
        on = ui.CELL_ON_CHAR
        off = ui.CELL_OFF_CHAR
        for r in range(self.height):
            lines.append(''.join(on if c else off for c in self.current[r]))
        return '\n'.join(lines)

    def copy(self):
        return Grid(self.width, self.height, data=self.current.copy())
