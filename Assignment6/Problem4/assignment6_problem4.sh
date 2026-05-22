#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH -p short
#SBATCH -J locality-sensitive-hashing
#SBATCH --output=assignment6prob4_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"

containerpath="/data/courses/2026_dat471_dit066/containers/assignment6.sif"
small=glove.6B.50d
big=glove.840B.300d
datapath="/data/courses/2026_dat471_dit066/datasets/glove/${big}.txt"
D=50
k=20
L=10

apptainer exec \
  --bind "${datapath}:/mnt/data:ro" \
  "${containerpath}" \
  python3 "${base_dir}/lsh_lsh.py" -D ${D} -k ${k} -L ${L} /mnt/data "queries.txt"

cp "assignment6prob4_${SLURM_JOB_ID}.log" "${base_dir}/output/assignment6prob4-${big}-${D}-${k}-${L}-${SLURM_CPUS_PER_TASK}.out"