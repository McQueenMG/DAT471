#!/usr/bin/env bash
#SBATCH -t 00:05:00
#SBATCH -p short
#SBATCH -J system_info
#SBATCH --output=container_database_%j.log

containerpath="/data/courses/2026_dat471_dit066/containers/assignment1.sif"
datapath="/data/courses/2026_dat471_dit066/datasets/bike_sharing_hourly.csv"
base_dir="${SLURM_SUBMIT_DIR:-$PWD}"


if ls bike_sharing_hourly.csv 2>/dev/null; then
    echo "bike_sharing_hourly.csv already exists in the current directory."
else
    echo "bike_sharing_hourly.csv not found in the current directory. Copying from data path..."
    cp $datapath .
    if ls bike_sharing_hourly.csv 2>/dev/null; then
        echo "bike_sharing_hourly.csv successfully copied to the current directory."
    else
        echo "Failed to copy bike_sharing_hourly.csv to the current directory."
        exit 1
    fi
fi

apptainer exec $containerpath python3 assignment1_problem2c_skeleton.py bike_sharing_hourly.csv

cp container_database_$SLURM_JOB_ID.log $base_dir/output/container_database.out