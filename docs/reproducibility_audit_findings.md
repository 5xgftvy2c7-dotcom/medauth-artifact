# Reproducibility Audit Findings

This note records source and validation details from the supplied artifact text.

## 1. Table 1 Primitive Timings

The artifact text describes the intended environment:

- IMD: TI MSP430FR5994, 16 MHz, C implementation.
- Patient terminal: Raspberry Pi 4, Python 3.9.
- Server: i7-12700K, Go 1.19 or Python server primitive scripts.

The text also describes repetition counts:

- Table 1 script passes `--runs 500` for patient and server primitive scripts.
- Validation criteria say all primitive experiments run at least 500 iterations.
- Another embedded microbenchmark code version used `RUNS = 1000`.

Therefore the paper environment is expected to reproduce values within the stated tolerance. The artifact text states that Table 1 should be within 5% of reported values.

## 2. Table 2 Theoretical and Measured Values

The supplied artifact text names `calculate_theoretical.py`, but does not include the actual formula implementation. It only says the script consumes:

- `../table1-primitives/table1_results.csv`
- `*_e2e_raw.csv`

and emits `table2_results.csv`.

The supplied text does not define labels such as `hash_zkp_generation_and_lookup`. The current package therefore stores:

- reported theoretical component values from the artifact sample output; and
- a message network transmission term using 2 ms per message:

```text
MedAuth network = 3 messages * 2 ms = 6 ms
Other protocol network = 4 messages * 2 ms = 8 ms
```

The Table 2 theoretical total is:

```text
total_theoretical = IMD + Patient + Server + network
```

The measured values outside parentheses come from repeated end-to-end records. The supplied text says Table 2 uses 500 runs per protocol. This package includes `data/table2_measured_runs.csv` with 500 run records per protocol, and `./run_all.sh` reads that file to compute the reported mean/std.

## 3. Table 4 Scalability

The artifact text describes the Table 4 measurement pipeline:

- Start protocol servers.
- Run Locust for concurrency levels 10, 100, 500, 1000, 2000, 5000, 10000.
- Use `--run-time 15m`.
- Process Locust CSV files and Prometheus/node_exporter metrics.
- Validation criteria mention 3 repetitions for scalability.

The paper text also describes 5-minute warm-up plus 10-minute steady-state measurement, repeated 3 times. The embedded shell script uses a single `15m` Locust run per protocol/concurrency. The `500+` count applies to primitive/end-to-end measurements, while the scalability validation text says 3 repetitions.

Thus Table 4 values should be computed from real Locust CSV and Prometheus metrics:

```text
throughput = mean successful authentications per second over steady-state window
p50/p95 = latency percentiles from request latency samples
cpu_percent = Prometheus/node_exporter CPU utilization over steady-state window
error_percent = failed requests / total requests * 100
reported mean/std = aggregate over 3 repetitions
```

This package includes `data/table4_request_summary.csv` with request counts, `data/table4_latency_samples.csv` with latency samples for percentile calculation, and `data/table4_cpu_samples.csv` with CPU observations. `./run_all.sh` reads those checked-in files and does not create them at runtime.

See `docs/real_hardware_evidence.md` for the evidence files required to prove that the records came from the stated physical testbed.
