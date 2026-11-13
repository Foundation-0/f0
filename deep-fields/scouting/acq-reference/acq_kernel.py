#!/usr/bin/env python3
"""acq_kernel.py - Zero-dependency reference implementation of the four-gate
Anchored Conservation Quotient (ACQ) verification architecture.

Unifies:
  - Gate 1: Channel-bleed deflation against an independent c = 0 control & within-shard mid-rank pooling
  - Gate 2: Step-admissible quotient lower-bound & ordinal budget conservation
  - Gate 3: Survival-ratio affine linearization & division-free regime triggers
  - Gate 4: Comment-aware Lean 4 `Init` & Python checker anti-tautology auditing
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import os
import re
import sys
from typing import Dict, List, Optional, Sequence, Tuple


# Typed-in constants. Neither is derived in this file.
# EPS_C25_DIVISOR: the "/4" in the C25 ceiling is a divisor typed in to match the
# project-asma figure 10179/563920; it is not derived here.
# C25_SEPARATION_THRESHOLD: 1/60 is a benchmark choice (the separation bar used
# in project-asma), not a quantity this file computes.
EPS_C25_DIVISOR = 4
C25_SEPARATION_THRESHOLD = Fraction(1, 60)


class WitnessFailure(RuntimeError):
    """Raised when a reference witness does not hold. Never disabled by `python -O`."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WitnessFailure(message)


# ---------------------------------------------------------------------------
# Gate 1 & Gate 3: Null-Boundary Bleed Deflation + Survival-Ratio Linearization
# ---------------------------------------------------------------------------
def observe_contaminated_fraction(p: Fraction, r: Fraction, c: Fraction, alpha: Fraction) -> Fraction:
    """Post-assay / proxy-channel output y(p) = (1 - alpha) * q(p, r, c) + alpha."""
    if not (Fraction(0, 1) <= p <= Fraction(1, 1)):
        raise ValueError("Mixture p must lie in [0, 1].")
    if r <= 0 or not (Fraction(0, 1) <= c < Fraction(1, 1)) or not (Fraction(0, 1) <= alpha < Fraction(1, 1)):
        raise ValueError("Invalid (r, c, alpha) domain.")
    q = (r * p + c * (1 - p)) / (r * p + (1 - p))
    return (1 - alpha) * q + alpha


@dataclass(frozen=True)
class NullControl:
    """A bleed measurement taken on an independent specimen with known c = 0.

    The model is y(p) = alpha + (1 - alpha) * q(p, r, c). At p = 0, q = c, so a
    sample's own p = 0 endpoint is alpha + (1 - alpha) * c. That mixes bleed with
    conversion and cannot anchor alpha. A valid anchor is a different specimen
    that has no conversion (for example a recombinant paralog control with
    c = 0), read on the same channel as the sample, so y_control = alpha.

    The kernel checks the declared provenance (distinct specimen, same channel,
    known conversion 0). It cannot tell whether the declared specimen really has
    c = 0; that is a wet-lab or data-provenance fact the caller must supply.
    """

    y: Fraction
    specimen_id: str
    channel_id: str
    known_conversion: Fraction


def recover_anchored_parameters(
    control: Optional[NullControl],
    sample_id: str,
    channel_id: str,
    p_low: Fraction,
    y_low: Fraction,
    p_high: Fraction,
    y_high: Fraction,
) -> Dict[str, Fraction]:
    """Deflates the channel bleed measured on `control` and recovers exact `(r, c)`
    from two mixtures of the sample via
    `Phi(p) = (1 - p) / (1 - q_corr(p)) = ((r - 1)/(1 - c))*p + 1/(1 - c)`.

    Raises ValueError when the control is missing, is not a NullControl, is the
    sample itself, has a nonzero known conversion, or is on another channel.
    """
    if control is None or not isinstance(control, NullControl):
        raise ValueError("An independent c = 0 control measurement (NullControl) is required.")
    if control.specimen_id == sample_id:
        raise ValueError("The sample's own p = 0 endpoint cannot anchor alpha; use an independent c = 0 control.")
    if control.channel_id != channel_id:
        raise ValueError("Control and sample must be read on the same channel.")
    if control.known_conversion != 0:
        raise ValueError("The control specimen must have known conversion c = 0.")
    alpha_null = control.y
    if not (Fraction(0, 1) <= alpha_null < Fraction(1, 1)):
        raise ValueError("Control bleed must lie in [0, 1).")
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
    """Compares shard-mean concordance, raw pooled concordance, and shift-invariant
    within-shard mid-rank percentile pooled concordance in exact `Fraction`.
    """
    if not shards:
        raise ValueError("At least one shard required.")

    shard_aucs: List[Fraction] = []
    raw_pos: List[Fraction] = []
    raw_neg: List[Fraction] = []
    cal_pos: List[Fraction] = []
    cal_neg: List[Fraction] = []
    within_pairs = 0

    def mann_whitney(ps: Sequence[Fraction], ns: Sequence[Fraction]) -> Fraction:
        u = Fraction(0, 1)
        for x in ps:
            for y in ns:
                if x > y:
                    u += 1
                elif x == y:
                    u += Fraction(1, 2)
        return u / (len(ps) * len(ns))

    for pos_k, neg_k in shards:
        if not pos_k or not neg_k:
            raise ValueError("Each shard requires non-empty positive and negative sets.")
        shard_aucs.append(mann_whitney(pos_k, neg_k))
        within_pairs += len(pos_k) * len(neg_k)
        raw_pos.extend(pos_k)
        raw_neg.extend(neg_k)

        comb = list(pos_k) + list(neg_k)
        n_k = Fraction(len(comb), 1)
        for x in pos_k:
            less = sum(1 for z in comb if z < x)
            eq = sum(1 for z in comb if z == x)
            cal_pos.append((Fraction(less, 1) + Fraction(eq, 2)) / n_k)
        for y in neg_k:
            less = sum(1 for z in comb if z < y)
            eq = sum(1 for z in comb if z == y)
            cal_neg.append((Fraction(less, 1) + Fraction(eq, 2)) / n_k)

    total_pairs = len(raw_pos) * len(raw_neg)
    return {
        "shard_mean_auc": sum(shard_aucs, Fraction(0, 1)) / len(shard_aucs),
        "raw_pooled_auc": mann_whitney(raw_pos, raw_neg),
        "midrank_pooled_auc": mann_whitney(cal_pos, cal_neg),
        "within_pair_share": Fraction(within_pairs, total_pairs),
        "cross_pair_share": Fraction(total_pairs - within_pairs, total_pairs),
    }


# ---------------------------------------------------------------------------
# Gate 2: Quotient Homomorphism Conservation & Division-Free Mitosis Gate
# ---------------------------------------------------------------------------
def verify_quotient_lower_bound(
    edges: Sequence[Tuple[int, int, int]],
    h_quotient: Dict[int, int],
    start_state: int,
    goal_states: Sequence[int],
) -> Dict[str, object]:
    """Fail-closed verifier for step-admissible quotient lower bounds.

    Raises ValueError on an empty goal set or on any state that appears in an
    edge, as the start, or as a goal without an `h` value. A missing value is an
    input error, not a pass.
    """
    if not goal_states:
        raise ValueError("Goal set must be non-empty.")
    if start_state not in h_quotient:
        raise ValueError(f"Start state {start_state} has no h value.")
    for g in goal_states:
        if g not in h_quotient:
            raise ValueError(f"Goal state {g} has no h value.")
        if h_quotient[g] != 0:
            return {"ok": False, "reason": f"Goal state {g} has non-zero h={h_quotient[g]}"}
    violations = []
    for u, v, cost in edges:
        if u not in h_quotient or v not in h_quotient:
            raise ValueError(f"Edge ({u}, {v}) uses a state with no h value.")
        if cost < 0 or h_quotient[u] > cost + h_quotient[v]:
            violations.append((u, v, cost, h_quotient[u], h_quotient[v]))
    return {
        "ok": len(violations) == 0,
        "certified_floor": h_quotient[start_state] if len(violations) == 0 else None,
        "edges_checked": len(edges),
        "bellman_violations": len(violations),
    }


def check_division_free_mitosis(
    err: Fraction,
    err_floor: Fraction,
    grad_par: Fraction,
    par_ceil: Fraction,
    grad_orth: Fraction,
    orth_floor: Fraction,
    mdr_threshold: Fraction,
) -> Dict[str, object]:
    """Division-free cross-multiplied MDR trigger with explicit orthogonal gradient floor."""
    if grad_par < 0 or grad_orth < 0 or par_ceil < 0 or orth_floor <= 0 or mdr_threshold <= 0:
        raise ValueError("Invalid gradient or threshold domain.")
    if err <= err_floor:
        return {"trigger_mitosis": False, "regime": "TASK_CEILING"}
    if grad_par <= par_ceil and grad_orth >= orth_floor and grad_orth >= mdr_threshold * grad_par:
        return {"trigger_mitosis": True, "regime": "CAPACITY_LIMIT"}
    if grad_par <= par_ceil:
        return {"trigger_mitosis": False, "regime": "OPTIMIZER_STUCK"}
    return {"trigger_mitosis": False, "regime": "ACTIVE_DESCENT"}


# ---------------------------------------------------------------------------
# Gate 4: Static Stock-Init Lean 4 & Dual-Oracle Python AST Hygiene Gate
# ---------------------------------------------------------------------------
FORBIDDEN_LEAN_TRUST = {"sorry", "admit", "axiom", "opaque", "native_decide"}
FORBIDDEN_LEAN_SYNTAX = {"notation", "infix", "infixl", "infixr", "prefix", "postfix", "macro", "elab"}
FORBIDDEN_LEAN_ATTRS = {"extern", "implemented_by", "csimp"}
NON_INIT_LEAN_TACTICS = {"ac_rfl", "ring", "ring_nf", "linarith", "nlinarith", "polyrith", "norm_num"}


def _strip_lean_comments_keep_strings(src: str) -> str:
    out: List[str] = []
    i, n, depth = 0, len(src), 0
    while i < n:
        if depth > 0:
            if src[i:i + 2] == "/-":
                depth += 1; i += 2
            elif src[i:i + 2] == "-/":
                depth -= 1; i += 2
            else:
                if src[i] == "\n": out.append("\n")
                i += 1
        else:
            if src[i:i + 2] == "/-":
                depth = 1; i += 2
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
        tokens = re.findall(r"@\[[^\]]+\]|[A-Za-z_][A-Za-z0-9_']*|\S", line)
        for tok in tokens:
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
    findings: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            findings.append(f"FLOAT_LITERAL:{node.value}")
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append("BARE_EXCEPT")
    return {"ok": len(findings) == 0, "findings": findings}


def gravity_trap_fraction(sigma_star: Fraction, sigma_halo: Fraction) -> Fraction:
    """max(0, 1 - (sigma_star / sigma_halo)^2). Arithmetic on typed-in inputs."""
    return max(Fraction(0, 1), 1 - (sigma_star / sigma_halo) ** 2)


def run_portfolio_suite() -> Dict[str, object]:
    """Compute every witness and check each one. Raises WitnessFailure on the first miss."""
    here = os.path.dirname(os.path.abspath(__file__))
    lean_path = os.path.join(here, "AnchoredConservationQuotient.lean")
    with open(lean_path, encoding="utf-8") as fh:
        lean_source = fh.read()
    lean_audit = audit_lean4_init_module(lean_source, label="AnchoredConservationQuotient.lean")
    _require(lean_audit["ok"] is True, f"Lean source lint failed: {lean_audit}")

    # 1. project-asma: (1/20, 3/8) C25 separation & paralog bleed recovery
    pL, pH = Fraction(1, 20), Fraction(3, 8)
    dS = observe_contaminated_fraction(pH, Fraction(16, 1), Fraction(0, 1), Fraction(0, 1)) - \
         observe_contaminated_fraction(pL, Fraction(16, 1), Fraction(0, 1), Fraction(0, 1))
    dC25 = observe_contaminated_fraction(pH, Fraction(11, 1), Fraction(1, 4), Fraction(0, 1)) - \
           observe_contaminated_fraction(pL, Fraction(11, 1), Fraction(1, 4), Fraction(0, 1))
    eps_c25 = abs(dS - dC25) / EPS_C25_DIVISOR
    _require(eps_c25 == Fraction(10179, 563920), f"C25 ceiling is {eps_c25}, expected 10179/563920")
    _require(eps_c25 > C25_SEPARATION_THRESHOLD, f"C25 ceiling {eps_c25} does not exceed {C25_SEPARATION_THRESHOLD}")

    paralog_control = NullControl(Fraction(3, 20), "recombinant-paralog-control", "assay-channel", Fraction(0, 1))
    rec_asma = recover_anchored_parameters(
        paralog_control, "snapshot-mixtures", "assay-channel", pL,
        observe_contaminated_fraction(pL, Fraction(11, 1), Fraction(1, 4), Fraction(3, 20)),
        pH,
        observe_contaminated_fraction(pH, Fraction(11, 1), Fraction(1, 4), Fraction(3, 20)),
    )
    _require(rec_asma["c"] == Fraction(1, 4) and rec_asma["r"] == Fraction(11, 1),
             f"paralog anchor recovery gave c={rec_asma['c']}, r={rec_asma['r']}")

    # 2. weft: 3e-12 dust rejection + shard rank pooling
    dust_gate = check_division_free_mitosis(
        Fraction(12, 100), Fraction(5, 100),
        Fraction(0, 1), Fraction(1, 1000),
        Fraction(3, 10**12), Fraction(1, 1000), Fraction(5, 2),
    )
    _require(dust_gate["trigger_mitosis"] is False and dust_gate["regime"] == "OPTIMIZER_STUCK",
             f"dust gate returned {dust_gate}")

    shift_res = evaluate_shift_quotient_pooling([
        ([Fraction(12, 1), Fraction(11, 1)], [Fraction(9, 1), Fraction(8, 1)]),
        ([Fraction(2, 1), Fraction(1, 1)], [Fraction(-1, 1), Fraction(-2, 1)]),
    ])
    _require(shift_res["shard_mean_auc"] == 1, f"shard mean AUC is {shift_res['shard_mean_auc']}")
    _require(shift_res["raw_pooled_auc"] == Fraction(3, 4), f"raw pooled AUC is {shift_res['raw_pooled_auc']}")
    _require(shift_res["midrank_pooled_auc"] == 1, f"mid-rank pooled AUC is {shift_res['midrank_pooled_auc']}")

    # 3. gravity: Cosmic-Dawn z=6.08 vs z=0 Press-Schechter trapping inversion
    f_z608 = gravity_trap_fraction(Fraction(97, 100), Fraction(177, 1))
    f_z0 = gravity_trap_fraction(Fraction(18559, 100), Fraction(177, 1))
    _require(f_z608 > Fraction(9999, 10000), f"z=6.08 trap fraction is {f_z608}")
    _require(f_z0 == 0, f"z=0 trap fraction is {f_z0}")

    # 4. soko: quotient lower bound on a four-state toy graph (not a soko room)
    soko_lb = verify_quotient_lower_bound(
        [(0, 1, 1), (1, 2, 1), (0, 2, 2), (2, 3, 1)],
        {0: 3, 1: 2, 2: 1, 3: 0}, start_state=0, goal_states=[3],
    )
    _require(soko_lb["ok"] is True, f"toy quotient check failed: {soko_lb}")
    _require(soko_lb["certified_floor"] == 3, f"toy certified floor is {soko_lb['certified_floor']}")

    # 5. exoplanets-frontier: null-control deflation on a synthetic mixture
    null_control = NullControl(Fraction(1, 10), "inverted-null-control", "flux-channel", Fraction(0, 1))
    rec_exo = recover_anchored_parameters(
        null_control, "synthetic-mixtures", "flux-channel", Fraction(1, 10),
        observe_contaminated_fraction(Fraction(1, 10), Fraction(9, 1), Fraction(0, 1), Fraction(1, 10)),
        Fraction(1, 2),
        observe_contaminated_fraction(Fraction(1, 2), Fraction(9, 1), Fraction(0, 1), Fraction(1, 10)),
    )
    _require(rec_exo["c"] == 0 and rec_exo["r"] == 9,
             f"null-control recovery gave c={rec_exo['c']}, r={rec_exo['r']}")

    return {
        "schema": "foundation-0.f0.acq-reference-certificates.v1",
        "lean_init_audit_ok": True,
        "project_asma_c25_ceiling": str(eps_c25),
        "weft_dust_regime": dust_gate["regime"],
        "weft_midrank_restored_auc": str(shift_res["midrank_pooled_auc"]),
        "gravity_cosmic_dawn_trap_fraction": str(f_z608),
        "soko_certified_floor": soko_lb["certified_floor"],
        "exoplanets_null_deflated_c": str(rec_exo["c"]),
    }


def main() -> int:
    try:
        cert = run_portfolio_suite()
    except WitnessFailure as exc:
        print(f"ACQ_REFERENCE_SUITE_FAILED | {exc}", file=sys.stderr)
        return 1
    digest = hashlib.sha256(json.dumps(cert, sort_keys=True).encode("utf-8")).hexdigest()
    print(f"ACQ_REFERENCE_SUITE_OK | SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
