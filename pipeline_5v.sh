#!/bin/bash
# =============================================================================
# L-level pipeline (5V): simulate -> extract -> delete for TSMC 5V devices
# 5 corners run in parallel per L, raw data lives in RAM disk only
# =============================================================================

set -euo pipefail

cleanup() {
    echo ""
    echo "[!] Interrupted. Cleaning up..."
    pkill -P $$ 2>/dev/null || true
    sleep 1
    umount "$RAMDIR" 2>/dev/null || true
    echo "[!] Done."
    exit 1
}
trap cleanup INT TERM

# ----- Config ----------------------------------------------------------------
RAMDIR="/mnt/ramraw"
MATDIR="/mnt/data/tsmc18_5v_out"
SCRIPTDIR="/mnt/hgfs/share/gmIdNeoKit_tsmc18"
PYTHON="python3"
FINE="--fine"
VOLTAGE="5v"
CORNERS="tt ff ss fs sf"

# ----- Helper: create RAM disk -----------------------------------------------
setup_ramdisk() {
    if ! mountpoint -q "$RAMDIR"; then
        echo "[*] Creating tmpfs at $RAMDIR (size=16G) ..."
        mkdir -p "$RAMDIR"
        mount -t tmpfs -o size=16G tmpfs "$RAMDIR"
    fi
}

# ----- Helper: run one corner simulation -------------------------------------
run_sim() {
    local corner=$1 l_start=$2 l_end=$3
    local logfile="/tmp/sim5v_${corner}_L${l_start}.log"
    cd "$SCRIPTDIR"
    $PYTHON run_sim_5v.py "$corner" $FINE --outdir "$RAMDIR" --L-range "$l_start" "$l_end" 2>&1 | tee "$logfile"
}

# ----- Helper: run one corner extraction -------------------------------------
run_extract() {
    local corner=$1 l_start=$2 l_end=$3
    local logfile="/tmp/ext5v_${corner}_L${l_start}.log"
    cd "$SCRIPTDIR"
    $PYTHON extract_new.py --voltage "$VOLTAGE" $FINE \
        --srcdir "$RAMDIR" --outdir "$MATDIR" \
        --L-range "$l_start" "$l_end" --workers 1 "$corner" 2>&1 | tee "$logfile"
}

# ----- Helper: clean one L across all corners --------------------------------
clean_l() {
    local idx=$1
    local prefix="L$(printf '%03d' $idx)_"
    for d in "$RAMDIR"/raw_tsmc18_5v_*/; do
        if [ -d "$d" ]; then
            find "$d" -maxdepth 1 -type d -name "${prefix}*" -exec rm -rf {} + 2>/dev/null || true
        fi
    done
}

# ----- Helper: check if a previous run failed --------------------------------
check_failure() {
    local stage=$1 l_idx=$2
    local failed=0
    for corner in $CORNERS; do
        if [ -f "/tmp/${stage}5v_${corner}_L${l_idx}.fail" ]; then
            failed=1
            echo "    [ERROR] $stage failed for corner=$corner L=$l_idx"
            echo "    Log: /tmp/${stage}5v_${corner}_L${l_idx}.log"
        fi
    done
    if [ $failed -ne 0 ]; then
        echo "*** Aborting due to failures above ***"
        exit 1
    fi
}

# ----- Main ------------------------------------------------------------------
echo "========================================"
echo "Pipeline (5V): 5 corners x nL, fine mode"
echo "RAM:      $RAMDIR"
echo "MAT:      $MATDIR"
echo "========================================"

setup_ramdisk
mkdir -p "$MATDIR"

cd "$SCRIPTDIR"
nL=$($PYTHON -c "
from config_tsmc18_5v import get_config
c=get_config('tt', coarse=False)
all_L = sorted(set(list(c['LENGTH']) + list(c['LENGTH_p'])))
print(len(all_L))
")

echo "[*] Total L count: $nL"
echo "[*] Corners: $CORNERS"
echo ""

t_total_start=$(date +%s)

for l in $(seq 0 $((nL - 1))); do
    l_next=$((l + 1))
    t_l_start=$(date +%s)
    echo ""
    echo "===== L=$l / $((nL - 1)) ====="

    # --- 1. Parallel simulation (5 corners) ---
    echo "[1/3] Simulating ..."
    pids=()
    for corner in $CORNERS; do
        (
            if run_sim "$corner" "$l" "$l_next"; then
                rm -f "/tmp/sim5v_${corner}_L${l}.fail"
            else
                touch "/tmp/sim5v_${corner}_L${l}.fail"
            fi
        ) &
        pids+=($!)
    done
    for pid in "${pids[@]}"; do wait "$pid"; done
    check_failure "sim" "$l"
    echo "      Simulation OK"

    # --- 2. Parallel extraction (5 corners) ---
    echo "[2/3] Extracting ..."
    pids=()
    for corner in $CORNERS; do
        (
            if run_extract "$corner" "$l" "$l_next"; then
                rm -f "/tmp/ext5v_${corner}_L${l}.fail"
            else
                touch "/tmp/ext5v_${corner}_L${l}.fail"
            fi
        ) &
        pids+=($!)
    done
    for pid in "${pids[@]}"; do wait "$pid"; done
    check_failure "ext" "$l"
    echo "      Extraction OK"

    # --- 3. Clean raw for this L ---
    echo "[3/3] Cleaning raw ..."
    clean_l "$l"
    echo "      Cleaned"

    # --- Timing ---
    t_l_end=$(date +%s)
    l_elapsed=$((t_l_end - t_l_start))
    total_elapsed=$((t_l_end - t_total_start))
    avg_l_time=$((total_elapsed / (l + 1)))
    remaining=$((nL - l - 1))
    eta=$((remaining * avg_l_time))

    printf "  [TIME] L=%d took %ds | Total %ds | Avg %ds/L | ETA %ds (~%dh%02dm)\n" \
        "$l" "$l_elapsed" "$total_elapsed" "$avg_l_time" "$eta" "$((eta / 3600))" "$((eta % 3600 / 60))"
done

t_total_end=$(date +%s)
total_time=$((t_total_end - t_total_start))
echo ""
echo "========================================"
printf "ALL DONE in %ds (~%dh%02dm%02ds)\n" "$total_time" "$((total_time / 3600))" "$((total_time % 3600 / 60))" "$((total_time % 60))"
echo "========================================"
