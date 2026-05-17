#!/usr/bin/env bash
#SBATCH -t 00:30:00
#SBATCH -p short
#SBATCH -J hyperloglog
#SBATCH --output=assignment5prob3c_%A_%a.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --array=0-999%50

base_dir="${SLURM_SUBMIT_DIR:-$PWD}"
containerpath="/data/courses/2026_dat471_dit066/containers/assignment5.sif"

datasize=small
datapath="/data/courses/2026_dat471_dit066/datasets/gutenberg/${datasize}"
m=1024

seed_base=0x9747b28c
seed_decimal=$((seed_base + SLURM_ARRAY_TASK_ID))
seed_hex=$(printf '0x%x' "$seed_decimal")

# Create the shared results file once before any task writes to it.
mkdir -p "${base_dir}/output"
RESULTS="${base_dir}/output/assignment5_problem3c_results.csv"
LOCK="${base_dir}/output/assignment5_problem3c_results.lock"
touch "${LOCK}"
if command -v flock >/dev/null 2>&1; then
  flock "${LOCK}" -c "if [ ! -s '${RESULTS}' ]; then printf 'task_id,seed,m,estimate,workers,time\n' > '${RESULTS}'; fi"
else
  if [ ! -s "${RESULTS}" ]; then printf 'task_id,seed,m,estimate,workers,time\n' > "${RESULTS}"; fi
fi

tmp_log="${base_dir}/output/assignment5_problem3c_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.tmp.log"

apptainer exec \
  --bind "${datapath}:/mnt/data:ro" \
  "${containerpath}" \
  python3 "${base_dir}/assignment5_problem3.py" /mnt/data -s "${seed_hex}" -m "${m}" -w "${SLURM_CPUS_PER_TASK}" 2>&1 | tee "${tmp_log}"

# Parse the finished temp log instead of the still-running SLURM log.
# Use awk to extract the value after the colon or the second field for 'Took'.
estimate=$(awk -F': ' '/^Cardinality estimate:/ {print $2; exit}' "${tmp_log}" | awk '{print $1}')
workers=$(awk -F': ' '/^Number of workers:/ {print $2; exit}' "${tmp_log}" | awk '{print $1}')
time=$(awk '/^Took / {print $2; exit}' "${tmp_log}")

# Fallbacks: if any field is empty, try a looser numeric extraction (handles scientific notation)
if [ -z "${estimate}" ]; then
  estimate=$(grep -m1 -oE 'Cardinality estimate: *[+-]?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?' "${tmp_log}" | grep -oE '[+-]?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?' | head -n1)
fi
if [ -z "${workers}" ]; then
  workers=$(grep -m1 -oE 'Number of workers: *[0-9]+' "${tmp_log}" | grep -oE '[0-9]+' | head -n1)
fi
if [ -z "${time}" ]; then
  time=$(grep -m1 -oE 'Took *[0-9]+(\.[0-9]+)?' "${tmp_log}" | grep -oE '[0-9]+(\.[0-9]+)?' | head -n1)
fi

# assemble CSV line
entry="${SLURM_ARRAY_TASK_ID},${seed_hex},${m},${estimate},${workers},${time}"

# atomically append the row
if command -v flock >/dev/null 2>&1; then
  flock "${LOCK}" -c "echo '${entry}' >> '${RESULTS}'"
  rc=$?
else
  echo "${entry}" >> "${RESULTS}"
  rc=$?
fi

# Keep the SLURM log for debugging; only the temp log is deleted.
if [ "${rc}" -ne 0 ]; then
  echo "Warning: failed to append results for task ${SLURM_ARRAY_TASK_ID}" >&2
fi

# remove temp log now that parsing/appending is done
rm -f "${tmp_log}"