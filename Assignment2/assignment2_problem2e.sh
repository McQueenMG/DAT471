#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH --nodelist=callisto
#SBATCH -p short
#SBATCH -J assignment2e
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --output=assignment2e_%j.log

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"

datasize="huge"
workers=64
batch_size=1

containerpath="/data/courses/2026_dat471_dit066/containers/assignment2.sif"
datapath="/data/courses/2026_dat471_dit066/datasets/gutenberg/${datasize}"

apptainer exec --bind "${datapath}:/mnt/data:ro" "${containerpath}" python3 "${base_dir}/assignment2_problem2e.py" -w "${workers}" -b "${batch_size}" /mnt/data  

cp "assignment2e_${SLURM_JOB_ID}.log" "${base_dir}/output/assignment2e-${datasize}-${workers}.out"