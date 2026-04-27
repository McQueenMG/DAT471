#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH --nodelist=callisto
#SBATCH -p short
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH -J system_info
#SBATCH --output=assignment2c_%j.log

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"

datasize="huge"
workers=1
batch_size=1

containerpath="/data/courses/2026_dat471_dit066/containers/assignment2.sif"
datapath="/data/courses/2026_dat471_dit066/datasets/gutenberg/${datasize}"

apptainer exec \
  --bind "${datapath}:/mnt/data:ro" \
  "${containerpath}" \
  python3 "${base_dir}/assignment2_problem2a.py" -w "${workers}" -b "${batch_size}" /mnt/data  

cp "assignment2c_${SLURM_JOB_ID}.log" "${base_dir}/output/assignment2c-${datasize}.out"