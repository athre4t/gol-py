# Game of Life — Python (Sequential, Vectorized, Parallel, GPU)

Python implementation of Conway's Game of Life with four execution backends:

| Mode | Description |
|------|-------------|
| `sequential` | Pure Python sparse set — naive reference baseline |
| `vectorized` | NumPy-vectorized single-threaded — fast CPU path |
| `parallel` | Multi-thread row decomposition via `ThreadPoolExecutor` |
| `gpu` | OpenCL kernel (byte-per-cell) via PyOpenCL |

---

## Requirements

- Python 3.11+
- NumPy
- PyOpenCL

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

Measured on **AMD Phoenix3** (16-core CPU, OpenCL via Mesa rusticl),
pattern: `pp8primecalculator` (~2.5 M cells), **1 000 steps**.

| Method | ExecutionTime (ms) | Avg ms/step | LiveCells | LiveCell % | Threads |
|---------------------------|------------------:|------------:|----------:|-----------:|--------:|
| Pure Python (Sparse) | 77 687.9 | 77.69 | 12 032 | 0.476 % | 1 |
| NumPy (Vectorized) | 4 236.9 | 4.24 | 12 032 | 0.476 % | 1 |
| Parallel (Multithreading) | 2 337.0 | 2.34 | 12 032 | 0.476 % | 16 |
| GPU (OpenCL) | 313.5 | 0.31 | 12 032 | 0.476 % | — |

**Speedup over pure Python baseline:**

| Method | Speedup |
|---------------------------|--------:|
| NumPy (Vectorized) | ~18x |
| Parallel (Multithreading) | ~33x |
| GPU (OpenCL) | ~248x |

---

## Patterns

Built-in RLE patterns included in `patterns/`:

| File | Description |
|------|-------------|
| `glider.rle` | Classic 5-cell glider |
| `gosper_glider_gun.rle` | Infinite glider factory |
| `pulsar.rle` | Period-3 oscillator |
| `caterpillar.rle` | Large, fast spaceship |
| `diehard2500.rle` | Pattern that survives exactly 2500 generations |
| `rpentominoequivalents.rle` | R-pentomino variant |
| `pp8primecalculator.rle` | Large prime-sieve pattern (~2.5 M cells) |

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
│       ├── parallel.py         # ThreadPoolExecutor row decomposition
│       └── gpu.py              # PyOpenCL backend
├── patterns/                   # Bundled RLE pattern files
├── benchmark.csv               # Latest benchmark results
└── requirements.txt
```