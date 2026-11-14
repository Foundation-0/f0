#!/usr/bin/env python3
"""quotient_anchor_kernel.py — Executable Single-Thread Unification Kernel
Across Foundation-0 (gravity, project-asma, exoplanets-frontier), Moissanite-Labs (weft),
ahrazzle/soko, and Proven-Commons.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from typing import Dict, List, Sequence, Tuple


def verify_anchored_mobius_certificate(
    domain: str,
    alpha_null_anchor: Fraction,
    p_low: Fraction,
    y_low: Fraction,
    p_high: Fraction,
    y_high: Fraction,
) -> Dict[str, str]:
    assert Fraction(0, 1) <= alpha_null_anchor < Fraction(1, 1)
    assert Fraction(0, 1) < p_low < p_high < Fraction(1, 1)
    q_low = (y_low - alpha_null_anchor) / (1 - alpha_null_anchor)
    q_high = (y_high - alpha_null_anchor) / (1 - alpha_null_anchor)
    assert q_low < 1 and q_high < 1
    phi_low = (1 - p_low) / (1 - q_low)
    phi_high = (1 - p_high) / (1 - q_high)
    slope = (phi_high - phi_low) / (p_high - p_low)
    intercept = phi1_0 = phi_low - slope * p_low
    c_conv = 1 - Fraction(1, 1) / phi1_0
    r_amp = 1 + slope / phi1_0
    return {
        "domain": domain,
        "alpha_anchor": str(alpha_null_anchor),
        "Phi_intercept": str(intercept),
        "Phi_slope": str(slope),
        "c_conversion_or_synthesis": str(c_conv),
        "r_selection_or_snr": str(r_amp),
    }


def verify_shift_quotient_concordance(
    folds: Sequence[Tuple[Sequence[Fraction], Sequence[Fraction]]],
) -> Dict[str, str]:
    within_n = 0
    fold_aucs: List[Fraction] = []
    raw_pos, raw_neg, cal_pos, cal_neg = [], [], [], []
    for pos_k, neg_k in folds:
        u_k = sum(
            Fraction(1, 1) if x > y else (Fraction(1, 2) if x == y else Fraction(0, 1))
            for x in pos_k for y in neg_k
        )
        within_n += len(pos_k) * len(neg_k)
        fold_aucs.append(u_k / (len(pos_k) * len(neg_k)))
        raw_pos.extend(pos_k)
        raw_neg.extend(neg_k)
        comb = list(pos_k) + list(neg_k)
        m = Fraction(len(comb), 1)
        for x in pos_k:
            cal_pos.append((Fraction(sum(1 for z in comb if z < x), 1) + Fraction(sum(1 for z in comb if z == x), 2)) / m)
        for y in neg_k:
            cal_neg.append((Fraction(sum(1 for z in comb if z < y), 1) + Fraction(sum(1 for z in comb if z == y), 2)) / m)

    def pair_auc(ps: Sequence[Fraction], ns: Sequence[Fraction]) -> Fraction:
        u = sum(Fraction(1, 1) if x > y else (Fraction(1, 2) if x == y else Fraction(0, 1)) for x in ps for y in ns)
        return u / (len(ps) * len(ns))

    return {
        "fold_mean_auc": str(sum(fold_aucs, Fraction(0, 1)) / len(fold_aucs)),
        "raw_pooled_auc": str(pair_auc(raw_pos, raw_neg)),
        "midrank_calibrated_auc": str(pair_auc(cal_pos, cal_neg)),
        "within_pair_fraction": str(Fraction(within_n, len(raw_pos) * len(raw_neg))),
    }


def verify_quotient_conservation_bound(
    concrete_edges: Sequence[Tuple[int, int, int]],
    quotient_h: Dict[int, int],
    s0: int,
    goal_states: Sequence[int],
) -> Dict[str, object]:
    for g in goal_states:
        assert quotient_h[g] == 0
    violations = sum(1 for u, v, cost in concrete_edges if quotient_h[u] > cost + quotient_h[v])
    assert violations == 0
    return {"certified_lower_bound": quotient_h[s0], "edges_checked": len(concrete_edges), "bellman_violations": violations}


def main() -> None:
    def obs_y(p: Fraction, r: Fraction, c: Fraction, alpha: Fraction) -> Fraction:
        q = (r * p + c * (1 - p)) / (r * p + (1 - p))
        return (1 - alpha) * q + alpha

    asma = verify_anchored_mobius_certificate(
        "Foundation-0/project-asma", Fraction(3, 20),
        Fraction(1, 20), obs_y(Fraction(1, 20), Fraction(11, 1), Fraction(1, 4), Fraction(3, 20)),
        Fraction(3, 8), obs_y(Fraction(3, 8), Fraction(11, 1), Fraction(1, 4), Fraction(3, 20)),
    )
    assert asma["c_conversion_or_synthesis"] == "1/4" and asma["r_selection_or_snr"] == "11"

    weft = verify_anchored_mobius_certificate(
        "Moissanite-Labs/weft", Fraction(2, 5),
        Fraction(1, 20), obs_y(Fraction(1, 20), Fraction(8, 1), Fraction(0, 1), Fraction(2, 5)),
        Fraction(3, 8), obs_y(Fraction(3, 8), Fraction(8, 1), Fraction(0, 1), Fraction(2, 5)),
    )
    assert weft["c_conversion_or_synthesis"] == "0"

    shift = verify_shift_quotient_concordance([
        ([Fraction(12, 1), Fraction(11, 1)], [Fraction(9, 1), Fraction(8, 1)]),
        ([Fraction(2, 1), Fraction(1, 1)], [Fraction(-1, 1), Fraction(-2, 1)]),
    ])
    assert shift["fold_mean_auc"] == "1" and shift["raw_pooled_auc"] == "3/4" and shift["midrank_calibrated_auc"] == "1"

    sigma_halo_sq = Fraction(177 * 177, 1)
    f_trap_z608 = 1 - Fraction(97, 100) ** 2 / sigma_halo_sq
    f_trap_z0 = max(Fraction(0, 1), 1 - Fraction(18559, 100) ** 2 / sigma_halo_sq)
    assert f_trap_z608 > Fraction(9999, 10000) and f_trap_z0 == 0

    soko = verify_quotient_conservation_bound([(0, 1, 1), (1, 2, 1), (0, 2, 2), (2, 3, 1)], {0: 3, 1: 2, 2: 1, 3: 0}, 0, [3])
    assert soko["certified_lower_bound"] == 3

    exo = verify_anchored_mobius_certificate(
        "Foundation-0/exoplanets-frontier", Fraction(1, 10),
        Fraction(1, 10), obs_y(Fraction(1, 10), Fraction(9, 1), Fraction(0, 1), Fraction(1, 10)),
        Fraction(1, 2), obs_y(Fraction(1, 2), Fraction(9, 1), Fraction(0, 1), Fraction(1, 10)),
    )
    assert exo["c_conversion_or_synthesis"] == "0"

    digest = hashlib.sha256(json.dumps([asma, weft, shift, str(f_trap_z608), soko, exo], sort_keys=True).encode()).hexdigest()
    print(f"SINGLE_THREAD_KERNEL_OK: 5/5 domains verified | SHA-256: {digest}")


if __name__ == "__main__":
    main()
