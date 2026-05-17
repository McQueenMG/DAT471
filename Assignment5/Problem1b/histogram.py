#!/usr/bin/env python3

import argparse
from pathlib import Path

import matplotlib.pyplot as plt


def read_histogram_data(path: Path) -> tuple[list[int], float]:
	counts: list[int] = []
	expected_count = None

	with path.open("r", encoding="utf-8") as handle:
		for line in handle:
			line = line.strip()
			if (
				not line
				or line.startswith("Hash value mean")
				or line.startswith("Hash value standard deviation")
				or line.startswith("Collision probability")
			):
				continue
			if line.startswith("Hash value"):
				continue

			parts = line.split()
			if len(parts) < 3:
				continue

			count = int(parts[1])
			expected_count = float(parts[2])

			counts.append(count)

	if expected_count is None:
		raise ValueError(f"No histogram rows found in {path}")

	return counts, expected_count


def build_histogram(
	counts: list[int],
	expected_count: float,
	output_path: Path | None = None,
) -> None:
	fig, ax = plt.subplots(figsize=(10, 6))
	ax.hist(counts, bins=20, color="#3b82f6", edgecolor="white", alpha=0.9)
	ax.axvline(
		expected_count,
		color="#ef4444",
		linestyle=":",
		linewidth=2,
		label=f"Actual Cardinality ({expected_count:.0f})",
	)

	ax.set_title("Histogram of Cardinality Estimates")
	ax.set_xlabel("Estimate")
	ax.set_ylabel("Frequency")
	ax.legend()
	fig.tight_layout()

	if output_path:
		fig.savefig(output_path, dpi=200, bbox_inches="tight")
	else:
		plt.show()


def parse_args() -> argparse.Namespace:
	script_dir = Path(__file__).resolve().parent
	default_input = script_dir / "output" / "assignment5prob1b-7.out"
	default_output = script_dir / "output" / "histogram.png"

	parser = argparse.ArgumentParser(
		description="Plot a histogram of hash value counts with the expected count line"
	)
	parser.add_argument(
		"input_file",
		nargs="?",
		default=default_input,
		type=Path,
		help="Path to the evaluator output file",
	)
	parser.add_argument(
		"-o",
		"--output",
		type=Path,
		default=default_output,
		help="Save the plot to this file instead of showing it",
	)
	return parser.parse_args()


def main() -> int:
	args = parse_args()

	counts, expected_count = read_histogram_data(args.input_file)
	build_histogram(counts, expected_count, args.output)
	print(f"Saved histogram to {args.output}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
