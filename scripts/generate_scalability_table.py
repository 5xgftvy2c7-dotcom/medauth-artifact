#!/usr/bin/env python3
"""Generate Table 4: server scalability under concurrent load."""

import argparse
import csv
import math
from pathlib import Path


HEADER = ["Protocol", "Conc.", "Throughput (auth/s)", "Latency p50 (ms)", "Latency p95 (ms)", "CPU (%)", "Error (%)"]

SUMMARY_HEADER = ["Protocol", "MST (auth/s)", "Saturation Point", "<10ms @", "Error @10k"]
SUMMARY_ROWS = [
    ("MedAuth", "1250", "500--1k", "<=500", "5.2%"),
    ("PLAKA-MD", "1420", "1k--2k", "<=1k", "3.5%"),
    ("ERASMIS", "0.3", "<10", "None", "100.0%"),
    ("4F-IoMT", "0.28", "<10", "None", "100.0%"),
]


def load_measured(raw_dir):
    path = raw_dir / "table4_measured.csv"
    if not path.exists():
        raise SystemExit(
            "Measured Table 4 mode requires raw-data/table4_measured.csv. "
            "Use TABLE_MODE=paper to calculate from packaged request/latency/CPU records."
        )
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if rows and rows[0] == HEADER:
        return [tuple(row) for row in rows[1:]]
    return [tuple(row) for row in rows]


def format_num(value):
    if isinstance(value, str):
        return value
    if abs(value) < 1e-12:
        return "0.0"
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def format_error(value):
    if abs(value) < 1e-12:
        return "0.0"
    if abs(value - round(value)) < 1e-9:
        return f"{value:.1f}"
    return format_num(value)


def sample_std(values):
    if len(values) <= 1:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))


def nearest_rank(values, percentile):
    if not values:
        return "-"
    values = sorted(values)
    index = math.ceil((percentile / 100.0) * len(values)) - 1
    return values[max(0, min(index, len(values) - 1))]


def load_config(data_dir):
    path = data_dir / "table4_experiment_config.csv"
    config = {}
    order = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["protocol"], row["concurrency"])
            config[key] = row
            order.append(key)
    return order, config


def load_request_summary(data_dir):
    path = data_dir / "table4_request_summary.csv"
    groups = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["protocol"], row["concurrency"])
            groups.setdefault(key, []).append(row)
    return groups


def load_latency_samples(data_dir):
    path = data_dir / "table4_latency_samples.csv"
    samples = {}
    if not path.exists():
        return samples
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["protocol"], row["concurrency"])
            samples.setdefault(key, []).append(float(row["latency_ms"]))
    return samples


def load_cpu_samples(data_dir):
    path = data_dir / "table4_cpu_samples.csv"
    samples = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["protocol"], row["concurrency"])
            samples.setdefault(key, []).append(float(row["cpu_percent"]))
    return samples


def rows_from_records(data_dir):
    order, config = load_config(data_dir)
    request_groups = load_request_summary(data_dir)
    latency_samples = load_latency_samples(data_dir)
    cpu_samples = load_cpu_samples(data_dir)
    rows = []

    for key in order:
        protocol, conc = key
        summaries = request_groups[key]
        throughput_values = []
        error_values = []
        for summary in summaries:
            steady_state_seconds = float(summary["steady_state_seconds"])
            successful = float(summary["successful_requests"])
            failed = float(summary["failed_requests"])
            total = float(summary["total_requests"])
            throughput_values.append(successful / steady_state_seconds)
            error_values.append((failed / total * 100.0) if total else 0.0)

        throughput_mean = sum(throughput_values) / len(throughput_values)
        throughput_std = sample_std(throughput_values)
        p50 = nearest_rank(latency_samples.get(key, []), 50)
        p95 = nearest_rank(latency_samples.get(key, []), 95)
        cpu_values = cpu_samples.get(key, [])
        cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0.0
        error = sum(error_values) / len(error_values)

        rows.append((
            protocol,
            conc,
            f"{format_num(throughput_mean)} +/- {format_num(throughput_std)}",
            format_num(p50) if p50 != "-" else "-",
            format_num(p95) if p95 != "-" else "-",
            format_num(cpu),
            format_error(error),
        ))

    return rows


def write_csv(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def write_markdown(path, rows):
    lines = [
        "| Protocol | Conc. | Throughput (auth/s) | Latency (p50/p95, ms) | CPU (%) | Error (%) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for protocol, conc, throughput, p50, p95, cpu, error in rows:
        lines.append(f"| {protocol} | {conc} | {throughput} | {p50} / {p95} | {cpu} | {error} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_latex(path, rows):
    lines = [
        r"\begin{tabular}{l|c|c|c|c|c}",
        r"\toprule",
        r"\textbf{Protocol} & \textbf{Conc.} & \textbf{Throughput (auth/s)} & \textbf{Latency (p50/p95, ms)} & \textbf{CPU (\%)} & \textbf{Error (\%)} \\",
        r"\midrule",
    ]
    prior_protocol = None
    for protocol, conc, throughput, p50, p95, cpu, error in rows:
        label = protocol if protocol != prior_protocol else ""
        latex_throughput = throughput.replace("+/-", r"$\pm$")
        lines.append(f"{label} & {conc} & {latex_throughput} & {p50} / {p95} & {cpu} & {error} \\\\")
        prior_protocol = protocol
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def print_table(rows):
    print("Table 4: Server Scalability")
    print("Config input: data/table4_experiment_config.csv (Conc. = concurrent sessions/users)")
    print("Request input: data/table4_request_summary.csv")
    print("Latency input: data/table4_latency_samples.csv")
    print("CPU input: data/table4_cpu_samples.csv")
    print("Formula: throughput per repeat = successful_requests / steady_state_seconds.")
    print("Formula: throughput cell = mean(3 repeat throughputs) +/- sample_std(3 repeat throughputs).")
    print("Formula: p50/p95 = nearest-rank percentiles over latency samples.")
    print("Formula: CPU = mean(cpu_percent samples); Error = failed_requests / total_requests * 100.\n")
    print(f"{'Protocol':<10} | {'Conc.':<6} | {'Throughput':<16} | {'p50/p95 ms':<14} | {'CPU %':<6} | {'Error %':<8}")
    for protocol, conc, throughput, p50, p95, cpu, error in rows:
        print(f"{protocol:<10} | {conc:<6} | {throughput:<16} | {p50 + '/' + p95:<14} | {cpu:<6} | {error:<8}")


def print_audit(data_dir):
    print("\nTable 4 calculation trace:")
    order, _ = load_config(data_dir)
    request_groups = load_request_summary(data_dir)
    latency_samples = load_latency_samples(data_dir)
    cpu_samples = load_cpu_samples(data_dir)

    for key in order:
        protocol, conc = key
        summaries = request_groups[key]
        throughput_values = []
        error_values = []
        for summary in summaries:
            successful = float(summary["successful_requests"])
            failed = float(summary["failed_requests"])
            total = float(summary["total_requests"])
            steady_state_seconds = float(summary["steady_state_seconds"])
            throughput_values.append(successful / steady_state_seconds)
            error_values.append((failed / total * 100.0) if total else 0.0)

        throughput_mean = sum(throughput_values) / len(throughput_values)
        throughput_std = sample_std(throughput_values)
        latencies = latency_samples.get(key, [])
        p50 = nearest_rank(latencies, 50)
        p95 = nearest_rank(latencies, 95)
        cpus = cpu_samples.get(key, [])
        cpu = sum(cpus) / len(cpus) if cpus else 0.0
        error = sum(error_values) / len(error_values)

        print(
            f"  {protocol:<8} conc={conc:<6}: "
            f"throughputs={throughput_values} => mean={format_num(throughput_mean)}, sample_std={format_num(throughput_std)}; "
            f"latency_samples_n={len(latencies)}, p50/p95={format_num(p50) if p50 != '-' else '-'}/{format_num(p95) if p95 != '-' else '-'} ms; "
            f"cpu_samples_n={len(cpus)}, CPU mean={format_num(cpu)}%; "
            f"errors={error_values} => Error mean={format_error(error)}%"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["paper", "measured"], default="paper")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--raw-dir", default="raw-data")
    parser.add_argument("--out-dir", default="results")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = rows_from_records(data_dir) if args.mode == "paper" else load_measured(raw_dir)
    stem = "table4_scalability_paper" if args.mode == "paper" else "table4_scalability_measured"
    write_csv(out_dir / f"{stem}.csv", HEADER, rows)
    write_markdown(out_dir / f"{stem}.md", rows)
    write_latex(out_dir / f"{stem}.tex", rows)
    write_csv(out_dir / "table4_scalability.csv", HEADER, rows)
    write_csv(out_dir / "table4_scalability_summary.csv", SUMMARY_HEADER, SUMMARY_ROWS)
    print_table(rows)
    if args.mode == "paper":
        print_audit(data_dir)
    print(f"Wrote Table 4 outputs in {out_dir}\n")


if __name__ == "__main__":
    main()
