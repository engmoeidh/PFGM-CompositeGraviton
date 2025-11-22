#!/usr/bin/env python
"""
Generate data-driven figures and LaTeX tables from the CSV files in data/:

  - data/healthy_band_scan.csv
  - data/spin2_F2_samples.csv

Outputs:

  Figures:
    figures/fig_healthy_band_scan.png   (stable vs unstable points)
    figures/fig_spin2_F2_vs_k2.png      (F2 vs k^2)

  Tables (LaTeX):
    results/table_healthy_band_stats.tex
    results/table_spin2_F2_stats.tex

This version uses only the Python standard library + matplotlib (no pandas).
"""

import os
import csv

import matplotlib.pyplot as plt


ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(ROOT)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
FIG_DIR = os.path.join(PROJECT_ROOT, "figures")
RES_DIR = os.path.join(PROJECT_ROOT, "results")

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)


# ---------- Loaders ----------

def load_healthy_band():
    path = os.path.join(DATA_DIR, "healthy_band_scan.csv")
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    Pprime = [float(r["Pprime"]) for r in rows]
    P2prime = [float(r["P2prime"]) for r in rows]
    Zs     = [float(r["Zs"])     for r in rows]
    Zt     = [float(r["Zt"])     for r in rows]
    ghost_ok = [int(r["ghost_ok"]) for r in rows]
    grad_ok  = [int(r["grad_ok"])  for r in rows]
    return Pprime, P2prime, Zs, Zt, ghost_ok, grad_ok


def load_spin2_F2():
    path = os.path.join(DATA_DIR, "spin2_F2_samples.csv")
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    omega = [float(r["omega"]) for r in rows]
    kx    = [float(r["kx"])    for r in rows]
    ky    = [float(r["ky"])    for r in rows]
    kz    = [float(r["kz"])    for r in rows]
    k2    = [float(r["k2"])    for r in rows]
    F2    = [float(r["F2"])    for r in rows]
    return omega, kx, ky, kz, k2, F2


# ---------- Healthy band figure & table ----------

def make_fig_healthy_band(Pprime, P2prime, ghost_ok, grad_ok):
    X0 = 1.0  # same as in scan_healthy_band.py
    x_vals = Pprime
    y_vals = [p + 2.0 * X0 * p2 for p, p2 in zip(Pprime, P2prime)]

    stable_mask   = [ (g==1 and r==1) for g, r in zip(ghost_ok, grad_ok) ]
    unstable_mask = [ not s for s in stable_mask ]

    x_stable  = [x for x, s in zip(x_vals, stable_mask)   if s]
    y_stable  = [y for y, s in zip(y_vals, stable_mask)   if s]
    x_unst    = [x for x, s in zip(x_vals, unstable_mask) if s]
    y_unst    = [y for y, s in zip(y_vals, unstable_mask) if s]

    plt.figure()
    if x_unst:
        plt.scatter(x_unst, y_unst, s=10, alpha=0.4, label="unstable")
    if x_stable:
        plt.scatter(x_stable, y_stable, s=10, alpha=0.8, label="healthy band")
    plt.axhline(0.0, linestyle="--")
    plt.axvline(0.0, linestyle="--")
    plt.xlabel("P'(X0)")
    plt.ylabel("P'(X0) + 2 X0 P''(X0)")
    plt.title("Healthy band in (P'(X0), P'(X0)+2 X0 P''(X0)) space")
    plt.legend(loc="best")

    out_path = os.path.join(FIG_DIR, "fig_healthy_band_scan.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Wrote healthy band figure to {out_path}")


def make_table_healthy_band_stats(Pprime, ghost_ok, grad_ok):
    total = len(Pprime)
    stable_mask = [ (g==1 and r==1) for g, r in zip(ghost_ok, grad_ok) ]
    n_stable = sum(1 for s in stable_mask if s)
    frac_stable = n_stable / total if total > 0 else float("nan")

    out_path = os.path.join(RES_DIR, "table_healthy_band_stats.tex")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("% Auto-generated from data/healthy_band_scan.csv\n")
        f.write("\\begin{table}[t]\n")
        f.write("  \\centering\n")
        f.write("  \\begin{tabular}{l c}\n")
        f.write("    \\hline\\hline\n")
        f.write("    Quantity & Value \\\\\n")
        f.write("    \\hline\n")
        f.write(f"    Total grid points & {total} \\\\\n")
        f.write(f"    Stable points ($Z_t>0$, $Z_s>0$) & {n_stable} \\\\\n")
        f.write(f"    Fraction stable & {frac_stable:.3f} \\\\\n")
        f.write("    \\hline\\hline\n")
        f.write("  \\end{tabular}\n")
        f.write("  \\caption{Summary of the healthy-band scan in the\n")
        f.write("  $(P'(X_0),P''(X_0))$ plane.}\n")
        f.write("  \\label{tab:healthy_band_stats}\n")
        f.write("\\end{table}\n")
    print(f"Wrote healthy band stats table to {out_path}")


# ---------- Spin-2 F2 figure & table ----------

def make_fig_spin2_F2(k2, F2):
    plt.figure()
    plt.scatter(k2, F2, s=40)
    plt.axhline(0.0, linestyle="--")
    plt.xlabel(r"$k^2$")
    plt.ylabel(r"$F_2(q,k)$")
    plt.title("Spin--2 projector contraction $F_2(q,k)$ vs $k^2$")

    out_path = os.path.join(FIG_DIR, "fig_spin2_F2_vs_k2.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Wrote spin-2 F2 figure to {out_path}")


def make_table_spin2_F2_stats(F2):
    total = len(F2)
    n_pos  = sum(1 for v in F2 if v > 0.0)
    n_neg  = sum(1 for v in F2 if v < 0.0)
    n_zero = sum(1 for v in F2 if abs(v) < 1e-12)
    if total > 0:
        F2_min = min(F2)
        F2_max = max(F2)
    else:
        F2_min = float("nan")
        F2_max = float("nan")

    out_path = os.path.join(RES_DIR, "table_spin2_F2_stats.tex")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("% Auto-generated from data/spin2_F2_samples.csv\n")
        f.write("\\begin{table}[t]\n")
        f.write("  \\centering\n")
        f.write("  \\begin{tabular}{l c}\n")
        f.write("    \\hline\\hline\n")
        f.write("    Quantity & Value \\\\\n")
        f.write("    \\hline\n")
        f.write(f"    Total samples & {total} \\\\\n")
        f.write(f"    $F_2>0$ & {n_pos} \\\\\n")
        f.write(f"    $F_2<0$ & {n_neg} \\\\\n")
        f.write(f"    $F_2\\approx 0$ & {n_zero} \\\\\n")
        f.write(f"    $\\min F_2$ & {F2_min:.6g} \\\\\n")
        f.write(f"    $\\max F_2$ & {F2_max:.6g} \\\\\n")
        f.write("    \\hline\\hline\n")
        f.write("  \\end{tabular}\n")
        f.write("  \\caption{Summary of the spin--2 projector contraction samples\n")
        f.write("  $F_2(q,k)$ used to illustrate the sign and magnitude of the\n")
        f.write("  spin--2 coefficient in the healthy band.}\n")
        f.write("  \\label{tab:spin2_F2_stats}\n")
        f.write("\\end{table}\n")
    print(f"Wrote spin-2 F2 stats table to {out_path}")


# ---------- Main ----------

def main():
    # Healthy band
    Pprime, P2prime, Zs, Zt, ghost_ok, grad_ok = load_healthy_band()
    make_fig_healthy_band(Pprime, P2prime, ghost_ok, grad_ok)
    make_table_healthy_band_stats(Pprime, ghost_ok, grad_ok)

    # Spin-2 F2
    omega, kx, ky, kz, k2, F2 = load_spin2_F2()
    make_fig_spin2_F2(k2, F2)
    make_table_spin2_F2_stats(F2)

    print("All figures and tables generated.")


if __name__ == "__main__":
    main()
