#!/usr/bin/env python3
"""acq_kernel.py - Zero-dependency reference implementation of the four-gate
Anchored Conservation Quotient (ACQ) verification architecture.
"""

from __future__ import annotations

import ast
from fractions import Fraction
import hashlib
import json
import os
import re
from typing import Dict, List, Sequence, Tuple


def observe_contaminated_fraction(p: Fraction, r: Fraction, c: Fraction, alpha: Fraction) -> Fraction:
    if not (Fraction(0, 1) <= p <= Fraction(1, 1)):
        raise ValueError("Mixture p must lie in [0, 1].")
    if r <= 0 or not (Fraction(0, 1) <= c < Fraction(1, 1)) or not (Fraction(0, 1) <= alpha < Fraction(1, 1)):
        raise ValueError("Invalid (r, c, alpha) domain.")
    q = (r * p + c * (1 - p)) / (r * p + (1 - p))
    return (1 - alpha) * q + alpha


def recover_anchored_parameters(
    alpha_null: Fraction,
    p_low: Fraction,
    y_low: Fraction,
    p_high: Fraction,
    y_high: Fraction,
) -> Dict[str, Fraction]:
    if not (Fraction(0, 1) <= alpha_null < Fraction(1, 1)):
        raise ValueError("Null anchor alpha must lie in [0, 1).")
    if not (Fraction(0, 1) < p_low < p_high < Fraction(1, 1)):
        raise ValueError("Requires 0 < p_low < p_high < 1.")
    q_low = (y_low - alpha_null) / (1 - alpha_null)
    q_high = (y_high - alpha_null) / (1 - alpha_null)
    if not (Fraction(0, 1) <= q_low < Fraction(1, 1)) or not (Fraction(0, 1) <= q_high < Fraction(1, 1)):
        raise ValueError("Deflated fraction outside [0, 1).")
    phi_low = (1 - p_low) / (1 - q_low)
    phi_high = (1 - p_high) / (1 - q_high)
    slope = (phi_high - phi_low) / (p_high - p_low)
    intercept = phi_low - slope * p_low
    if intercept <= 0:
        raise ValueError("Non-positive survival intercept.")
    return {
        "alpha_null": alpha_null,
        "Phi_intercept": intercept,
        "Phi_slope": slope,
        "c": 1 - Fraction(1, 1) / intercept,
        "r": 1 + slope / intercept,
    }


def evaluate_shift_quotient_pooling(
    shards: Sequence[Tuple[Sequence[Fraction], Sequence[Fraction]]],
) -> Dict[str, Fraction]:
    if not shards:
        raise ValueError("At least one shard required.")
    shard_aucs: List[Fraction] = []
    raw_pos, raw_neg, cal_pos, cal_neg = [], [], [], []
    within_pairs = 0

    def mann_whitney(ps: Sequence[Fraction], ns: Sequence[Fraction]) -> Fraction:
        u = sum(Fraction(1, 1) if x > y else (Fraction(1, 2) if x == y else Fraction(0, 1)) for x in ps for y in ns)
        return u / (len(ps) * len(ns))

    for pos_k, neg_k in shards:
        shard_aucs.append(mann_whitney(pos_k, neg_k))
        within_pairs += len(pos_k) * len(neg_k)
        raw_pos.extend(pos_k)
        raw_neg.extend(neg_k)
        comb = list(pos_k) + list(neg_k)
        n_k = Fraction(len(comb), 1)
        for x in pos_k:
            cal_pos.append((Fraction(sum(1 for z in comb if z < x), 1) + Fraction(sum(1 for z in comb if z == x), 2)) / n_k)
        for y in neg_k:
            cal_neg.append((Fraction(sum(1 for z in comb if z < y), 1) + Fraction(sum(1 for z in comb if z == y), 2)) / n_k)

    total_pairs = len(raw_pos) * len(raw_neg)
    return {
        "shard_mean_auc": sum(shard_aucs, Fraction(0, 1)) / len(shard_aucs),
        "raw_pooled_auc": mann_whitney(raw_pos, raw_neg),
        "midrank_pooled_auc": mann_whitney(cal_pos, cal_neg),
        "within_pair_share": Fraction(within_pairs, total_pairs),
        "cross_pair_share": Fraction(total_pairs - within_pairs, total_pairs),
    }


def verify_quotient_lower_bound(
    edges: Sequence[Tuple[int, int, int]],
    h_quotient: Dict[int, int],
    start_state: int,
    goal_states: Sequence[int],
) -> Dict[str, object]:
    for g in goal_states:
        if h_quotient.get(g) != 0:
            return {"ok": False, "reason": f"Goal state {g} non-zero"}
    violations = [(u, v, c) for u, v, c in edges if c < 0 or h_quotient[u] > c + h_quotient[v]]
    return {
        "ok": len(violations) == 0,
        "certified_floor": h_quotient[start_state] if not violations else None,
        "edges_checked": len(edges),
        "bellman_violations": len(violations),
    }


def check_division_free_mitosis(
    err: Fraction, err_floor: Fraction, grad_par: Fraction, par_ceil: Fraction,
    grad_orth: Fraction, orth_floor: Fraction, mdr_threshold: Fraction,
) -> Dict[str, object]:
    if err <= err_floor:
        return {"trigger_mitosis": False, "regime": "TASK_CEILING"}
    if grad_par <= par_ceil and grad_orth >= orth_floor and grad_orth >= mdr_threshold * grad_par:
        return {"trigger_mitosis": True, "regime": "CAPACITY_LIMIT"}
    if grad_par <= par_ceil:
        return {"trigger_mitosis": False, "regime": "OPTIMIZER_STUCK"}
    return {"trigger_mitosis": False, "regime": "ACTIVE_DESCENT"}


FORBIDDEN_LEAN_TRUST = {"sorry", "admit", "axiom", "opaque", "native_decide"}
FORBIDDEN_LEAN_SYNTAX = {"notation", "infix", "infixl", "infixr", "prefix", "postfix", "macro", "elab"}
FORBIDDEN_LEAN_ATTRS = {"extern", "implemented_by", "csimp"}
NON_INIT_LEAN_TACTICS = {"ac_rfl", "ring", "ring_nf", "linarith", "nlinarith", "polyrith", "norm_num"}


def _strip_lean_comments_keep_strings(src: str) -> str:
    out: List[str] = []
    i, n, depth = 0, len(src), 0
    while i < n:
        if depth > 0:
            if src[i:i + 2] == "/-": depth += 1; i += 2
            elif src[i:i + 2] == "-/": depth -= 1; i += 2
            else:
                if src[i] == "\n": out.append("\n")
                i += 1
        else:
            if src[i:i + 2] == "/-": depth = 1; i += 2
            elif src[i:i + 2] == "--":
                while i < n and src[i] != "\n": i += 1
            elif src[i] == '"':
                out.append('"S"'); i += 1
                while i < n and src[i] != '"':
                    if src[i] == "\\" and i + 1 < n: i += 2
                    else:
                        if src[i] == "\n": out.append("\n")
                        i += 1
                if i < n: i += 1
            else:
                out.append(src[i]); i += 1
    return "".join(out)


def audit_lean4_init_module(source: str, label: str = "<lean>") -> Dict[str, object]:
    cleaned = _strip_lean_comments_keep_strings(source)
    findings: List[Dict[str, object]] = []
    for lineno, line in enumerate(cleaned.splitlines(), 1):
        for tok in re.findall(r"@\[[^\]]+\]|[A-Za-z_][A-Za-z0-9_']*|\S", line):
            if tok in FORBIDDEN_LEAN_TRUST:
                findings.append({"line": lineno, "code": "TRUST_BYPASS", "detail": tok})
            elif tok in FORBIDDEN_LEAN_SYNTAX:
                findings.append({"line": lineno, "code": "SYNTAX_OVERRIDE", "detail": tok})
            elif tok.startswith("@["):
                for attr in FORBIDDEN_LEAN_ATTRS:
                    if re.search(rf"\b{attr}\b", tok[2:-1]):
                        findings.append({"line": lineno, "code": "UNSOUND_ATTR", "detail": tok})
            elif tok in NON_INIT_LEAN_TACTICS:
                findings.append({"line": lineno, "code": "NON_INIT_TACTIC", "detail": tok})
        if re.match(r"^\s*import\s+(Mathlib|Std)\b", line):
            findings.append({"line": lineno, "code": "NON_INIT_IMPORT", "detail": line.strip()})
        if re.search(r":\s*Float\b", line):
            findings.append({"line": lineno, "code": "FLOAT_SPEC_CARRIER", "detail": line.strip()})
        if re.search(r":=\s*by\s+omega\b", line):
            lhs = line.split(":=")[0]
            if re.search(r"\b\d+\s*\*\s*[A-Za-z_]\w*\s*\*\s*\(", lhs):
                findings.append({"line": lineno, "code": "NONLINEAR_OMEGA_PRODUCT", "detail": lhs.strip()})
    return {"label": label, "ok": len(findings) == 0, "findings": findings}


def audit_python_exact_checker(source: str) -> Dict[str, object]:
    tree = ast.parse(source)
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            findings.append(f"FLOAT_LITERAL:{node.value}")
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append("BARE_EXCEPT")
    return {"ok": len(findings) == 0, "findings": findings}


def run_portfolio_suite() -> Dict[str, object]:
    here = os.path.dirname(os.path.abspath(__file__))
    lean_audit = audit_lean4_init_module(open(os.path.join(here, "AnchoredConservationQuotient.lean"), encoding="utf-8").read())
    assert lean_audit["ok"]
    pL, pH = Fraction(1, 20), Fraction(3, 8)
    dS = observe_contaminated_fraction(pH, Fraction(16, 1), Fraction(0, 1), Fraction(0, 1)) - observe_contaminated_fraction(pL, Fraction(16, 1), Fraction(0, 1), Fraction(0, 1))
    dC25 = observe_contaminated_fraction(pH, Fraction(11, 1), Fraction(1, 4), Fraction(0, 1)) - observe_contaminated_fraction(pL, Fraction(11, 1), Fraction(1, 4), Fraction(0, 1))
    eps_c25 = abs(dS - dC25) / 4
    assert eps_c25 == Fraction(10179, 563920) > Fraction(1, 60)
    dust = check_division_free_mitosis(Fraction(12, 100), Fraction(5, 100), Fraction(0, 1), Fraction(1, 1000), Fraction(3, 10**12), Fraction(1, 1000), Fraction(5, 2))
    shift = evaluate_shift_quotient_pooling([([Fraction(12, 1), Fraction(11, 1)], [Fraction(9, 1), Fraction(8, 1)]), ([Fraction(2, 1), Fraction(1, 1)], [Fraction(-1, 1), Fraction(-2, 1)])])
    f_z608 = 1 - Fraction(97, 100) ** 2 / Fraction(177 * 177, 1)
    soko = verify_quotient_lower_bound([(0, 1, 1), (1, 2, 1), (0, 2, 2), (2, 3, 1)], {0: 3, 1: 2, 2: 1, 3: 0}, 0, [3])
    exo = recover_anchored_parameters(Fraction(1, 10), Fraction(1, 10), observe_contaminated_fraction(Fraction(1, 10), Fraction(9, 1), Fraction(0, 1), Fraction(1, 10)), Fraction(1, 2), observe_contaminated_fraction(Fraction(1, 2), Fraction(9, 1), Fraction(0, 1), Fraction(1, 10)))
    return {
        "schema": "foundation-0.f0.acq-reference-certificates.v1",
        "lean_init_audit_ok": True,
        "project_asma_c25_ceiling": str(eps_c25),
        "weft_dust_regime": dust["regime"],
        "weft_midrank_restored_auc": str(shift["midrank_pooled_auc"]),
        "gravity_cosmic_dawn_trap_fraction": str(f_z608),
        "soko_certified_floor": soko["certified_floor"],
        "exoplanets_null_deflated_c": str(exo["c"]),
    }


if __name__ == "__main__":
    cert = run_portfolio_suite()
    print("ACQ_REFERENCE_SUITE_OK | SHA-256:", hashlib.sha256(json.dumps(cert, sort_keys=True).encode()).hexdigest())
