#!/usr/bin/env bash
#SBATCH -t 00:05:00
#SBATCH --nodelist=uranus
#SBATCH -p short
#SBATCH -J system_info
#SBATCH --output=system_info_%j.out

echo "Fetching system information of uranus..."
./info_fetcher.sh > system_info_${SLURM_JOB_ID}.out
echo "System information fetched and saved to system_info_${SLURM_JOB_ID}.out"