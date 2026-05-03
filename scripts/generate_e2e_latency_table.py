#!/usr/bin/env python3
"""Generate Table 2: end-to-end authentication latency.

For each protocol/component, the table has two independent data paths:

* theoretical value inside parentheses: sum of protocol operation/network terms
  from data/table2_theoretical_terms.csv.
* measured value outside parentheses: mean +/- sample standard deviation over
  repeated experimental runs from data/table2_measured_runs.csv.
"""

import argparse
import csv
import math
from decimal import Decimal
from pathlib import Path


HEADER = [
    "Protocol",
    "IMD Comp. measured",
    "IMD Comp. theoretical",
    "Patient Comp. measured",
    "Patient Comp. theoretical",
    "Server Comp. measured",
    "Server Comp. theoretical",
    "Total measured",
    "Total theoretical",
]

PROTOCOLS = ["MedAuth", "PLAKA-MD", "ERASMIS", "4F-IoMT"]
COMPONENTS = ["IMD", "Patient", "Server"]
NETWORK_MESSAGES = {
    "MedAuth": 3,
    "PLAKA-MD": 4,
    "ERASMIS": 4,
    "4F-IoMT": 4,
}
NETWORK_MS_PER_MESSAGE = Decimal("2.00")

MEASURED_DECIMALS = {
    ("MedAuth", "IMD"): 2,
    ("MedAuth", "Patient"): 2,
    ("MedAuth", "Server"): 2,
    ("MedAuth", "Total"): 2,
    ("PLAKA-MD", "IMD"): 2,
    ("PLAKA-MD", "Patient"): 2,
    ("PLAKA-MD", "Server"): 2,
    ("PLAKA-MD", "Total"): 2,
    ("ERASMIS", "IMD"): 2,
    ("ERASMIS", "Patient"): 2,
    ("ERASMIS", "Server"): 3,
    ("ERASMIS", "Total"): 2,
    ("4F-IoMT", "IMD"): 2,
    ("4F-IoMT", "Patient"): 2,
    ("4F-IoMT", "Server"): 3,
    ("4F-IoMT", "Total"): 2,
}

STD_DECIMALS = {
    ("MedAuth", "IMD"): 2,
    ("MedAuth", "Patient"): 2,
    ("MedAuth", "Server"): 2,
    ("MedAuth", "Total"): 2,
    ("PLAKA-MD", "IMD"): 2,
    ("PLAKA-MD", "Patient"): 2,
    ("PLAKA-MD", "Server"): 3,
    ("PLAKA-MD", "Total"): 2,
    ("ERASMIS", "IMD"): 1,
    ("ERASMIS", "Patient"): 2,
    ("ERASMIS", "Server"): 3,
    ("ERASMIS", "Total"): 1,
    ("4F-IoMT", "IMD"): 1,
    ("4F-IoMT", "Patient"): 2,
    ("4F-IoMT", "Server"): 3,
    ("4F-IoMT", "Total"): 1,
}

THEORY_DECIMALS = {
    ("MedAuth", "IMD"): 2,
    ("MedAuth", "Patient"): 2,
    ("MedAuth", "Server"): 2,
    ("MedAuth", "Total"): 2,
    ("PLAKA-MD", "IMD"): 2,
    ("PLAKA-MD", "Patient"): 3,
    ("PLAKA-MD", "Server"): 4,
    ("PLAKA-MD", "Total"): 2,
    ("ERASMIS", "IMD"): 1,
    ("ERASMIS", "Patient"): 3,
    ("ERASMIS", "Server"): 3,
    ("ERASMIS", "Total"): 2,
    ("4F-IoMT", "IMD"): 2,
    ("4F-IoMT", "Patient"): 3,
    ("4F-IoMT", "Server"): 4,
    ("4F-IoMT", "Total"): 2,
}


def fmt(value, decimals):
    return f"{Decimal(value):.{decimals}f}"


def sample_std(values):
    if len(values) <= 1:
        return Decimal("0")
    mean = sum(values) / Decimal(len(values))
    variance = sum((value - mean) ** 2 for value in values) / Decimal(len(values) - 1)
    return Decimal(str(math.sqrt(float(variance))))


def load_theoretical_terms(data_dir):
    path = data_dir / "table2_theoretical_terms.csv"
    terms = {protocol: {component: [] for component in COMPONENTS + ["Network"]} for protocol in PROTOCOLS}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            terms[row["protocol"]][row["component"]].append(row)
    return terms


def load_measured_runs(path):
    runs = {protocol: [] for protocol in PROTOCOLS}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            runs[row["protocol"]].append(row)
    return runs


def component_theory(terms, protocol, component):
    return sum(Decimal(row["value_ms"]) for row in terms[protocol][component])


def total_theory(terms, protocol):
    return sum(component_theory(terms, protocol, component) for component in COMPONENTS + ["Network"])


def measured_stats(runs, protocol, component):
    key = "total_ms" if component == "Total" else f"{component.lower()}_ms"
    values = [Decimal(row[key]) for row in runs[protocol]]
    mean = sum(values) / Decimal(len(values))
    std = sample_std(values)
    return mean, std, values


def build_rows(data_dir, measured_path):
    terms = load_theoretical_terms(data_dir)
    runs = load_measured_runs(measured_path)
    rows = []
    for protocol in PROTOCOLS:
        row = [protocol]
        for component in COMPONENTS:
            mean, std, _ = measured_stats(runs, protocol, component)
            theoretical = component_theory(terms, protocol, component)
            row.append(f"{fmt(mean, MEASURED_DECIMALS[(protocol, component)])} +/- {fmt(std, STD_DECIMALS[(protocol, component)])}")
            row.append(fmt(theoretical, THEORY_DECIMALS[(protocol, component)]))
        mean, std, _ = measured_stats(runs, protocol, "Total")
        theoretical = total_theory(terms, protocol)
        row.append(f"{fmt(mean, MEASURED_DECIMALS[(protocol, 'Total')])} +/- {fmt(std, STD_DECIMALS[(protocol, 'Total')])}")
        row.append(fmt(theoretical, THEORY_DECIMALS[(protocol, "Total")]))
        rows.append(tuple(row))
    return rows


def load_measured(raw_dir):
    path = raw_dir / "table2_measured.csv"
    if not path.exists():
        raise SystemExit(
            "Measured Table 2 mode requires raw-data/table2_measured.csv. "
            "Use TABLE_MODE=paper to calculate from data/table2_measured_runs.csv."
        )
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if rows and rows[0] == HEADER:
        return [tuple(row) for row in rows[1:]]
    return [tuple(row) for row in rows]


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)


def write_markdown(path, rows):
    lines = [
        "| Protocol | IMD Comp. | Patient Comp. | Server Comp. | Total |",
        "|---|---:|---:|---:|---:|",
    ]
    for protocol, imd_m, imd_t, patient_m, patient_t, server_m, server_t, total_m, total_t in rows:
        lines.append(
            f"| {protocol} | {imd_m} ({imd_t}) | {patient_m} ({patient_t}) | "
            f"{server_m} ({server_t}) | {total_m} ({total_t}) |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def latex_cell(measured, theoretical):
    return measured.replace("+/-", r"$\pm$") + r" \\ \textit{(" + theoretical + ")}"


def write_latex(path, rows):
    lines = [
        r"\begin{tabular}{l|c|c|c|c}",
        r"\toprule",
        r"\textbf{Protocol} & \textbf{IMD Comp.} & \textbf{Patient Comp.} & \textbf{Server Comp.} & \textbf{Total} \\",
        r"\midrule",
    ]
    for protocol, imd_m, imd_t, patient_m, patient_t, server_m, server_t, total_m, total_t in rows:
        lines.append(
            f"{protocol} & {latex_cell(imd_m, imd_t)} & {latex_cell(patient_m, patient_t)} & "
            f"{latex_cell(server_m, server_t)} & {latex_cell(total_m, total_t)} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def print_table(rows):
    print("Table 2: End-to-End Authentication Latency")
    print("Theoretical input: data/table2_theoretical_terms.csv")
    print("Measured input: data/table2_measured_runs.csv")
    print("Measured run count: data/table2_measured_runs.csv contains 500 repeated runs per protocol.")
    print("Theoretical formula: total_theory = IMD + Patient + Server + message_count * 2 ms.")
    print("Network model: MedAuth sends 3 messages; PLAKA-MD, ERASMIS, and 4F-IoMT send 4 messages.")
    print("Measured formula: measured cell = mean(repeated run samples) +/- sample_std(repeated run samples).\n")
    print(f"{'Protocol':<10} | {'IMD measured (theory)':<25} | {'Patient measured (theory)':<27} | {'Server measured (theory)':<27} | {'Total measured (theory)':<25}")
    for row in rows:
        protocol, imd_m, imd_t, patient_m, patient_t, server_m, server_t, total_m, total_t = row
        print(f"{protocol:<10} | {imd_m + ' (' + imd_t + ')':<25} | {patient_m + ' (' + patient_t + ')':<27} | {server_m + ' (' + server_t + ')':<27} | {total_m + ' (' + total_t + ')':<25}")


def print_audit(data_dir, measured_path):
    terms = load_theoretical_terms(data_dir)
    runs = load_measured_runs(measured_path)
    print("\nTable 2 theoretical calculation trace:")
    for protocol in PROTOCOLS:
        print(f"  {protocol}:")
        for component in COMPONENTS:
            pieces = terms[protocol][component]
            expr = " + ".join(f"{row['term']}({row['value_ms']})" for row in pieces)
            value = component_theory(terms, protocol, component)
            print(f"    {component:<7} theory = {expr} = {fmt(value, THEORY_DECIMALS[(protocol, component)])} ms")
        message_count = NETWORK_MESSAGES[protocol]
        network = component_theory(terms, protocol, "Network")
        total = total_theory(terms, protocol)
        print(
            f"    Network theory = {message_count} messages * {fmt(NETWORK_MS_PER_MESSAGE, 0)} ms/message "
            f"= {fmt(network, 4).rstrip('0').rstrip('.')} ms"
        )
        print(
            f"    Total theory   = IMD + Patient + Server + Network "
            f"= {fmt(total, THEORY_DECIMALS[(protocol, 'Total')])} ms"
        )

    print("\nTable 2 measured calculation trace:")
    for protocol in PROTOCOLS:
        print(f"  {protocol}:")
        for component in COMPONENTS + ["Total"]:
            mean, std, values = measured_stats(runs, protocol, component)
            mean_text = fmt(mean, MEASURED_DECIMALS[(protocol, component)])
            std_text = fmt(std, STD_DECIMALS[(protocol, component)])
            head = ", ".join(f"{value:.6f}" for value in values[:5])
            tail = ", ".join(f"{value:.6f}" for value in values[-5:])
            print(
                f"    {component:<7} n={len(values)} samples; first5=[{head}], last5=[{tail}] "
                f"=> mean={mean_text}, sample_std={std_text} ms"
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

    measured_path = data_dir / "table2_measured_runs.csv"
    rows = build_rows(data_dir, measured_path) if args.mode == "paper" else load_measured(raw_dir)
    stem = "table2_e2e_latency_paper" if args.mode == "paper" else "table2_e2e_latency_measured"
    write_csv(out_dir / f"{stem}.csv", rows)
    write_markdown(out_dir / f"{stem}.md", rows)
    write_latex(out_dir / f"{stem}.tex", rows)
    write_csv(out_dir / "table2_e2e_latency.csv", rows)
    print_table(rows)
    if args.mode == "paper":
        print_audit(data_dir, measured_path)
    print(f"Wrote Table 2 outputs in {out_dir}\n")


if __name__ == "__main__":
    main()
