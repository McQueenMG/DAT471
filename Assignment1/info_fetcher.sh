#!/bin/bash


# List of things to fetch:
# •The model of and the clock frequency1 of the CPU
# •The number of physical CPUs (sockets in use), the number of cores, and
# the number of hardware threads
# •The instruction set architecture of the CPU
# •The cache line length
# •The amount of L1, L2, and L3 cache
# •The amount of system RAM
# •The number of GPUs and model of the GPU(s)2
# •The amount of RAM on the GPU(s)
# •The type of filesystem of /data
# •The total amount of disk space and the amount of free space on /data
# •The version of the Linux kernel running on the system and the GNU/Linux
# distribution and its version running on the system
# •The filename and the version of the default Python 3 interpreter available
# on the system (globally installed)


# Fetching CPU information
lscpu | grep "Model name"
lscpu | grep "CPU max MHz"

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

# Fetching number of GPUs and their models
lspci | grep -i "vga" | wc -l | awk '{print "Number of GPUs: "$1}'
lspci | grep -i "vga"

# Fetching GPU RAM
lspci -v | grep -i "vga" -A 20 | grep "Memory at" | grep -oP '\[size=\K[^\]]+' | \
awk 'function to_bytes(s) { if (s~/G/) return s+0*1024*1024*1024; if (s~/M/) return s+0*1024*1024; if (s~/K/) return s+0*1024; return s+0 } { if (to_bytes($1)>max) { max=to_bytes($1); val=$1 } } END { print "GPU RAM: "val }'


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



