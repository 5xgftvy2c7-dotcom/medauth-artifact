# Artifact Contents

## Structure

The artifact is organized as a GitHub-ready reproduction package with:

- root `README.md`
- root `run_all.sh`
- root `install_deps.sh`
- platform-specific code under `platform/`
- experiment records under `data/`
- local timing logs under `raw-data/`
- calculated outputs under `results/`

## Source And Build Files

The package includes these source and build files:

- C/H: `aes128`, `sha256`, `puf`, `zkp`, `ecc_p256`, `crypto_primitives`, `microbenchmark_main`
- Makefile: `platform/imd-msp430/Makefile`
- Shell: `run_all.sh`, `install_deps.sh`
- Go: `platform/i7-server/i7_microbenchmark.go`
- Python: `platform/rpi4-patient/rpi4_microbenchmark.py`
- Table 1 generator: `scripts/generate_microbenchmark_table.py`
- Table 2 generator: `scripts/generate_e2e_latency_table.py`
- Table 4 generator: `scripts/generate_scalability_table.py`

## Experiment Records

The table calculations use these checked-in records:

- `data/table1_primitive_profiles.csv`
- `data/table2_theoretical_terms.csv`
- `data/table2_measured_runs.csv`
- `data/table4_experiment_config.csv`
- `data/table4_request_summary.csv`
- `data/table4_latency_samples.csv`
- `data/table4_cpu_samples.csv`

## Calculation Coverage

`./run_all.sh` calculates:

- Table 1: cryptographic primitive execution time
- Table 2: end-to-end authentication latency
- Table 4: server scalability under concurrent load

The output files are written to `results/` as CSV, Markdown, and LaTeX table bodies where applicable.

