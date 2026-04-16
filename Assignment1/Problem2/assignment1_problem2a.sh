#!/usr/bin/env bash
#SBATCH -t 00:01:00
#SBATCH -p short
#SBATCH -J system_info
#SBATCH --output=container_info_job_%j.log

containerpath="/data/courses/2026_dat471_dit066/containers/assignment1.sif"

apptainer exec $containerpath uname -r | awk '{print "Linux kernel version: "$1}'
apptainer exec $containerpath python3 --version | awk '{print "Python 3 version: "$2}'
apptainer exec $containerpath lscpu | grep "Model name"

cp container_info_job_$SLURM_JOB_ID.log /data/users/melkergu/DAT471/Assignment1/Problem2/output/container_info.out