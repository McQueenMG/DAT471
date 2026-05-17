#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


ACTUAL_CARDINALITY = 284689


def read_estimates(csv_path: Path) -> list[float]:
	estimates: list[float] = []
	with csv_path.open(newline="", encoding="utf-8") as csv_file:
		reader = csv.DictReader(csv_file)
		for row in reader:
			if not row:
				continue
			estimates.append(float(row["estimate"]))
	return estimates


def build_histogram(estimates: list[float], actual_cardinality: float, output_path: Path) -> None:
	fig, ax = plt.subplots(figsize=(10, 6))
	ax.hist(estimates, bins=20, color="#3b82f6", edgecolor="white", alpha=0.9)
	ax.axvline(
		actual_cardinality,
		color="#ef4444",
		linestyle=":",
		linewidth=2,
		label=f"Actual cardinality ({actual_cardinality:.0f})",
	)

	ax.set_title("Histogram of Cardinality Estimates")
	ax.set_xlabel("Estimate")
	ax.set_ylabel("Frequency")
	ax.legend()
	fig.tight_layout()
	fig.savefig(output_path, dpi=200, bbox_inches="tight")


def parse_args() -> argparse.Namespace:
	script_dir = Path(__file__).resolve().parent
	default_csv = script_dir / "output" / "assignment5_problem3c_results.csv"
	default_output = script_dir / "output" / "assignment5_problem3c_histogram.png"

	parser = argparse.ArgumentParser(
		description="Plot a histogram of cardinality estimates and mark the actual cardinality."
	)
	parser.add_argument("--csv", type=Path, default=default_csv, help="Path to the CSV file with estimates")
	parser.add_argument(
		"--output",
		type=Path,
		default=default_output,
		help="Path where the histogram image will be saved",
	)
	parser.add_argument(
		"--actual-cardinality",
		type=float,
		default=ACTUAL_CARDINALITY,
		help="Actual cardinality to mark on the plot",
	)
	return parser.parse_args()


def main() -> int:
	args = parse_args()
	estimates = read_estimates(args.csv)

	if not estimates:
		raise ValueError(f"No estimates found in {args.csv}")

	args.output.parent.mkdir(parents=True, exist_ok=True)
	build_histogram(estimates, args.actual_cardinality, args.output)
	print(f"Saved histogram to {args.output}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
