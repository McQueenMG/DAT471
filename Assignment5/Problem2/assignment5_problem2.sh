#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH -p short
#SBATCH -J hash_evaluation
#SBATCH --output=assignment5prob2_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"

containerpath="/data/courses/2026_dat471_dit066/containers/assignment5.sif"
key=test
seed=0x00000000
m=128

apptainer exec \
  "${containerpath}" \
  python3 "${base_dir}/assignment5_problem2.py" -k "${key}" -s "${seed}" -m "${m}"

cp "assignment5prob2_${SLURM_JOB_ID}.log" "${base_dir}/output/assignment5prob2-${key}-${seed}-${m}.out"