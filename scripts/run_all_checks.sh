#!/usr/bin/env bash
set -e

echo "Running healthy-band scan..."
python scripts/scan_healthy_band.py

echo "Checking spin-2 projector structure..."
python scripts/check_spin2_structure.py

echo "All checks completed."
