#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH -p short
#SBATCH -J planet_game
#SBATCH --output=assignment3c_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"

containerpath="/data/courses/2026_dat471_dit066/containers/assignment3.sif"
planet_datapath="/data/courses/2026_dat471_dit066/datasets/sc2/planets.csv"

time apptainer exec \
  --bind "${planet_datapath}:/mnt/planets:ro" \
  "${containerpath}" \
  python3 "${base_dir}/assignment3_problem1.py" -r local --num-cores "${SLURM_CPUS_PER_TASK}" "/mnt/planets"

cp "assignment3c_${SLURM_JOB_ID}.log" "${base_dir}/output/assignment3c-${datasize}.out"