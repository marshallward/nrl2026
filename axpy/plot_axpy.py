#!/usr/bin/env python3
import argparse
from pathlib import Path

from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import yaml


AXPY_BYTES_PER_FLOP = 12

CPU_DDR5_CHANNELS = 12
CPU_DDR5_GB_PER_S_PER_CHANNEL = 38.4
CPU_BANDWIDTH_ROOF = round(CPU_DDR5_CHANNELS * CPU_DDR5_GB_PER_S_PER_CHANNEL / AXPY_BYTES_PER_FLOP)
CPU_CORES = 96
CPU_FP64_FLOP_PER_CYCLE_PER_CORE = 16
CPU_CLOCK_GHZ = 3.0
CPU_COMPUTE_PEAK = round(CPU_CORES * CPU_FP64_FLOP_PER_CYCLE_PER_CORE * CPU_CLOCK_GHZ)

GPU_HBM_GB_PER_S = 4000
GPU_BANDWIDTH_ROOF = round(GPU_HBM_GB_PER_S / AXPY_BYTES_PER_FLOP)
GPU_FP64_CUDA_CORE_PEAK = 33500

FILES = [
    ("cpu_axpy_v2.txt", "y[:] = a x[:] + y[:]", "CPU (Genoa 96-core)", 96, "tab:blue", "tab:blue", CPU_BANDWIDTH_ROOF, CPU_COMPUTE_PEAK),
    ("gpu_axpy.txt", "GPU (BLAS): y[:] = a * x[:] + y[:]", "GPU (GH200)", 1, "tab:orange", "darkorange", GPU_BANDWIDTH_ROOF, GPU_FP64_CUDA_CORE_PEAK),
]


def load_flops(path, result_name, size_scale):
    with path.open() as f:
        data = yaml.safe_load(f)

    points = []
    for entry in data.get("roof", []) or []:
        size = entry.get("len")
        results = entry.get("results") or []
        for result in results:
            if result.get("name") != result_name:
                continue
            flop = result.get("flop")
            if size and flop and size > 0 and flop > 0:
                points.append((size * size_scale, flop / 1e9))

    points.sort()
    if not points:
        return [], []
    return zip(*points)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dark", action="store_true", help="Use transparent background with white lettering")
    args = parser.parse_args()

    fig, ax = plt.subplots(figsize=(7.0, 4.6), constrained_layout=True)
    legend_handles = []

    max_peak = max(row[-1] for row in FILES)

    for filename, result_name, label, size_scale, color, text_color, roof, peak in FILES:
        path = Path(filename)
        sizes, gflops = load_flops(path, result_name, size_scale)
        ax.scatter(sizes, gflops, s=2, alpha=0.65, color=color)
        legend_handles.append(Line2D([0], [0], color=color, linewidth=2.5, label=label))
        ax.axhline(roof, color=color, linestyle="--", linewidth=1.4)
        ax.axhline(peak, color=color, linestyle="-", linewidth=1.4)
        ax.text(
            0.03,
            roof * 1.08,
            f"{roof} GF/s",
            color=text_color,
            transform=ax.get_yaxis_transform(),
            ha="left",
            va="bottom",
            clip_on=False,
        )
        ax.text(
            0.03,
            peak * 1.08,
            f"{peak / 1000:.1f} TF/s",
            color=text_color,
            transform=ax.get_yaxis_transform(),
            ha="left",
            va="bottom",
            clip_on=False,
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(top=max_peak * 3.0)
    ax.set_xlabel("Total array length")
    ax.set_ylabel("Performance (GFLOP/s)")
    ax.set_title("y = ax + y performance")
    ax.grid(False)
    legend = ax.legend(handles=legend_handles, frameon=True, framealpha=1.0)

    if args.dark:
        fig.patch.set_alpha(0)
        ax.patch.set_facecolor("white")
        ax.patch.set_alpha(1)
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
        ax.tick_params(axis="both", which="both", colors="white")
        legend.get_frame().set_facecolor("white")
        legend.get_frame().set_alpha(1)
        legend.get_frame().set_edgecolor("0.8")
        for text in legend.get_texts():
            text.set_color("black")

    fig.savefig("axpy_flops.png", dpi=300)
    fig.savefig("axpy_flops.pdf")
    fig.savefig("axpy_flops.svg")


if __name__ == "__main__":
    main()
