#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import os
import re

# Read timing data from output files
output_dir = '/data/users/melkergu/DAT471/Assignment3/Problem3/output'
data = {}

for filename in os.listdir(output_dir):
    if filename.startswith('assignment3prob3b-10M-') and filename.endswith('.out'):
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
            # Extract number of workers and time elapsed
            workers_match = re.search(r'Number of workers: (\d+)', content)
            time_match = re.search(r'Time elapsed: ([\d.]+) s', content)
            
            if workers_match and time_match:
                num_workers = int(workers_match.group(1))
                elapsed_time = float(time_match.group(1))
                data[num_workers] = elapsed_time

# Sort by number of cores and extract sorted lists
cores = sorted(data.keys())
times = [data[c] for c in cores]

# Calculate speedup relative to single core (baseline)
baseline_time = times[0]
speedup = [baseline_time / t for t in times]

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(cores, speedup, marker='o', linewidth=2, markersize=8, label='Empirical Speedup')

# Add ideal linear speedup for comparison
ideal_speedup = cores
plt.plot(cores, ideal_speedup, marker='s', linewidth=2, markersize=6, linestyle='--', label='Ideal Linear Speedup')

# Labels and title
plt.xlabel('Number of Cores', fontsize=12)
plt.ylabel('Speedup', fontsize=12)
plt.title('Empirical Speedup vs. Number of Cores (10M Dataset)', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=11)
plt.xticks(cores)

# Set axis limits with some padding
plt.xlim(0, 34)
plt.ylim(0, max(ideal_speedup) + 2)

plt.tight_layout()
plt.savefig('/data/users/melkergu/DAT471/Assignment3/Problem3/output/speedup_plot.png', dpi=300)
print("Speedup plot saved to output/speedup_plot.png")

# Print speedup values for reference
print("\nSpeedup Summary:")
print("Cores\tTime (s)\t\tSpeedup")
print("-" * 40)
for c, t, s in zip(cores, times, speedup):
    print(f"{c}\t{t:.4f}\t{s:.4f}")
