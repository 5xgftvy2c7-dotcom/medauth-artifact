# Real Hardware Evidence Requirements

This document lists the evidence needed to support the experimental origin of the included records:

1. The packaged CSV records calculate the paper tables.
2. The packaged CSV records were captured from the stated physical testbed.

Run `./run_all.sh` to verify the table calculations. Use the evidence files below to document the real hardware and load-test environment.

## Table 4 Repetition Count From Supplied Artifact Text

The supplied artifact text contains two relevant statements:

- The `table4-scalability/run_experiment.sh` fragment loops over protocols and concurrency levels and runs one Locust command per protocol/concurrency pair with `--run-time 15m`.
- The validation/statistical-rigor text says scalability experiments use `3 repetitions`.

Therefore, the strongest support for Table 4 is:

- 3 repeated throughput observations per protocol/concurrency level when reporting `mean +/- std. dev.`.
- Each repeated observation should correspond to one 15-minute Locust run: 5-minute warm-up discarded, 10-minute steady-state used.

The supplied text does not state 100 or 500 repetitions for Table 4. The `500+` count applies to primitive/end-to-end repeated measurements, not to scalability repetitions.

## Evidence Needed To Prove Real-Hardware Origin

To prove the Table 2 and Table 4 records came from the real testbed, include these files without editing them after capture:

- `evidence/environment/server_uname.txt`: output of `uname -a`.
- `evidence/environment/server_cpu.txt`: output of `lscpu`.
- `evidence/environment/server_memory.txt`: output of `free -h`.
- `evidence/environment/tool_versions.txt`: versions for `go`, `python3`, `gcc`, `locust`, `prometheus`, and `node_exporter`.
- `evidence/environment/git_commit.txt`: repository commit hash used during the run.
- `evidence/table2/*.csv`: raw 500-run end-to-end logs for each protocol.
- `evidence/table4/locust_raw/*.csv`: Locust CSV files for each protocol/concurrency/repetition.
- `evidence/table4/prometheus_raw/*.csv`: exported CPU/memory observations covering each 15-minute run.
- `evidence/table4/run_command_log.txt`: terminal transcript showing the exact Locust commands, timestamps, protocol, concurrency, and repetition number.
- `evidence/manifest_sha256.txt`: SHA-256 checksums for all raw evidence files.

## Minimal Table 4 File Count

For Table 4, with the paper's 3-repetition interpretation:

- MedAuth: 7 concurrency levels x 3 repetitions = 21 Locust raw result sets.
- PLAKA-MD: 7 concurrency levels x 3 repetitions = 21 Locust raw result sets.
- ERASMIS: 10, 100, and `>=500` summary rows x 3 repetitions = at least 9 raw/evidence result sets. If all original concurrency levels were actually run before collapsing to `>=500`, keep all 21 result sets.
- 4F-IoMT: same as ERASMIS.

If an experiment uses 100 or 500 scalability repetitions, include 100 or 500 raw result sets per protocol/concurrency level, and aggregate all of them in the table calculation.

## Example Evidence-Capture Commands

Run these on the server before the experiment:

```bash
mkdir -p evidence/environment evidence/table2 evidence/table4/locust_raw evidence/table4/prometheus_raw
uname -a > evidence/environment/server_uname.txt
lscpu > evidence/environment/server_cpu.txt
free -h > evidence/environment/server_memory.txt
{
  go version
  python3 --version
  gcc --version | head -n 1
  locust --version
  prometheus --version 2>&1 | head -n 1
  node_exporter --version 2>&1 | head -n 1
} > evidence/environment/tool_versions.txt
git rev-parse HEAD > evidence/environment/git_commit.txt
```

After collecting all raw logs:

```bash
find evidence -type f -print0 | sort -z | xargs -0 sha256sum > evidence/manifest_sha256.txt
```

The final proof statement should cite:

- the exact machine/testbed;
- the exact date/time;
- the git commit;
- the raw log filenames;
- the checksum manifest;
- the `./run_all.sh` output showing that the checked-in raw/summary records calculate the paper tables.
