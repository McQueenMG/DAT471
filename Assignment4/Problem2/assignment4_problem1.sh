#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH -p short
#SBATCH -J climate_analysis
#SBATCH --output=assignment4prob2_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"
data_size=tiny

containerpath="/data/courses/2026_dat471_dit066/containers/assignment4.sif"
climate_datapath="/data/courses/2026_dat471_dit066/datasets/climate/climate_${data_size}.csv"


apptainer exec \
  --bind "${climate_datapath}:/mnt/climate:ro" \
  "${containerpath}" \
  python3 "${base_dir}/pyspark_climate.py" -w "${SLURM_CPUS_PER_TASK}" "/mnt/climate"

cp "assignment4prob2_${SLURM_JOB_ID}.log" "${base_dir}/output/assignment4prob2-${data_size}-${SLURM_CPUS_PER_TASK}.out"