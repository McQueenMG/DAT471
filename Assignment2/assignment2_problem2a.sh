#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH -p short
#SBATCH -J system_info
#SBATCH --output=assignment2a_%j.log

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"

datasize="tiny"
workers=16
batch_size=16

containerpath="/data/courses/2026_dat471_dit066/containers/assignment2.sif"
datapath="/data/courses/2026_dat471_dit066/datasets/gutenberg/${datasize}"

apptainer exec \
  --bind "${datapath}:/mnt/data:ro" \
  "${containerpath}" \
  python3 "${base_dir}/assignment2_problem2.py" -w "${workers}" -b "${batch_size}" /mnt/data \
  | awk '{print "Output from assignment2_problem2.py: "$0}'

cp "assignment2a_${SLURM_JOB_ID}.log" "${base_dir}/output/assignment2a-${datasize}.out"