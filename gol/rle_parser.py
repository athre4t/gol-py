import re
import os

from grid import Grid

MAX_DIMENSION = 10000


def parse_rle(path: str) -> Grid:
    """Parse an RLE file and return a centered Grid."""
    with open(path, 'r') as fh:
        lines = [ln.rstrip('\n') for ln in fh]

    header_line = ''
    body_lines = []
    for ln in lines:
        if ln.strip().startswith('#'):
            continue
        if 'x' in ln and 'y' in ln and '=' in ln and header_line == '':
            header_line = ln
            continue
        body_lines.append(ln.strip())

    if not header_line:
        raise ValueError('RLE header (x = ..., y = ...) not found')

    m = re.search(r'x\s*=\s*(\d+)\s*,\s*y\s*=\s*(\d+)', header_line)
    if not m:
        raise ValueError('Could not parse dimensions from RLE header')

    width = int(m.group(1))
    height = int(m.group(2))

    if width <= 0 or height <= 0:
        raise ValueError('Invalid pattern dimensions')

    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        width = min(width, MAX_DIMENSION)
        height = min(height, MAX_DIMENSION)

    # Build the compact RLE string
    rle_str = ''.join(body_lines)
    # Remove any 'rule=' parts if present
    rle_str = re.sub(r'\s*rule\s*=\s*[^,;]*', '', rle_str)

    padded_w = min(max(width * 2, 100), MAX_DIMENSION)
    padded_h = min(max(height * 2, 100), MAX_DIMENSION)

    grid = Grid(padded_w, padded_h)

    offset_x = (padded_w - width) // 2
    offset_y = (padded_h - height) // 2

    row = 0
    col = 0
    count = 0
    i = 0
    while i < len(rle_str):
        c = rle_str[i]
        if c.isdigit():
            count = count * 10 + int(c)
        elif c == 'b':
            step = count if count > 0 else 1
            col += step
            count = 0
        elif c == 'o':
            step = count if count > 0 else 1
            for k in range(step):
                r = offset_y + row
                cc = offset_x + col + k
                if 0 <= r < padded_h and 0 <= cc < padded_w:
                    grid.set_cell(r, cc, True)
            col += step
            count = 0
        elif c == '$':
            step = count if count > 0 else 1
            row += step
            col = 0
            count = 0
            if offset_y + row >= padded_h:
                break
        elif c == '!':
            break
        # ignore other characters (whitespace etc.)
        i += 1

    return grid


if __name__ == '__main__':
    # simple CLI for testing
    import sys
    if len(sys.argv) < 2:
        print('Usage: python rle_parser.py path/to/pattern.rle')
    else:
        g = parse_rle(sys.argv[1])
        print('Loaded grid:', g.live_count(), 'live cells')
