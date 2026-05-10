#!/usr/bin/env python3

import os
import re
import sys
import matplotlib.pyplot as plt

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, 'output')
data = {}

file_pattern = re.compile(r'^assignment4prob2-large-.*\.out$')

for filename in os.listdir(output_dir):
    if not file_pattern.match(filename):
        continue
    path = os.path.join(output_dir, filename)
    with open(path, 'r') as f:
        txt = f.read()

    workers_m = re.search(r'num workers:\s*(\d+)', txt, re.IGNORECASE)
    if not workers_m:
        continue
    workers = int(workers_m.group(1))

    # Find named time components like 'read time: 97.4 s'
    comps = dict(re.findall(r'([a-zA-Z0-9 _-]+time):\s*([\d.]+)\s*s', txt, re.IGNORECASE))
    # normalize keys to lower-case trimmed
    comps = {k.strip().lower().replace('_', ' '): float(v) for k, v in comps.items()}

    total = None
    if 'total time' in comps:
        total = comps.get('total time')

    read = comps.get('read time')

    # Compute compute_time:
    # Prefer sum of all components except 'read time' if components present.
    if comps:
        compute_time = sum(v for k, v in comps.items() if k not in ('read time', 'total time', 'other time'))
        # If 'total time' present but components don't add to it (floating/formatting),
        # ensure compute_time isn't zero; otherwise fallback to total - read
        if compute_time == 0 and total is not None and read is not None:
            compute_time = max(0.0, total - read)
    elif total is not None and read is not None:
        compute_time = max(0.0, total - read)
    elif total is not None:
        compute_time = total
    else:
        # Could not find any time info for this file
        print(f"Warning: no timing found for {filename}", file=sys.stderr)
        continue

    data[workers] = compute_time

if not data:
    print("No timing data found. Check output files and regexes.", file=sys.stderr)
    sys.exit(1)

cores = sorted(data.keys())
times = [data[c] for c in cores]

baseline_time = times[0]
speedup = [baseline_time / t if t > 0 else 0.0 for t in times]

plt.figure(figsize=(10, 6))
plt.plot(cores, speedup, marker='o', linewidth=2, markersize=8, label='Compute-time Speedup')
plt.xlabel('Number of Cores', fontsize=12)
plt.ylabel('Speedup (compute time)', fontsize=12)
plt.title('Empirical Compute-time Speedup vs. Number of Cores', fontsize=14)
plt.xscale('log', base=2)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=11)
plt.xticks(cores)
plt.xlim((min(cores)-0.05) if cores else 1, (max(cores)+4) if cores else 1)
plt.ylim(0, max(speedup) + 2)

plt.tight_layout()
out_png = os.path.join(output_dir, 'prob2_compute_speedup_plot.png')
plt.savefig(out_png, dpi=300)
print(f"Compute-speedup plot saved to {out_png}")

print("\nSpeedup Summary (compute time):")
print("Cores\tCompute Time (s)\tSpeedup")
print("-" * 44)
for c, t, s in zip(cores, times, speedup):
    print(f"{c}\t{t:.4f}\t{s:.4f}")