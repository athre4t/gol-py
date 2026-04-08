import sys
import shutil
import math

# Character used for live / dead cells. Change via `set_cell_char()` or CLI.
CELL_ON_CHAR = '#'
CELL_OFF_CHAR = ' '


def set_cell_char(ch: str):
    global CELL_ON_CHAR
    if not ch:
        return
    CELL_ON_CHAR = ch[0]


def hide_cursor():
    sys.stdout.write('\x1b[?25l')
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write('\x1b[?25h')
    sys.stdout.flush()


def move_cursor_home():
    sys.stdout.write('\x1b[H')
    sys.stdout.flush()


def clear_screen():
    sys.stdout.write('\x1b[2J')
    sys.stdout.flush()


def render_grid_str(grid):
    """Render a grid to a string that fits the current terminal size.

    If the grid is larger than the terminal, downscale by grouping blocks
    so the entire grid is visible. If it fits, render at full resolution.
    """
    cols, lines = shutil.get_terminal_size((80, 24))
    # reserve two lines for status and spacing
    max_rows = max(1, lines - 2)

    h = grid.height
    w = grid.width

    # If fits exactly, use full rendering
    if h <= max_rows and w <= cols:
        # build string row by row
        out_lines = []
        arr = grid.current
        for r in range(h):
            out_lines.append(''.join(CELL_ON_CHAR if arr[r, c] else CELL_OFF_CHAR for c in range(w)))
        return '\n'.join(out_lines)

    # Need to downscale to fit
    scale_y = math.ceil(h / max_rows)
    scale_x = math.ceil(w / cols)

    out_lines = []
    arr = grid.current
    for ro in range(0, h, scale_y):
        if len(out_lines) >= max_rows:
            break
        row_chunks = []
        for co in range(0, w, scale_x):
            block = arr[ro: min(ro + scale_y, h), co: min(co + scale_x, w)]
            ch = CELL_ON_CHAR if block.any() else CELL_OFF_CHAR
            row_chunks.append(ch)
        # ensure each output row is at most `cols` characters
        row_str = ''.join(row_chunks)[:cols]
        out_lines.append(row_str)

    return '\n'.join(out_lines)


def print_frame(grid, step, steps):
    move_cursor_home()
    out = f'Step {step}/{steps} — live cells: {grid.live_count()}\n'
    out += render_grid_str(grid)
    sys.stdout.write(out + '\n')
    sys.stdout.flush()


def print_status_line(step, steps, live_cells):
    # overwrite single status line
    status = f'Step {step}/{steps} — live cells: {live_cells}'
    sys.stdout.write('\r' + status + ' ' * 10)
    sys.stdout.flush()
