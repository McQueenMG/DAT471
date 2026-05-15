#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH -p short
#SBATCH -J hash_evaluation
#SBATCH --output=assignment5prob1b_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"

containerpath="/data/courses/2026_dat471_dit066/containers/assignment5.sif"
datapath="/data/courses/2026_dat471_dit066/datasets/words"
m=7

apptainer exec \
  --bind "${datapath}:/mnt/words:ro" \
  "${containerpath}" \
  python3 "${base_dir}/hash_evaluator.py" -s "/mnt/words" -m "${m}"

cp "assignment5prob1b_${SLURM_JOB_ID}.log" "${base_dir}/output/assignment5prob1b-${m}.out"