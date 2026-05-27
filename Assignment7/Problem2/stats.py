#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


METRIC_PATTERNS = {
	"load_dataset_cpu": re.compile(r"^Loading dataset .* took (?P<value>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)$"),
	"transfer_dataset_gpu": re.compile(r"^Transferring dataset to the GPU took (?P<value>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)$"),
	"load_queries_cpu": re.compile(r"^Loading queries .* took (?P<value>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)$"),
	"transfer_queries_gpu": re.compile(r"^Transferring queries to the GPU took (?P<value>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)$"),
	"perform_nn_queries": re.compile(r"^Performing .* NN queries took (?P<value>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)$"),
	"transfer_results_cpu": re.compile(r"^Transferring results to the CPU took (?P<value>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)$"),
}

METRIC_LABELS = {
	"load_dataset_cpu": "Loading dataset to CPU",
	"transfer_dataset_gpu": "Transferring dataset to GPU",
	"load_queries_cpu": "Loading queries to CPU",
	"transfer_queries_gpu": "Transferring queries to GPU",
	"perform_nn_queries": "Performing NN queries",
	"transfer_results_cpu": "Transferring results to CPU",
}

FILENAME_PATTERN = re.compile(
	r"^assignment7prob2-(?P<database>.+)-(?P<batch_size>\d+)-(?P<query_size>tiny|small|medium|big)\.out$"
)


def parse_output_file(path: Path) -> Tuple[bool, Dict[str, float]]:
	text = path.read_text(encoding="utf-8", errors="replace")
	is_dnf = "outofmemoryerror" in text.lower() or "out of memory" in text.lower()

	metrics: Dict[str, float] = {}
	if is_dnf:
		return True, metrics

	for line in text.splitlines():
		for metric_name, pattern in METRIC_PATTERNS.items():
			match = pattern.match(line.strip())
			if match:
				metrics[metric_name] = float(match.group("value"))

	return False, metrics


def collect_results(output_dir: Path):
	grouped = {}

	for path in sorted(output_dir.glob("assignment7prob2-*.out")):
		match = FILENAME_PATTERN.match(path.name)
		if not match:
			continue

		database = match.group("database")
		query_size = match.group("query_size")
		batch_size = int(match.group("batch_size"))

		is_dnf, metrics = parse_output_file(path)
		key = (database, query_size)

		if key not in grouped:
			grouped[key] = {"runs": [], "dnf": []}

		if is_dnf:
			grouped[key]["dnf"].append(batch_size)
		else:
			grouped[key]["runs"].append((batch_size, metrics, path.name))

	return grouped


def best_for_metric(runs: List[Tuple[int, Dict[str, float], str]], metric_name: str) -> Optional[Tuple[int, float, str]]:
	candidates = []
	for batch_size, metrics, filename in runs:
		if metric_name in metrics:
			candidates.append((batch_size, metrics[metric_name], filename))

	if not candidates:
		return None

	return min(candidates, key=lambda item: item[1])


def print_report(grouped):
	if not grouped:
		print("No matching output files found.")
		return

	databases = sorted({db for db, _ in grouped.keys()})
	query_sizes = ["tiny", "small", "medium", "big"]

	for database in databases:
		for query_size in query_sizes:
			key = (database, query_size)
			if key not in grouped:
				continue

			runs = grouped[key]["runs"]
			dnf_batches = sorted(grouped[key]["dnf"])

			print(f"Database: {database} | Query size: {query_size}")

			if dnf_batches:
				joined = ", ".join(str(b) for b in dnf_batches)
				print(f"  DNF batch sizes (OOM): {joined}")

			if not runs:
				print("  No successful runs for this combination.")
				print()
				continue

			successful = sorted(batch for batch, _, _ in runs)
			print(f"  Successful batch sizes: {', '.join(str(b) for b in successful)}")

			for metric_name in METRIC_PATTERNS.keys():
				best = best_for_metric(runs, metric_name)
				if best is None:
					print(f"  - {METRIC_LABELS[metric_name]}: no data")
				else:
					batch_size, seconds, _ = best
					print(
						f"  - {METRIC_LABELS[metric_name]}: best batch size = {batch_size} "
						f"({seconds:.6f} s)"
					)

			print()


def main() -> None:
	script_dir = Path(__file__).resolve().parent
	parser = argparse.ArgumentParser(
		description=(
			"Find best batch size per timing metric for each database/query-size "
			"combination from Assignment 7 Problem 2 output files."
		)
	)
	parser.add_argument(
		"--output-dir",
		type=Path,
		default=script_dir / "output",
		help="Directory containing assignment7prob2-*.out files (default: ./output)",
	)
	args = parser.parse_args()

	output_dir = args.output_dir
	if not output_dir.exists() or not output_dir.is_dir():
		raise SystemExit(f"Output directory not found or not a directory: {output_dir}")

	grouped = collect_results(output_dir)
	print_report(grouped)


if __name__ == "__main__":
	main()
