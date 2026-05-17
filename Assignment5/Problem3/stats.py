#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from statistics import fmean, pstdev


ACTUAL_CARDINALITY = 284689


def read_estimates(csv_path: Path) -> tuple[list[float], int]:
	estimates: list[float] = []
	m_value = None

	with csv_path.open(newline="", encoding="utf-8") as csv_file:
		reader = csv.DictReader(csv_file)
		for row in reader:
			if not row:
				continue

			estimates.append(float(row["estimate"]))
			if m_value is None and row.get("m"):
				m_value = int(row["m"])

	if not estimates:
		raise ValueError(f"No estimates found in {csv_path}")

	if m_value is None:
		raise ValueError(f"Could not determine m from {csv_path}")

	return estimates, m_value


def coverage_fraction(estimates: list[float], lower: float, upper: float) -> float:
	count = sum(lower <= estimate <= upper for estimate in estimates)
	return count / len(estimates)


def parse_args() -> argparse.Namespace:
	script_dir = Path(__file__).resolve().parent
	default_csv = script_dir / "output" / "assignment5_problem3c_results.csv"

	parser = argparse.ArgumentParser(
		description="Print summary statistics for the Assignment 5 Problem 3 estimates"
	)
	parser.add_argument(
		"--csv",
		type=Path,
		default=default_csv,
		help="Path to the CSV file with estimates",
	)
	return parser.parse_args()


def main() -> int:
	args = parse_args()
	estimates, m_value = read_estimates(args.csv)
	mean_estimate = fmean(estimates)
	std_dev_estimate = pstdev(estimates)
	sigma = 1.04 / math.sqrt(m_value)

	print(f"Actual cardinality: {ACTUAL_CARDINALITY}")
	print(f"Average estimate: {mean_estimate:.6f}")
	print(f"Standard deviation of estimates: {std_dev_estimate:.6f}")
	print(f"Using m = {m_value}, sigma = {sigma:.8f}")

	for k in (1, 2, 3):
		lower = ACTUAL_CARDINALITY * (1 - k * sigma)
		upper = ACTUAL_CARDINALITY * (1 + k * sigma)
		fraction = coverage_fraction(estimates, lower, upper)
		print(
			f"Fraction within n(1 +- {k}*sigma): {fraction:.6f} "
			f"[{lower:.3f}, {upper:.3f}]"
		)

	return 0


if __name__ == "__main__":
	raise SystemExit(main())
