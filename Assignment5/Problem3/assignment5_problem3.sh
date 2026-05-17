#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH -p short
#SBATCH -J hyperloglog
#SBATCH --output=assignment5prob3_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"
containerpath="/data/courses/2026_dat471_dit066/containers/assignment5.sif"

datasize=small
datapath="/data/courses/2026_dat471_dit066/datasets/gutenberg/${datasize}"
seed=0x9747b28c
m=1024

apptainer exec \
  --bind "${datapath}:/mnt/data:ro" \
  "${containerpath}" \
  python3 "${base_dir}/assignment5_problem3.py" /mnt/data  -s "${seed}" -m "${m}" -w "${SLURM_CPUS_PER_TASK}"

cp "assignment5prob3_${SLURM_JOB_ID}.log" "${base_dir}/output/assignment5prob3-${datasize}-${SLURM_CPUS_PER_TASK}.out"