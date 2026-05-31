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

QUERY_COUNTS = {
	"tiny": 10,
	"small": 100,
	"medium": 1000,
	"big": 10000,
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

			best = best_run(runs)
			if best is None:
				print("  No runs with query time available.")
				print()
				continue

			batch_size, metrics, _ = best
			load_dataset = metrics.get("load_dataset_cpu")
			transfer_dataset = metrics.get("transfer_dataset_gpu")
			load_queries = metrics.get("load_queries_cpu")
			transfer_queries = metrics.get("transfer_queries_gpu")
			query_time = metrics["perform_nn_queries"]
			transfer_results = metrics.get("transfer_results_cpu")
			query_count = QUERY_COUNTS[query_size]
			throughput = query_count / query_time if query_time else float("inf")

			total_time = 0.0
			for key in METRIC_PATTERNS.keys():
				if key in metrics:
					total_time += metrics[key]

			parts = [
				f"optimized for query time: {query_time:.6f} s",
				f"throughput: {throughput:.6f} queries/s",
			]
			if load_dataset is not None:
				parts.append(f"load dataset {load_dataset:.6f} s")
			if transfer_dataset is not None:
				parts.append(f"transfer dataset {transfer_dataset:.6f} s")
			if load_queries is not None:
				parts.append(f"load queries {load_queries:.6f} s")
			if transfer_queries is not None:
				parts.append(f"transfer queries {transfer_queries:.6f} s")
			if transfer_results is not None:
				parts.append(f"transfer results {transfer_results:.6f} s")
			parts.append(f"total {total_time:.6f} s")

			print(f"  Best batch size: {batch_size} ({'; '.join(parts)})")

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
