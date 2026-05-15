#!/usr/bin/env python3

import argparse
from pathlib import Path

import matplotlib.pyplot as plt


def read_histogram_data(path):
	hash_values = []
	counts = []
	expected_count = None

	with open(path, "r", encoding="utf-8") as handle:
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

			hash_value = int(parts[0])
			count = int(parts[1])
			expected_count = float(parts[2])

			hash_values.append(hash_value)
			counts.append(count)

	if expected_count is None:
		raise ValueError(f"No histogram rows found in {path}")

	return hash_values, counts, expected_count


def plot_histogram(hash_values, counts, expected_count, output_path=None):
    plt.figure(figsize=(16, 7))
    plt.bar(
        hash_values,
        counts,
        width=0.8,
        color="#4c78a8",
        edgecolor="black",
        linewidth=0.3,
    )
    plt.axhline(
        expected_count,
        color="#e45756",
        linestyle=":",
        linewidth=2,
        label=f"Expected count ({expected_count:.0f})",
    )

    plt.xlabel("Hash value")
    plt.ylabel("Count")
    plt.title("Histogram of hash values")

    stride = max(1, len(hash_values) // 16)
    tick_positions = hash_values[::stride]
    if tick_positions[-1] != hash_values[-1]:
        tick_positions.append(hash_values[-1])
    plt.xticks(tick_positions)
    plt.ylim(bottom=0, top=4000)
    plt.margins(x=0.01)
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=200)
    else:
        plt.show()


def main():
	parser = argparse.ArgumentParser(
		description="Plot a histogram of hash values with the expected count line"
	)
	parser.add_argument("input_file", help="Path to the evaluator output file")
	parser.add_argument(
		"-o",
		"--output",
		help="Save the plot to this file instead of showing it",
	)
	args = parser.parse_args()

	hash_values, counts, expected_count = read_histogram_data(args.input_file)

	output_path = Path(args.output) if args.output else None
	plot_histogram(hash_values, counts, expected_count, output_path)


if __name__ == "__main__":
	main()
