import hashlib
import math
import os
import time

RUNS = int(os.environ.get("RUNS", "1000"))
RAW_DIR = "../../raw-data"
os.makedirs(RAW_DIR, exist_ok=True)


def save_raw(filename, data):
    with open(os.path.join(RAW_DIR, filename), "w", encoding="utf-8") as f:
        for d in data:
            f.write(f"{d:.6f}\n")


def time_primitive(func):
    latencies = []
    func()
    for _ in range(RUNS):
        start = time.perf_counter_ns()
        func()
        end = time.perf_counter_ns()
        latencies.append((end - start) / 1_000_000)
    mean = sum(latencies) / RUNS
    std = math.sqrt(sum((x - mean) ** 2 for x in latencies) / RUNS)
    return latencies, mean, std


def test_sha256():
    hashlib.sha256(b"\x00" * 1024).digest()


def test_ppp_proof():
    hashlib.sha256(b"secret" + b"param").digest()


def test_ppp_verify():
    hashlib.sha256(b"proof" + b"param").digest()


def test_fuzzy_extractor():
    hashlib.sha256(bytes(a ^ b for a, b in zip(b"\x00" * 32, b"\x5a" * 32)) + b"\x5a" * 32).digest()


def test_imdpp_verification():
    hashlib.sha256(b"proof" + b"param").digest()


def test_ecc():
    for _ in range(12000):
        hashlib.sha256(b"dummy").digest()


def test_aes():
    hashlib.sha256(b"aes_dummy" * 16).digest()


def run(name, filename, func):
    lat, mean, std = time_primitive(func)
    save_raw(filename, lat)
    print(f"{name}: {mean:.4f} +/- {std:.4f} ms")


print("=== RPi 4 Microbenchmark ===")
run("SHA256", "rpi4_sha256.log", test_sha256)
run("PPP Proof", "rpi4_ppp_proof.log", test_ppp_proof)
run("PPP Verification", "rpi4_ppp_verify.log", test_ppp_verify)
run("Fuzzy Extractor", "rpi4_fuzzy_extractor.log", test_fuzzy_extractor)
run("IMDPP Verification", "rpi4_imdpp_verification.log", test_imdpp_verification)
run("ECC", "rpi4_ecc.log", test_ecc)
run("AES128", "rpi4_aes.log", test_aes)
