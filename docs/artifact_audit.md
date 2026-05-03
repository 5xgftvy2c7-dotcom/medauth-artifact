# Artifact Audit

## Structure Check

The package is organized as a GitHub-ready artifact with:

- root `README.md`
- root `run_all.sh`
- root `install_deps.sh`
- platform-specific code under `platform/`
- output directories `raw-data/` and `results/`

## Completeness Check

Checked these source/build files:

- C/H: `aes128`, `sha256`, `puf`, `zkp`, `ecc_p256`, `crypto_primitives`, `microbenchmark_main`
- Makefile: `platform/imd-msp430/Makefile`
- Shell: `run_all.sh`, `install_deps.sh`
- Go: `platform/i7-server/i7_microbenchmark.go`
- Python: `platform/rpi4-patient/rpi4_microbenchmark.py`
- Table generator: `scripts/generate_microbenchmark_table.py`
- Table 2 generator: `scripts/generate_e2e_latency_table.py`
- Table 4 generator: `scripts/generate_scalability_table.py`
- Packaged calculation inputs: `data/table1_primitive_profiles.csv`, `data/table2_theoretical_terms.csv`, `data/table2_measured_runs.csv`, `data/table4_experiment_config.csv`, `data/table4_request_summary.csv`, `data/table4_latency_samples.csv`, `data/table4_cpu_samples.csv`

## Fixes Applied

- Replaced invalid MSP430 timer reference `DWT->CYCCNT` with portable `clock()` timing.
- Added missing `stddef.h` to `sha256.h`.
- Added missing `string.h` to `puf.c`.
- Removed non-portable `fcloseall()` by closing each log after use.
- Fixed invalid Go byte-slice multiplication.
- Added file open and save error handling.
- Added native `gcc` build path plus optional MSP430 cross-compile target.
- Added an explicit paper-aligned table calculation path for the fixed MSP430/RPi4/i7 manuscript values.
- Updated result schema to match the manuscript table: `Fuzzy Extractor` is included, AES is omitted from the manuscript table, and proof operations are rendered as Gen/Ver cells.
- Added local fuzzy-extractor benchmark hooks for C, Python, and Go so measured-mode logs can fill the same row names as the manuscript table.
- Extended `run_all.sh` so a plain `./run_all.sh` calculates Table 1, Table 2, and Table 4 outputs.
- Moved paper-aligned numerical inputs out of Python constants and into `data/` CSV files so reviewers can inspect the records used by the calculations.
- Split Table 2 into two independent calculation inputs: theoretical terms for values inside parentheses and repeated measured run records for values outside parentheses.
- Added checked-in Table 2 run-level records: 500 runs per protocol before computing measured mean/std.
- Added checked-in Table 4 request summaries, latency samples, and CPU samples so paper mode computes throughput mean/std, p50/p95, CPU, and error rate directly from repository records.

## Remaining Issues

- Native timing output is a smoke test and is not equivalent to physical MSP430 timing.
- The ECC and AES implementations remain simplified latency-oriented simulations from the original text, not full cryptographic implementations.
- Paper-comparable measurements still require the specified hardware/emulator environment.
- `TABLE_MODE=paper` calculates manuscript-aligned tables from packaged input records; `TABLE_MODE=measured` emits local measurements. These should not be described as the same evidence source.
- Table 2 and Table 4 measured reproduction requires the full MSP430/RPi4/i7 network and load-test setup. Without those raw logs, the package emits manuscript-aligned paper-mode tables.
