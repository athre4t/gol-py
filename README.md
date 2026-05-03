# Game of Life — Python (Sequential, Vectorized, Parallel, GPU)

Python implementation of Conway's Game of Life with four execution backends:

| Mode | Description |
|------|-------------|
| `sequential` | Pure Python sparse set — naive reference baseline |
| `vectorized` | NumPy-vectorized single-threaded — fast CPU path |
| `parallel` | Multiprocessing with shared memory — bypasses GIL |
| `gpu` | OpenCL kernel (byte-per-cell) via PyOpenCL |

---

## Requirements

- Python 3.11+
- NumPy
- PyOpenCL
- MatPlotLib
- OpenCL

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python gol/cli.py [--mode MODE] <steps> [pattern] [options]
```

### Positional arguments

| Argument | Description |
|----------|-------------|
| `steps` | Number of simulation steps to run |
| `pattern` | Path to an `.rle` file (defaults to `patterns/glider.rle`) |

### Options

| Flag | Description |
|------|-------------|
| `--mode MODE` | Algorithm: `sequential`, `vectorized`, `parallel`, `gpu` |
| `-v [MS]`, `--visual [MS]` | Live terminal visualisation; optional delay in ms (default 1000 ms, `0` = no delay) |
| `-c CHAR`, `--cell-char CHAR` | Character for live cells (default `#`) |
| `-b`, `--benchmark` | Run all modes and write a CSV results file |
| `-r N`, `--repeats N` | Number of repeats per mode in benchmark (default 1) |
| `-o FILE`, `--output FILE` | CSV output path for `--benchmark` (default `benchmark.csv`) |

### Examples

```bash
# Run vectorized mode, 500 steps, default glider pattern
python gol/cli.py --mode vectorized 500

# Run parallel mode with live visualisation (200 ms between frames)
python gol/cli.py --mode parallel 200 patterns/gosper_glider_gun.rle -v 200

# Benchmark all modes, 10 000 steps, write to results.csv
python gol/cli.py --benchmark 10000 patterns/pp8primecalculator.rle -o results.csv
```

---

## Benchmark

Measured on **AMD Phoenix3** (16-core CPU, OpenCL via Mesa rusticl).

### otcametapixel (4116×4116, ~16.9 M cells), 100 steps

| Method | ExecutionTime (ms) | Avg ms/step | Speedup |
|---------------------------|------------------:|------------:|--------:|
| Pure Python (Sparse) | 63 303 | 633.03 | 1x |
| NumPy (Vectorized) | 2 158 | 21.58 | ~29x |
| Parallel (Multiprocessing) | 1 286 | 12.85 | ~49x |
| GPU (OpenCL) | 207 | 2.07 | ~306x |

### pp8primecalculator (2044×1236, ~2.5 M cells), 1 000 steps

| Method | ExecutionTime (ms) | Avg ms/step | Speedup |
|---------------------------|------------------:|------------:|--------:|
| Pure Python (Sparse) | 74 843 | 74.84 | 1x |
| NumPy (Vectorized) | 4 200 | 4.20 | ~18x |
| Parallel (Multiprocessing) | 1 841 | 1.84 | ~41x |
| GPU (OpenCL) | 334 | 0.33 | ~224x |

### breeder1 (1498×676, ~1 M cells), 1 000 steps

| Method | ExecutionTime (ms) | Avg ms/step | Speedup |
|---------------------------|------------------:|------------:|--------:|
| Pure Python (Sparse) | 30 310 | 30.31 | 1x |
| NumPy (Vectorized) | 616 | 0.62 | ~49x |
| Parallel (Multiprocessing) | 539 | 0.54 | ~56x |
| GPU (OpenCL) | 141 | 0.14 | ~215x |

---

## Patterns

Built-in RLE patterns included in `patterns/`:

| File | Description |
|------|-------------|
| `glider.rle` | Classic 5-cell glider |
| `gosper_glider_gun.rle` | Infinite glider factory |
| `pulsar.rle` | Period-3 oscillator |
| `diehard2500.rle` | Pattern that survives exactly 2500 generations |
| `rpentominoequivalents.rle` | R-pentomino variant |
| `breeder1.rle` | Quadratic growth breeder (749×338, grid 1498×676) |
| `pp8primecalculator.rle` | Large prime-sieve pattern (1022×618, grid 2044×1236) |
| `otcametapixel.rle` | OTCA metapixel (2058×2058, grid 4116×4116) |

---

## Project Structure

```
gol-py/
├── gol/
│   ├── cli.py                  # Entry point & benchmark runner
│   ├── grid.py                 # Grid data structure (NumPy-backed)
│   ├── rle_parser.py           # RLE file parser
│   ├── ui.py                   # Terminal rendering helpers
│   ├── kernels/
│   │   └── gameOfLife.cl       # OpenCL kernel (byte-per-cell)
│   └── algorithms/
│       ├── engine.py           # Base class with unified simulate loop
│       ├── sequential.py       # Pure Python loops
│       ├── vectorized.py       # NumPy vectorized
│       ├── parallel.py         # Multiprocessing + shared_memory
│       └── gpu.py              # PyOpenCL backend
├── patterns/                   # Bundled RLE pattern files
├── benchmark.csv               # Latest benchmark results
├── generate_graphs.py          # Benchmark graph generator (matplotlib)
├── report/                     # LaTeX report with compiled PDF
└── requirements.txt
```