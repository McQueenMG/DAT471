from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


WORKER_RE = re.compile(r"num_workers\s*=\s*(\d+)")
TOTAL_TIME_RE = re.compile(r"Total execution time:\s*([0-9]+(?:\.[0-9]+)?)")


def parse_result_file(file_path: Path) -> tuple[int, float] | None:
    """Return (num_workers, total_execution_time_seconds) for one result file."""
    text = file_path.read_text(encoding="utf-8", errors="replace")

    worker_match = WORKER_RE.search(text)
    total_time_match = TOTAL_TIME_RE.search(text)

    if worker_match is None or total_time_match is None:
        return None

    workers = int(worker_match.group(1))
    total_time = float(total_time_match.group(1))
    return workers, total_time


def parse_total_time(file_path: Path) -> float | None:
    """Return the total execution time from a sequential or parallel result file."""
    text = file_path.read_text(encoding="utf-8", errors="replace")
    total_time_match = TOTAL_TIME_RE.search(text)
    if total_time_match is None:
        return None
    return float(total_time_match.group(1))


def collect_results(results_dir: Path, pattern: str) -> list[tuple[int, float]]:
    parsed: list[tuple[int, float]] = []
    for file_path in sorted(results_dir.glob(pattern)):
        print(f"Parsing file: {file_path}")
        if not file_path.is_file():
            continue
        result = parse_result_file(file_path)
        if result is not None:
            parsed.append(result)
    return parsed


def compute_speedup(
    results: list[tuple[int, float]], baseline_time: float
) -> list[tuple[int, float, float]]:
    if not results:
        return []

    # Keep the fastest run if there are duplicate worker counts.
    best_time_by_workers: dict[int, float] = {}
    for workers, total_time in results:
        previous = best_time_by_workers.get(workers)
        if previous is None or total_time < previous:
            best_time_by_workers[workers] = total_time

    speedups: list[tuple[int, float, float]] = []
    for workers in sorted(best_time_by_workers):
        total_time = best_time_by_workers[workers]
        speedup = baseline_time / total_time
        speedups.append((workers, total_time, speedup))
    return speedups


def plot_speedup(speedup_data: list[tuple[int, float, float]], output_path: Path | None) -> None:
    workers = [row[0] for row in speedup_data]
    measured_speedup = [row[2] for row in speedup_data]
    ideal_speedup = [2.63] * len(workers)

    plt.figure(figsize=(9, 5.5))
    plt.plot(workers, measured_speedup, marker="o", linewidth=2, label="Measured speedup")
    plt.plot(workers, ideal_speedup, linestyle="--", linewidth=1.8, label="Ideal speedup")

    plt.title("Speedup vs Number of Workers")
    plt.xlabel("Number of workers")
    plt.ylabel("Speedup (T1 / Tp)")
    plt.xscale("log", base=2)
    plt.xticks(2 ** np.arange(0, 7))  
    plt.yticks(np.arange(0, 3.01, 0.2))
    plt.xlim(0.95, 68)    
    plt.margins(x=0)    
    plt.grid(True, linestyle=":", linewidth=0.7)
    plt.legend()
    plt.tight_layout()

    if output_path is not None:
        plt.savefig(output_path, dpi=150)
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot speedup from assignment output files.")
    parser.add_argument(
        "--results-dir",
        default=Path(__file__).parent / "output",
        type=Path,
        help="Directory containing result .out/.txt files (default: Assignment2/output).",
    )
    parser.add_argument(
        "--pattern",
        default="assignment2d-*.out",
        help="Glob pattern used to pick result files (default: assignment2d-*.out).",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Path to save the figure (e.g. speedup.png). If omitted, the plot is shown.",
    )
    parser.add_argument(
        "--baseline-file",
        type=Path,
        default=Path(__file__).parent / "output" / "assignment2c-huge.out",
        help=(
            "Path to the sequential baseline result file (default: "
            "Assignment2/output/assignment2c-huge.out)."
        ),
    )
    args = parser.parse_args()

    results = collect_results(args.results_dir, args.pattern)
    baseline_time = parse_total_time(args.baseline_file)

    if baseline_time is None:
        raise ValueError(
            f"Could not parse a total execution time from baseline file '{args.baseline_file}'."
        )

    print(f"Found {len(results)} parseable result files in '{args.results_dir}' matching pattern '{args.pattern}'.")
    speedup_data = compute_speedup(results, baseline_time)

    if not speedup_data:
        raise ValueError(
            f"No parseable files found in '{args.results_dir}' matching pattern '{args.pattern}'."
        )

    print(f"Sequential baseline: {baseline_time:.2f}s from {args.baseline_file}")
    print("Parsed runs:")
    for workers, total_time, speedup in speedup_data:
        print(f"workers={workers:>3}, time={total_time:>9.2f}s, speedup={speedup:>6.3f}")

    plot_speedup(speedup_data, args.save)


if __name__ == "__main__":
    main()


