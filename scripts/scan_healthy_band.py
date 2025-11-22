#!/usr/bin/env python
"""
Scan a simple grid in (Pprime, P2prime) and check the healthy-band conditions:

  Z_s = P'(X0) > 0,
  Z_t = P'(X0) + 2 X0 P''(X0) > 0,
  c_s^2 = Z_s / Z_t > 0.

Here X0 is treated as a fixed positive number setting the background scale.
This script is purely illustrative and does not assume a specific P(X).
"""

import csv
import math

# Background X0 (choose a representative positive value)
X0 = 1.0

# Scan ranges for P'(X0) and P''(X0)
PPRIME_MIN, PPRIME_MAX, PPRIME_STEP = -2.0, 2.0, 0.1
P2PRIME_MIN, P2PRIME_MAX, P2PRIME_STEP = -2.0, 2.0, 0.1

out_path = "data/healthy_band_scan.csv"

def frange(start, stop, step):
    x = start
    # be generous with end condition to avoid floating point glitches
    while x <= stop + 1e-9:
        yield x
        x += step

with open(out_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Pprime", "P2prime", "Zs", "Zt", "cs2", "ghost_ok", "grad_ok"])
    for Pprime in frange(PPRIME_MIN, PPRIME_MAX, PPRIME_STEP):
        for P2prime in frange(P2PRIME_MIN, P2PRIME_MAX, P2PRIME_STEP):
            Zs = Pprime
            Zt = Pprime + 2.0 * X0 * P2prime
            ghost_ok = Zt > 0.0
            grad_ok = Zs > 0.0
            cs2 = None
            if ghost_ok:
                cs2 = Zs / Zt
            writer.writerow([
                f"{Pprime:.3f}",
                f"{P2prime:.3f}",
                f"{Zs:.3f}",
                f"{Zt:.3f}",
                "" if cs2 is None else f"{cs2:.3f}",
                int(ghost_ok),
                int(grad_ok),
            ])

print(f"Written healthy-band scan to {out_path}")
