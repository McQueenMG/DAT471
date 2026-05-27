#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH -p short
#SBATCH -J cupy-linsearch
#SBATCH --gpus-per-node=L40s:1
#SBATCH --output=assignment7prob2_%j.log
#SBATCH --ntasks=1

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"

containerpath="/data/courses/2026_dat471_dit066/containers/assignment7.sif"

glovesmallpath="/data/courses/2026_dat471_dit066/datasets/glove/glove.6B.50d.txt"
glovebigpath="/data/courses/2026_dat471_dit066/datasets/glove/glove.840B.300d.txt"
pubspath="/data/courses/2026_dat471_dit066/datasets/pubs/pubs.csv"

querysize="tiny"
glovesmallquerypath="/data/courses/2026_dat471_dit066/datasets/glove/glove.6B.50d_queries_${querysize}"
glovebigquerypath="/data/courses/2026_dat471_dit066/datasets/glove/glove.840B.300d_queries_${querysize}"
pubsquerypath="/data/courses/2026_dat471_dit066/datasets/pubs/pub_queries_${querysize}"

data="${pubspath}"
query="${pubsquerypath}.txt"
facit="${pubsquerypath}_names.txt"

batchsize=2


data_base=$(basename "${data}")
query_base=$(basename "${query}")
facit_base=$(basename "${facit}")
dataname="${data_base%.*}"

apptainer exec \
  --bind "${data}:/mnt/data/${data_base}:ro" \
  --bind "${query}:/mnt/queries/${query_base}:ro" \
  --bind "${facit}:/mnt/facit/${facit_base}:ro" \
  --nv "${containerpath}" \
  python3 "${base_dir}/nnquery.py" -d /mnt/data/${data_base} -q /mnt/queries/${query_base} -l /mnt/facit/${facit_base} \
  -b ${batchsize}


echo "Data: ${data}, Query: ${query}, Batch size: ${batchsize}"
cp "assignment7prob2_${SLURM_JOB_ID}.log" "${base_dir}/output/assignment7prob2-${dataname}-${batchsize}-${querysize}.out"