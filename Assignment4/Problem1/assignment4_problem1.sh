#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH -p short
#SBATCH -J twitter_follows
#SBATCH --output=assignment4prob1_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"
data_size=10M

containerpath="/data/courses/2026_dat471_dit066/containers/assignment4.sif"
twitter_datapath="/data/courses/2026_dat471_dit066/datasets/twitter/twitter-2010_${data_size}.txt"


apptainer exec \
  --bind "${twitter_datapath}:/mnt/twitter:ro" \
  "${containerpath}" \
  python3 "${base_dir}/pyspark_twitter_follows.py" -w "${SLURM_CPUS_PER_TASK}" "/mnt/twitter"

cp "assignment4prob1_${SLURM_JOB_ID}.log" "${base_dir}/output/assignment4prob1-${data_size}-${SLURM_CPUS_PER_TASK}.out"