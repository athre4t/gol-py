#!/usr/bin/env python3
"""Generate benchmark graphs for the supplementary document."""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os

matplotlib.use("Agg")

CSV_PATH = "benchmark.csv"
OUT_DIR = "report"
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH)

patterns = df["PatternName"].unique()
methods_all = df["Method"].unique()

colors_map = {
    "Pure Python (Sparse)": "#c0392b",
    "NumPy (Vectorized)": "#2980b9",
    "Parallel (Multiprocessing)": "#27ae60",
    "GPU (OpenCL)": "#8e44ad",
}

# --- 1. Execution Time (log scale) per pattern ---
for pat in patterns:
    sub = df[df["PatternName"] == pat].copy()
    methods = sub["Method"].tolist()
    times = sub["ExecutionTime(ms)"].tolist()
    colors = [colors_map.get(m, "#666") for m in methods]

    fig, ax = plt.subplots(figsize=(8, 3.5))
    bars = ax.barh(methods, times, color=colors)
    ax.set_xlabel("Execution Time (ms, log scale)")
    ax.set_title(f"Execution Time — {pat}, 1000 steps")
    ax.set_xscale("log")
    ax.invert_yaxis()
    for bar, t in zip(bars, times):
        if t > min(times) * 3:
            ax.text(t * 0.45, bar.get_y() + bar.get_height() / 2,
                    f"{t:,.1f} ms", va="center", ha="center", fontsize=9,
                    color="white", fontweight="bold")
        else:
            ax.text(t * 1.3, bar.get_y() + bar.get_height() / 2,
                    f"{t:,.1f} ms", va="center", ha="left", fontsize=9)
    plt.subplots_adjust(left=0.30, right=0.95, bottom=0.18)
    fig.savefig(os.path.join(OUT_DIR, f"exec_time_log_{pat}.png"), dpi=200)
    plt.close(fig)

# --- 2. Speedup chart for pp8primecalculator (largest) ---
pp8 = df[df["PatternName"] == "pp8primecalculator"].copy()
baseline = pp8["ExecutionTime(ms)"].iloc[0]
methods_sp = pp8["Method"].tolist()
speedups = [baseline / t for t in pp8["ExecutionTime(ms)"].tolist()]
colors_sp = [colors_map.get(m, "#999") for m in methods_sp]

fig, ax = plt.subplots(figsize=(8, 3.5))
bars = ax.barh(methods_sp, speedups, color=colors_sp)
ax.set_xlabel("Speedup (x)")
ax.set_title("Speedup vs Pure Python — pp8primecalculator, 1000 steps")
ax.invert_yaxis()
for bar, s in zip(bars, speedups):
    w = bar.get_width()
    if w > max(speedups) * 0.08:
        ax.text(w * 0.5, bar.get_y() + bar.get_height() / 2,
                f"{s:.1f}x", va="center", ha="center", fontsize=9,
                color="white", fontweight="bold")
    else:
        ax.text(w + max(speedups) * 0.02, bar.get_y() + bar.get_height() / 2,
                f"{s:.1f}x", va="center", ha="left", fontsize=9)
ax.set_xlim(0, max(speedups) * 1.05)
plt.subplots_adjust(left=0.32, right=0.95, bottom=0.18)
fig.savefig(os.path.join(OUT_DIR, "speedup.png"), dpi=200)
plt.close(fig)

# --- 3. Multi-pattern grouped bar chart (log) ---
fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(patterns))
method_list = list(colors_map.keys())
width = 0.2
for i, method in enumerate(method_list):
    vals = []
    for pat in patterns:
        row = df[(df["PatternName"] == pat) & (df["Method"] == method)]
        vals.append(row["ExecutionTime(ms)"].values[0] if len(row) > 0 else 0)
    mask = [v > 0 for v in vals]
    x_m = x[mask]
    v_m = [v for v, m in zip(vals, mask) if m]
    ax.bar(x_m + i * width, v_m, width, label=method, color=colors_map[method])

ax.set_yscale("log")
ax.set_ylabel("Execution Time (ms, log scale)")
ax.set_title("Comparison Across Patterns — 1000 steps")
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(patterns, fontsize=9)
ax.legend(fontsize=8, loc="upper left")
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "multi_pattern.png"), dpi=200)
plt.close(fig)

print(f"Graphs saved to {OUT_DIR}/")
