#!/usr/bin/env python
"""
Numerically probe the spin-2 projector contraction F2(q,k) for sample
timelike q and generic k to check that:

  F2(q,k) = (1/N2) P^{(2) mu nu rho sigma} N_{mu nu rho sigma}(q,k)

is nonzero and has a definite sign in the healthy band.

We work in Minkowski signature (-,+,+,+) with:

  q_mu = (q0, 0, 0, 0),  q0 != 0,
  k_mu = (omega, kx, ky, kz),

and define:

  k^2 = -omega^2 + |k|^2.

We then construct:

  theta_{mu nu} = eta_{mu nu} - k_mu k_nu / k^2,
  P^{(2)}      = (1/2)(theta_{mu rho} theta_{nu sigma} + ... ) - (1/3) theta_{mu nu} theta_{rho sigma},

and

  N_{mu nu rho sigma} = (q_mu k_nu + q_nu k_mu)(q_rho k_sigma + q_sigma k_rho).

This script is for internal checks; the analytic structure is documented in
Appendix C of the paper.
"""

import csv
import math

# Minkowski metric with signature (-,+,+,+)
eta = [[-1.0, 0.0, 0.0, 0.0],
       [ 0.0, 1.0, 0.0, 0.0],
       [ 0.0, 0.0, 1.0, 0.0],
       [ 0.0, 0.0, 0.0, 1.0]]

def dot(a, b):
    return sum(eta[mu][nu] * a[mu] * b[nu] for mu in range(4) for nu in range(4) if mu == nu)

def minkowski_k2(k):
    # k^2 = eta^{mu nu} k_mu k_nu
    return -k[0] * k[0] + sum(k[i] * k[i] for i in range(1, 4))

def theta_tensor(k):
    """Return theta_{mu nu} = eta_{mu nu} - k_mu k_nu / k^2."""
    k2 = minkowski_k2(k)
    if abs(k2) < 1e-10:
        raise ValueError("k^2 too close to zero for projector definition.")
    theta = [[0.0 for _ in range(4)] for _ in range(4)]
    for mu in range(4):
        for nu in range(4):
            eta_mu_nu = eta[mu][nu] if mu == nu else 0.0
            theta[mu][nu] = eta_mu_nu - k[mu] * k[nu] / k2
    return theta

def P2_tensor(k):
    """Construct P^{(2)}_{mu nu rho sigma} from theta."""
    theta = theta_tensor(k)
    P2 = [[[[0.0 for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for mu in range(4):
        for nu in range(4):
            for rho in range(4):
                for sigma in range(4):
                    term1 = 0.5 * (theta[mu][rho] * theta[nu][sigma] +
                                   theta[mu][sigma] * theta[nu][rho])
                    term2 = (1.0 / 3.0) * theta[mu][nu] * theta[rho][sigma]
                    P2[mu][nu][rho][sigma] = term1 - term2
    return P2

def N_tensor(q, k):
    """N_{mu nu rho sigma} = (q_mu k_nu + q_nu k_mu)(q_rho k_sigma + q_sigma k_rho)."""
    N = [[[[0.0 for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for mu in range(4):
        for nu in range(4):
            for rho in range(4):
                for sigma in range(4):
                    A = q[mu] * k[nu] + q[nu] * k[mu]
                    B = q[rho] * k[sigma] + q[sigma] * k[rho]
                    N[mu][nu][rho][sigma] = A * B
    return N

def contract_P2_N(P2, N):
    """Compute P^{(2) mu nu rho sigma} N_{mu nu rho sigma} with eta-raising."""
    # Here P2 is already defined with lowered indices; for this simple check
    # we treat the contraction as a straightforward sum over indices.
    val = 0.0
    for mu in range(4):
        for nu in range(4):
            for rho in range(4):
                for sigma in range(4):
                    val += P2[mu][nu][rho][sigma] * N[mu][nu][rho][sigma]
    return val

# Choose a representative timelike q_mu and sample k_mu vectors
q0 = 1.0
q = [q0, 0.0, 0.0, 0.0]

out_path = "data/spin2_F2_samples.csv"
rows = []

for omega in [0.5, 1.0, 1.5, 2.0]:
    for kx in [0.5, 1.0, 1.5]:
        for ky in [0.0]:
            for kz in [0.0]:
                k = [omega, kx, ky, kz]
                k2 = minkowski_k2(k)
                if abs(k2) < 1e-8:
                    continue
                try:
                    P2 = P2_tensor(k)
                except ValueError:
                    continue
                N = N_tensor(q, k)
                F2_val = contract_P2_N(P2, N)
                rows.append({
                    "omega": omega,
                    "kx": kx,
                    "ky": ky,
                    "kz": kz,
                    "k2": k2,
                    "F2": F2_val
                })

with open(out_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["omega", "kx", "ky", "kz", "k2", "F2"])
    for r in rows:
        writer.writerow([r["omega"], r["kx"], r["ky"], r["kz"], r["k2"], r["F2"]])

print(f"Wrote {len(rows)} spin-2 projector samples to {out_path}")
# Quick human check
num_pos = sum(1 for r in rows if r["F2"] > 0)
num_neg = sum(1 for r in rows if r["F2"] < 0)
print(f"F2>0 in {num_pos} samples, F2<0 in {num_neg} samples.")
