import argparse
import csv
import os

from rle_parser import parse_rle
from algorithms import get_algorithm

MODES = ['sequential', 'vectorized', 'parallel', 'gpu']
CSV_FIELDS = ['Method', 'PatternName', 'ExecutionTime(ms)', 'LiveCells', 'DeadCells',
              'LiveCellPercentage', 'Threads', 'Steps']


def _run_one(mode, pattern, steps):
    """Run a single mode on a fresh grid and return a result dict, or None if unavailable."""
    grid = parse_rle(pattern)
    try:
        algo = get_algorithm(mode)
    except Exception:
        if mode == 'gpu':
            print(f'  [{mode}] GPU unavailable, skipping.')
            return None
        raise
    try:
        elapsed_ms = algo.simulate(grid, steps)
    finally:
        algo.cleanup()

    total_cells = grid.width * grid.height
    live = grid.live_count()
    dead = total_cells - live
    threads = os.cpu_count() if mode == 'parallel' else 0
    return {
        'Method': algo.name,
        'PatternName': os.path.splitext(os.path.basename(pattern))[0],
        'ExecutionTime(ms)': round(elapsed_ms, 4),
        'LiveCells': live,
        'DeadCells': dead,
        'LiveCellPercentage': round(live / total_cells * 100.0, 4),
        'Threads': threads,
        'Steps': steps,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description='Game of Life')
    parser.add_argument('--mode', nargs='?', choices=['sequential', 'vectorized', 'parallel', 'gpu'],
                        help='algorithm mode')
    parser.add_argument('steps', type=int, help='number of steps')
    parser.add_argument('pattern', nargs='?', help='path to RLE file (optional)')
    parser.add_argument('-v', '--visual', nargs='?', const=1000.0, type=float,
                        help='visualize; optional interval in milliseconds (default 1000 ms). Specify 0 for no delay')
    parser.add_argument('--cell-char', '-c', default='#', help='character to display for live cells (default "#")')
    parser.add_argument('--benchmark', '-b', action='store_true',
                        help='run all modes and write results to a CSV file')
    parser.add_argument('--output', '-o', default='benchmark.csv',
                        help='CSV output path for --benchmark (default: benchmark.csv)')
    args = parser.parse_args(argv)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    default_pattern = os.path.join(base_dir, 'patterns', 'glider.rle')
    pattern = args.pattern or default_pattern

    import ui
    ui.set_cell_char(args.cell_char)

    if args.benchmark:
        pattern_name = os.path.splitext(os.path.basename(pattern))[0]
        print(f'Benchmark: pattern={pattern_name}, steps={args.steps}')
        rows = []
        for mode in MODES:
            print(f'  Running [{mode}]...')
            row = _run_one(mode, pattern, args.steps)
            if row:
                rows.append(row)

        with open(args.output, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

        print(f'\nResults written to: {args.output}')
        print(','.join(CSV_FIELDS))
        for r in rows:
            print(','.join(str(r[field]) for field in CSV_FIELDS))
        return

    if not args.mode:
        parser.error('mode is required when not using --benchmark')

    print(f'Loading pattern: {pattern}')
    grid = parse_rle(pattern)
    print(f'Initial live cells: {grid.live_count()}')

    visual_interval = args.visual

    try:
        algo = get_algorithm(args.mode)
    except Exception:
        if args.mode == 'gpu':
            print('GPU backend not available; falling back to parallel CPU implementation.')
            algo = get_algorithm('parallel')
        else:
            raise

    try:
        algo.simulate(grid, args.steps, visual_interval=visual_interval)
    finally:
        algo.cleanup()

    print('Final live cells:', grid.live_count())
    # print(grid)


if __name__ == '__main__':
    main()
