#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt


TIME_PATTERN = re.compile(r"Took\s+([0-9]*\.?[0-9]+)\s+s")
WORKER_PATTERN = re.compile(r"Number of workers:\s+(\d+)")


def read_result_file(path: Path) -> tuple[int, float]:
	workers = None
	elapsed_time = None

	with path.open("r", encoding="utf-8") as handle:
		for line in handle:
			if workers is None:
				worker_match = WORKER_PATTERN.search(line)
				if worker_match:
					workers = int(worker_match.group(1))

			if elapsed_time is None:
				time_match = TIME_PATTERN.search(line)
				if time_match:
					elapsed_time = float(time_match.group(1))

	if workers is None or elapsed_time is None:
		raise ValueError(f"Could not parse workers/time from {path}")

	return workers, elapsed_time


def collect_results(output_dir: Path, pattern: str) -> list[tuple[int, float]]:
	results: list[tuple[int, float]] = []
	for path in output_dir.glob(pattern):
		results.append(read_result_file(path))

	if not results:
		raise ValueError(f"No result files matched {pattern} in {output_dir}")

	results.sort(key=lambda item: item[0])
	return results


def build_speedup_graph(results: list[tuple[int, float]], output_path: Path | None = None) -> None:
	workers = [item[0] for item in results]
	times = [item[1] for item in results]
	baseline = times[workers.index(1)]
	speedups = [baseline / elapsed_time for elapsed_time in times]

	fig, ax = plt.subplots(figsize=(10, 6))
	ax.plot(workers, speedups, marker="o", linewidth=2.5, color="#3b82f6", label="Observed speedup")
	ax.set_xscale("log", base=2)

	ax.set_title("Speedup plot of Problem 3c")
	ax.set_xlabel("Workers")
	ax.set_ylabel("Speedup")
	ax.set_xticks(workers)
	ax.set_ylim(bottom=0)
	ax.grid(True, axis="both", linestyle="--", alpha=0.3)
	ax.legend()
	fig.tight_layout()

	if output_path:
		fig.savefig(output_path, dpi=200, bbox_inches="tight")
	else:
		plt.show()


def parse_args() -> argparse.Namespace:
	script_dir = Path(__file__).resolve().parent
	default_output = script_dir / "output" / "assignment5prob3_speedup.png"

	parser = argparse.ArgumentParser(
		description="Speedup plot of Problem 3c"
	)
	parser.add_argument(
		"-o",
		"--output",
		type=Path,
		default=default_output,
		help="Save the plot to this file instead of showing it",
	)
	parser.add_argument(
		"--input-dir",
		type=Path,
		default=script_dir / "output",
		help="Directory containing assignment5prob3-big-*.out files",
	)
	parser.add_argument(
		"--pattern",
		type=str,
		default="assignment5prob3-big-*.out",
		help="Filename pattern for result files",
	)
	return parser.parse_args()


def main() -> int:
	args = parse_args()
	results = collect_results(args.input_dir, args.pattern)
	build_speedup_graph(results, args.output)
	print(f"Saved speedup graph to {args.output}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
