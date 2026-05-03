# Reproducibility Notes

## Table 1 Primitive Timings

The experiment environment uses:

- IMD: TI MSP430FR5994, 16 MHz, C implementation.
- Patient terminal: Raspberry Pi 4, Python 3.9.
- Server: i7-12700K, Go 1.19 or Python server primitive scripts.

Primitive timing experiments use at least 500 iterations. `RUNS=500` is the default for local benchmark execution.

## Table 2 Theoretical And Measured Values

The theoretical values inside parentheses use:

```text
total_theoretical = IMD + Patient + Server + network
```

The network term uses 2 ms per message:

```text
MedAuth network = 3 messages * 2 ms = 6 ms
PLAKA-MD network = 4 messages * 2 ms = 8 ms
ERASMIS network = 4 messages * 2 ms = 8 ms
4F-IoMT network = 4 messages * 2 ms = 8 ms
```

The measured values outside parentheses use `data/table2_measured_runs.csv`, with 500 run records per protocol:

```text
measured cell = mean(run samples) +/- sample_std(run samples)
```

## Table 4 Scalability

The scalability experiment uses:

- concurrency levels: 10, 100, 500, 1000, 2000, 5000, 10000
- run time: 15 minutes
- warm-up: 5 minutes
- steady-state window: 10 minutes
- repetitions: 3

Table 4 is calculated from request counts, latency samples, and CPU observations:

```text
throughput per repeat = successful_requests / steady_state_seconds
throughput cell = mean(3 repeat throughputs) +/- sample_std(3 repeat throughputs)
p50/p95 = nearest-rank percentiles over latency samples
cpu_percent = mean(cpu_percent samples)
error_percent = failed_requests / total_requests * 100
```

