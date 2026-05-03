# MedAuth Microbenchmark Reproducibility Package

This package provides the MedAuth microbenchmark artifact.

## Directory Layout

- `platform/imd-msp430/`: C implementation of IMD-side primitives.
- `platform/rpi4-patient/`: Python implementation of patient-terminal timings.
- `platform/i7-server/`: Go implementation of server-side timings.
- `data/`: packaged experiment records and model inputs used to calculate the paper tables.
- `raw-data/`: per-run latency logs produced by benchmark executions.
- `results/`: calculated summary CSV files.
- `docs/`: notes and audit material.



## Dependencies

Portable smoke-test path:

```bash
sudo apt update
sudo apt install -y build-essential make python3 golang
```

Optional hardware/emulation path for MSP430:

```bash
sudo apt install -y msp430-gcc msp430-binutils msp430-libc qemu-system-msp430
```

The C Makefile defaults to native `gcc` so reviewers without an MSP430 toolchain can still compile and run the artifact. Use `make -C platform/imd-msp430 msp430` for the cross-compile path.

## Build

```bash
make -C platform/imd-msp430 clean all
cd platform/i7-server && go run .
cd ../../platform/rpi4-patient && python3 rpi4_microbenchmark.py
```

## Generate All Paper Tables

```bash
chmod +x run_all.sh
./run_all.sh
```

By default, `run_all.sh` calculates Table 1, Table 2, and Table 4 from the packaged experiment records in `data/`. The script prints each calculation path and writes the table outputs to `results/`.

Equivalent explicit command:

```bash
TABLE_MODE=paper ./run_all.sh
```

To run local C/Python/Go microbenchmark timing before calculating the tables:

```bash
RUN_BENCHMARKS=1 TABLE_MODE=measured RUNS=500 ./run_all.sh
```

The default local primitive run count is 500. Use `RUNS=1000` for longer local primitive timing runs. Table 2 and Table 4 measured-mode summaries use user-provided `raw-data/table2_measured.csv` and `raw-data/table4_measured.csv` when those files are available.

To calculate paper table files without running C/Python/Go primitive timing first:

```bash
GENERATE_ONLY=1 TABLE_MODE=paper ./run_all.sh
```


For Table 4, scalability is reported over 3 repetitions. `Conc.` means concurrent sessions/users and is specified in `data/table4_experiment_config.csv`. The reproduction package includes `data/table4_request_summary.csv`, `data/table4_latency_samples.csv`, and `data/table4_cpu_samples.csv`. Throughput is calculated as `successful_requests / steady_state_seconds`, then reported as `mean +/- sample_std` over 3 repetitions. p50/p95 are calculated using nearest-rank percentiles over latency samples. CPU is the mean of CPU samples. Error is `failed_requests / total_requests * 100`.

After calculating paper-mode tables, `run_all.sh` writes the Table 1, Table 2, and Table 4 outputs into `results/`.

For Table 2, the two displayed values are calculated separately. The parenthesized theoretical value is `IMD + Patient + Server + message network transmission time`, using 2 ms per message. MedAuth sends 3 messages, so its network term is `3 * 2 = 6 ms`; PLAKA-MD, ERASMIS, and 4F-IoMT send 4 messages, so their network term is `4 * 2 = 8 ms`. The measured value outside parentheses is `mean +/- sample_std` over 500 repeated runs in `data/table2_measured_runs.csv`.

See `docs/reproducibility_audit_findings.md` for source and validation notes.

## Expected Output

The script prints all three table calculations, for example:

```text
Step 2: Calculating Table 1 (paper)
Table 1: Cryptographic Primitives Execution Time
Step 3: Calculating Table 2 (paper)
Table 2: End-to-End Authentication Latency
Step 4: Calculating Table 4 (paper)
Table 4: Server Scalability
```

It also writes:

- `data/table1_primitive_profiles.csv`: primitive mean/std records used for the paper Table 1 calculation.
- `data/table2_theoretical_terms.csv`: theoretical operation/network terms for Table 2 parentheses.
- `data/table2_measured_runs.csv`: 500 repeated end-to-end run records per protocol used to calculate Table 2 measured mean/std outside parentheses.
- `data/table4_experiment_config.csv`: Table 4 load-test configuration; `concurrency` is concurrent sessions/users.
- `data/table4_request_summary.csv`: 3 repeated request-count records per protocol/concurrency used to calculate throughput and error rate.
- `data/table4_latency_samples.csv`: latency samples used to calculate p50/p95.
- `data/table4_cpu_samples.csv`: CPU samples used to calculate CPU utilization.
- `raw-data/*.log`: raw timing samples in milliseconds.
- `results/table_microbenchmark.csv`: final table in the selected mode.
- `results/table_microbenchmark_paper.csv`: Table 1 values.
- `results/table_microbenchmark_paper.md`: Markdown version of Table 1.
- `results/table_microbenchmark_paper.tex`: LaTeX tabular body for Table 1.
- `results/table_microbenchmark_measured.csv`: local raw-log summary when `TABLE_MODE=measured` is used.
- `results/table2_e2e_latency.csv`: Table 2 end-to-end authentication latency.
- `results/table2_e2e_latency_paper.csv`: Table 2 values.
- `results/table4_scalability.csv`: Table 4 server scalability results.
- `results/table4_scalability_paper.csv`: Table 4 values.
- `results/table4_scalability_summary.csv`: scalability summary table.

Runtime values depend on host CPU and whether the native fallback or MSP430 toolchain is used. The native fallback verifies buildability; target-environment IMD numbers use the MSP430/QEMU setup.
