#!/usr/bin/env bash
#SBATCH -t 00:01:00
#SBATCH --nodelist=uranus
#SBATCH -p short
#SBATCH -J system_info
#SBATCH --output=system_info_job_%j.log


# Fetching CPU information
lscpu | grep "Model name"
if lscpu | grep "CPU max MHz" > /dev/null; then
    lscpu | grep "CPU max MHz"
else
    echo "CPU MHz: Not available"
fi

# Fetching the number of physical CPUs, cores, and threads
lscpu | grep "Socket(s)"
lscpu | grep "Core(s) per socket"
lscpu | grep "Thread(s) per core"

# Fetching instruction set architecture
lscpu | grep "Architecture"

# Fetching cache line length
getconf -a | grep CACHE_LINESIZE

# Fetching cache sizes
lscpu | grep "L1d cache"
lscpu | grep "L1i cache"
lscpu | grep "L2 cache"
lscpu | grep "L3 cache"

# Fetching system RAM
free -h | grep "Mem" | awk '{print "Total RAM: "$2}'

# Fetching GPU information
if command -v nvidia-smi > /dev/null; then
    nvidia-smi --query-gpu=name --format=csv,noheader | awk '{print "GPU model: "$0}'
    nvidia-smi --query-gpu=name --format=csv,noheader | wc -l | awk '{print "Number of GPUs: "$1}'
    nvidia-smi --query-gpu=memory.total --format=csv,noheader | awk '{print "GPU RAM: "$0}'
else
    lspci | grep -i "vga" | grep -i "nvidia" | awk -F ': ' '{print "GPU model: "$2}'
    lspci | grep -i "vga" | grep -i "nvidia" | wc -l | awk '{print "Number of GPUs: "$1}'
    echo "GPU RAM: n/a"
fi

# Fetching filesystem type of /data
df -T /data | tail -1 | awk '{print "Filesystem type: "$2}'

# Fetching total and free disk space on /data
df -h /data | tail -1 | awk '{print "Total: "$2", Free: "$4}'

# Fetching Linux kernel version and distribution information
uname -r | awk '{print "Linux kernel version: "$1}'
cat /etc/os-release | grep "PRETTY_NAME" | awk '{print "Distribution: "$2}'

# Fetching default Python 3 interpreter and its version
which python3 | awk '{print "Python 3 interpreter: "$1}'
python3 --version | awk '{print "Python 3 version: "$2}'

# Copy the logs to an output file with the job ID and hostname
cp system_info_job_${SLURM_JOB_ID}.log output/system_info_${SLURM_JOB_ID}_$(hostname).out