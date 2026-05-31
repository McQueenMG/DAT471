#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


METRIC_PATTERNS = {
	"load_dataset": re.compile(r"^Loading dataset .* took (?P<value>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)$"),
	"perform_nn_queries": re.compile(r"^Performing .* NN queries took (?P<value>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)$"),
	"num_erroneous": re.compile(r"^Number of erroneous queries: (?P<value>\d+)$"),
}

METRIC_LABELS = {
	"load_dataset": "Loading dataset",
	"perform_nn_queries": "Performing NN queries",
	"num_erroneous": "Number of erroneous queries",
}

QUERY_COUNTS = {
	"tiny": 10,
	"small": 100,
	"medium": 1000,
	"big": 10000,
}

FILENAME_PATTERN = re.compile(
	r"^assignment7prob4-(?P<database>.+)-(?P<batch_size>\d+)-(?P<query_size>tiny|small|medium|big)\.out$"
)


def parse_output_file(path: Path) -> Dict[str, float]:
	text = path.read_text(encoding="utf-8", errors="replace")

	metrics: Dict[str, float] = {}

	for line in text.splitlines():
		for metric_name, pattern in METRIC_PATTERNS.items():
			match = pattern.match(line.strip())
			if match:
				metrics[metric_name] = float(match.group("value"))

	return metrics


def collect_results(output_dir: Path):
	grouped = {}

	for path in sorted(output_dir.glob("assignment7prob4-*.out")):
		match = FILENAME_PATTERN.match(path.name)
		if not match:
			continue

		database = match.group("database")
		query_size = match.group("query_size")
		batch_size = int(match.group("batch_size"))

		metrics = parse_output_file(path)
		key = (database, query_size)

		if key not in grouped:
			grouped[key] = {"runs": []}

		grouped[key]["runs"].append((batch_size, metrics, path.name))

	return grouped


def best_run(runs: List[Tuple[int, Dict[str, float], str]]) -> Optional[Tuple[int, Dict[str, float], str]]:
	candidates = []
	for batch_size, metrics, filename in runs:
		if "perform_nn_queries" in metrics:
			query_time = metrics["perform_nn_queries"]
			candidates.append((batch_size, query_time, metrics, filename))

	if not candidates:
		return None

	batch_size, _, metrics, filename = min(candidates, key=lambda item: (item[1], item[0], item[3]))
	return batch_size, metrics, filename


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

			print(f"Database: {database} | Query size: {query_size}")

			if not runs:
				print("  No successful runs for this combination.")
				print()
				continue

			successful = sorted(batch for batch, _, _ in runs)
			print(f"  Successful batch sizes: {', '.join(str(b) for b in successful)}")

			best = best_run(runs)
			if best is None:
				print("  No runs with query time available.")
				print()
				continue

			batch_size, metrics, _ = best
			load_time = metrics["load_dataset"]
			query_time = metrics["perform_nn_queries"]
			total_time = load_time + query_time
			erroneous = int(metrics.get("num_erroneous", 0.0))
			query_count = QUERY_COUNTS[query_size]
			throughput = query_count / query_time if query_time else float("inf")

			print(
				f"  Best batch size: {batch_size} "
				f"(optimized for query time: {query_time:.6f} s; throughput: {throughput:.6f} queries/s; loading {load_time:.6f} s, total {total_time:.6f} s, "
				f"erroneous queries {erroneous})"
			)

			print()


def main() -> None:
	script_dir = Path(__file__).resolve().parent
	parser = argparse.ArgumentParser(
		description=(
			"Find the best batch size for each database/query-size combination "
			"from Assignment 7 Problem 4 output files."
		)
	)
	parser.add_argument(
		"--output-dir",
		type=Path,
		default=script_dir / "output",
		help="Directory containing assignment7prob4-*.out files (default: ./output)",
	)
	args = parser.parse_args()

	output_dir = args.output_dir
	if not output_dir.exists() or not output_dir.is_dir():
		raise SystemExit(f"Output directory not found or not a directory: {output_dir}")

	grouped = collect_results(output_dir)
	print_report(grouped)


if __name__ == "__main__":
	main()
