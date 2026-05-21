#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH -p short
#SBATCH -J normalization
#SBATCH --output=assignment6prob1_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"

containerpath="/data/courses/2026_dat471_dit066/containers/assignment6.sif"
small=glove.6B.50d
big=glove.840B.300d
datapath="/data/courses/2026_dat471_dit066/datasets/glove/${big}.txt"

apptainer exec \
  --bind "${datapath}:/mnt/data:ro" \
  "${containerpath}" \
  python3 "${base_dir}/lsh_normalize.py" /mnt/data 

cp "assignment6prob1_${SLURM_JOB_ID}.log" "${base_dir}/output/assignment6prob1-${big}-${SLURM_CPUS_PER_TASK}.out"