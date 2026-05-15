#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH -p short
#SBATCH -J climate_analysis
#SBATCH --output=assignment5prob1_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"

containerpath="/data/courses/2026_dat471_dit066/containers/assignment5.sif"
seed=0x9747b28c
key="Hello, world!"

apptainer exec \
  "${containerpath}" \
  python3 "${base_dir}/assignment5_problem1.py" -s "${seed}" "${key}"

cp "assignment5prob1_${SLURM_JOB_ID}.log" "${base_dir}/output/assignment5prob1-${seed}-${key}.out"