#!/usr/bin/env bash

set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
template_script="${script_dir}/assignment7_problem2.sh"

batch_sizes=(1 2 4 8 16 32 64)
query_sizes=(tiny small medium big)

declare -A data_paths=(
	[pubs]="/data/courses/2026_dat471_dit066/datasets/pubs/pubs.csv"
	[glove6b]="/data/courses/2026_dat471_dit066/datasets/glove/glove.6B.50d.txt"
	[glove840b]="/data/courses/2026_dat471_dit066/datasets/glove/glove.840B.300d.txt"
)

declare -A query_prefixes=(
	[pubs]="/data/courses/2026_dat471_dit066/datasets/pubs/pub_queries"
	[glove6b]="/data/courses/2026_dat471_dit066/datasets/glove/glove.6B.50d_queries"
	[glove840b]="/data/courses/2026_dat471_dit066/datasets/glove/glove.840B.300d_queries"
)

for query_size in "${query_sizes[@]}"; do
	for database in pubs glove6b glove840b; do
		data_path="${data_paths[$database]}"
		query_prefix="${query_prefixes[$database]}_${query_size}"
		query_path="${query_prefix}.txt"
		facit_path="${query_prefix}_names.txt"

		for batch_size in "${batch_sizes[@]}"; do
			temp_script=$(mktemp "${script_dir}/.assignment7_problem2.${database}.${query_size}.${batch_size}.XXXXXX.sh")

			sed \
				-e "s|^querysize=.*|querysize=\"${query_size}\"|" \
				-e "s|^data=.*|data=\"${data_path}\"|" \
				-e "s|^query=.*|query=\"${query_path}\"|" \
				-e "s|^facit=.*|facit=\"${facit_path}\"|" \
				-e "s|^batchsize=.*|batchsize=${batch_size}|" \
				-e "s|^#SBATCH -J .*|#SBATCH -J cupy-${database}-${query_size}-b${batch_size}|" \
				"${template_script}" > "${temp_script}"

			sbatch "${temp_script}"
			rm -f "${temp_script}"
		done
	done
done
