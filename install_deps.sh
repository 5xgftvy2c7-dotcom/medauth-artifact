#!/usr/bin/env bash
set -euo pipefail

echo "=== Dependency notes for MedAuth microbenchmark ==="
echo "Required for the portable smoke test: gcc, make, python3, go."
echo "On Ubuntu 22.04:"
echo "  sudo apt update"
echo "  sudo apt install -y build-essential make python3 golang"
echo
echo "Optional MSP430 reproduction path:"
echo "  sudo apt install -y msp430-gcc msp430-binutils msp430-libc qemu-system-msp430"
echo "Then run: make -C platform/imd-msp430 msp430"
