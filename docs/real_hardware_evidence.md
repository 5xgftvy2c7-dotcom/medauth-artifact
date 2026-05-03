# Real Hardware Evidence

Use this checklist to document the physical hardware and load-test environment used for an experiment.

## Environment Files

Include these files after running the experiment:

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

## Table 4 File Count

For 3-repetition scalability experiments:

- MedAuth: 7 concurrency levels x 3 repetitions = 21 Locust raw result sets.
- PLAKA-MD: 7 concurrency levels x 3 repetitions = 21 Locust raw result sets.
- ERASMIS: 7 concurrency levels x 3 repetitions = 21 Locust raw result sets.
- 4F-IoMT: 7 concurrency levels x 3 repetitions = 21 Locust raw result sets.

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

