#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
RUNS="${RUNS:-500}"
TABLE_MODE="${TABLE_MODE:-paper}"
GENERATE_ONLY="${GENERATE_ONLY:-0}"
RUN_BENCHMARKS="${RUN_BENCHMARKS:-0}"

echo "=== Starting MedAuth Microbenchmark Reproducibility ==="
mkdir -p raw-data results

if [ "$GENERATE_ONLY" != "1" ] && [ "$RUN_BENCHMARKS" = "1" ]; then
    echo
    echo "Step 1: Building and running IMD C microbenchmarks"
    make -C platform/imd-msp430 clean all RUNS="$RUNS"
    (cd platform/imd-msp430 && ./imd_microbenchmark)

    echo
    echo "Step 2: Running RPi 4 patient microbenchmarks"
    (cd platform/rpi4-patient && RUNS="$RUNS" "$PYTHON_BIN" rpi4_microbenchmark.py)

    echo
    echo "Step 3: Running i7 server microbenchmarks"
    (cd platform/i7-server && go run .)
else
    echo
    echo "Step 1: Loading packaged experiment records from data/"
    echo "Set RUN_BENCHMARKS=1 to additionally run local primitive timing logs before table calculation."
fi

echo
echo "Step 2: Calculating Table 1 (${TABLE_MODE})"
"$PYTHON_BIN" scripts/generate_microbenchmark_table.py --mode "$TABLE_MODE" --data-dir data --raw-dir raw-data --out-dir results

echo
echo "Step 3: Calculating Table 2 (${TABLE_MODE})"
"$PYTHON_BIN" scripts/generate_e2e_latency_table.py --mode "$TABLE_MODE" --data-dir data --raw-dir raw-data --out-dir results

echo
echo "Step 4: Calculating Table 4 (${TABLE_MODE})"
"$PYTHON_BIN" scripts/generate_scalability_table.py --mode "$TABLE_MODE" --data-dir data --raw-dir raw-data --out-dir results

echo
echo "Done. Calculated tables are in results/"
