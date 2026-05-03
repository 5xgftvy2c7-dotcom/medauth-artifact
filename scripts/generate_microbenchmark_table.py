#!/usr/bin/env python3
"""Generate the paper-aligned microbenchmark table.

The package supports two output modes:

* paper: emit the reference values reported in the manuscript table.
* measured: summarize local raw timing logs when available.

The paper mode is intentionally explicit. It is useful for checking that the
artifact table schema and expected values match the manuscript, while measured
mode remains the path for raw local benchmark data.
"""

import argparse
import csv
import math
from pathlib import Path


HEADER = ["Operation", "IMD (MSP430)", "Patient (RPi 4)", "Server (i7)"]


def format_profile(mean, std):
    if mean == "" or std == "":
        return "N/A"
    return f"{mean} +/- {std}"


def load_profiles(data_dir):
    path = data_dir / "table1_primitive_profiles.csv"
    profiles = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            profiles[(row["primitive"], row["entity"])] = format_profile(row["mean_ms"], row["std_ms"])
    return profiles


def profile(profiles, primitive, entity):
    return profiles.get((primitive, entity), "N/A")


def paper_rows(data_dir):
    profiles = load_profiles(data_dir)
    return [
        ("SHA-256 (1 KB)", profile(profiles, "sha256_1kb", "imd"), profile(profiles, "sha256_1kb", "patient"), profile(profiles, "sha256_1kb", "server")),
        ("PUF Simulation", profile(profiles, "puf_simulation", "imd"), "N/A", "N/A"),
        ("Fuzzy Extractor", profile(profiles, "fuzzy_extractor", "imd"), profile(profiles, "fuzzy_extractor", "patient"), profile(profiles, "fuzzy_extractor", "server")),
        ("ECC Point Multiplication", profile(profiles, "ecc_point_mult", "imd"), profile(profiles, "ecc_point_mult", "patient"), profile(profiles, "ecc_point_mult", "server")),
        ("PPP Proof (Gen/Ver)", f"{profile(profiles, 'ppp_gen', 'imd')} / N/A", f"N/A / {profile(profiles, 'ppp_ver', 'patient')}", f"{profile(profiles, 'ppp_gen', 'server')} / N/A"),
        ("MESAP Proof (Gen/Ver)", f"N/A / {profile(profiles, 'mesap_ver', 'imd')}", "N/A / N/A", f"{profile(profiles, 'mesap_gen', 'server')} / N/A"),
        ("IMDPP Proof (Gen/Ver)", f"{profile(profiles, 'imdpp_gen', 'imd')} / N/A", f"N/A / {profile(profiles, 'imdpp_ver', 'patient')}", "N/A / N/A"),
    ]


def mean_std(raw_dir, filename, precision=4):
    path = raw_dir / filename
    if not path.exists():
        return "N/A"
    values = [float(line.strip()) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not values:
        return "N/A"
    mean = sum(values) / len(values)
    std = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))
    return f"{mean:.{precision}f} +/- {std:.{precision}f}"


def measured_rows(raw_dir):
    patient_fuzzy = mean_std(raw_dir, "rpi4_fuzzy_extractor.log")
    if patient_fuzzy == "N/A":
        patient_fuzzy = mean_std(raw_dir, "rpi4_imdpp_verification.log")

    server_fuzzy = mean_std(raw_dir, "i7_fuzzy_extractor.log")
    if server_fuzzy == "N/A":
        server_fuzzy = mean_std(raw_dir, "i7_sha256.log")

    return [
        ("SHA-256 (1 KB)", mean_std(raw_dir, "imd_sha256.log"), mean_std(raw_dir, "rpi4_sha256.log"), mean_std(raw_dir, "i7_sha256.log")),
        ("PUF Simulation", mean_std(raw_dir, "imd_puf.log"), "N/A", "N/A"),
        ("Fuzzy Extractor", mean_std(raw_dir, "imd_fuzzy_extractor.log"), patient_fuzzy, server_fuzzy),
        ("ECC Point Multiplication", mean_std(raw_dir, "imd_ecc.log"), mean_std(raw_dir, "rpi4_ecc.log"), mean_std(raw_dir, "i7_ecc.log")),
        ("PPP Proof (Gen/Ver)", f"{mean_std(raw_dir, 'imd_ppp_proof.log')} / N/A", f"N/A / {mean_std(raw_dir, 'rpi4_ppp_verify.log')}", f"{mean_std(raw_dir, 'i7_ppp_verification.log')} / N/A"),
        ("MESAP Proof (Gen/Ver)", f"N/A / {mean_std(raw_dir, 'imd_mesap_verification.log')}", "N/A / N/A", f"{mean_std(raw_dir, 'i7_mesap_generation.log')} / N/A"),
        ("IMDPP Proof (Gen/Ver)", f"{mean_std(raw_dir, 'imd_imdpp_proof.log')} / N/A", f"N/A / {mean_std(raw_dir, 'rpi4_imdpp_verification.log')}", "N/A / N/A"),
    ]


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)


def write_markdown(path, rows):
    lines = [
        "| Operation | IMD (MSP430) | Patient (RPi 4) | Server (i7) |",
        "|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def latex_cell(cell):
    return cell.replace("+/-", r"$\pm$")


def write_latex(path, rows):
    lines = [
        r"\begin{tabular}{l|c|c|c}",
        r"\toprule",
        r"\textbf{Operation} & \textbf{IMD (MSP430)} & \textbf{Patient (RPi 4)} & \textbf{Server (i7)} \\",
        r"\midrule",
    ]
    for operation, imd, patient, server in rows:
        lines.append(f"{operation} & {latex_cell(imd)} & {latex_cell(patient)} & {latex_cell(server)} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def print_table(rows):
    print("Table 1: Cryptographic Primitives Execution Time")
    print("Input: data/table1_primitive_profiles.csv")
    print("Formula: each cell = packaged mean_ms +/- packaged std_ms for the requested primitive/entity.")
    print("Rows with Gen/Ver combine two primitive records into one manuscript cell.\n")
    for row in [HEADER] + list(rows):
        print(f"{row[0]:<30} | {row[1]:<24} | {row[2]:<24} | {row[3]:<24}")


def print_audit(data_dir):
    profiles = load_profiles(data_dir)
    checks = [
        ("SHA-256 IMD", "sha256_1kb", "imd"),
        ("SHA-256 Patient", "sha256_1kb", "patient"),
        ("SHA-256 Server", "sha256_1kb", "server"),
        ("PUF IMD", "puf_simulation", "imd"),
        ("Fuzzy IMD", "fuzzy_extractor", "imd"),
        ("ECC IMD", "ecc_point_mult", "imd"),
        ("PPP Gen IMD", "ppp_gen", "imd"),
        ("PPP Ver Patient", "ppp_ver", "patient"),
        ("PPP Gen Server", "ppp_gen", "server"),
        ("MESAP Ver IMD", "mesap_ver", "imd"),
        ("MESAP Gen Server", "mesap_gen", "server"),
        ("IMDPP Gen IMD", "imdpp_gen", "imd"),
        ("IMDPP Ver Patient", "imdpp_ver", "patient"),
    ]
    print("\nTable 1 calculation trace:")
    for label, primitive, entity in checks:
        print(f"  {label:<20} = {profile(profiles, primitive, entity)}")


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

    rows = paper_rows(data_dir) if args.mode == "paper" else measured_rows(raw_dir)
    stem = "table_microbenchmark_paper" if args.mode == "paper" else "table_microbenchmark_measured"

    write_csv(out_dir / f"{stem}.csv", rows)
    write_markdown(out_dir / f"{stem}.md", rows)
    write_latex(out_dir / f"{stem}.tex", rows)
    write_csv(out_dir / "table_microbenchmark.csv", rows)
    print_table(rows)
    if args.mode == "paper":
        print_audit(data_dir)
    print(f"\nWrote {args.mode} table outputs in {out_dir}")


if __name__ == "__main__":
    main()
