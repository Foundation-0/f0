import os
import sys
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import acq_kernel as acq


class TestAnchoredConservationQuotient(unittest.TestCase):
    def test_portfolio_witness_suite(self) -> None:
        cert = acq.run_portfolio_suite()
        self.assertTrue(cert["lean_init_audit_ok"])
        self.assertEqual(cert["project_asma_c25_ceiling"], "10179/563920")
        self.assertEqual(cert["weft_dust_regime"], "OPTIMIZER_STUCK")
        self.assertEqual(cert["weft_midrank_restored_auc"], "1")
        self.assertEqual(cert["soko_certified_floor"], 3)

    def test_unanchored_pgl2_indistinguishability_and_anchor_resolution(self) -> None:
        for num in range(0, 11):
            p = Fraction(num, 10)
            y_bleed = acq.observe_contaminated_fraction(p, Fraction(6, 1), Fraction(0, 1), Fraction(1, 2))
            y_conv = acq.observe_contaminated_fraction(p, Fraction(6, 1), Fraction(1, 2), Fraction(0, 1))
            self.assertEqual(y_bleed, y_conv)
        p1, p2 = Fraction(1, 20), Fraction(3, 8)
        y1 = acq.observe_contaminated_fraction(p1, Fraction(6, 1), Fraction(0, 1), Fraction(1, 2))
        y2 = acq.observe_contaminated_fraction(p2, Fraction(6, 1), Fraction(0, 1), Fraction(1, 2))
        self.assertEqual(acq.recover_anchored_parameters(Fraction(1, 2), p1, y1, p2, y2)["c"], 0)
        self.assertEqual(acq.recover_anchored_parameters(Fraction(0, 1), p1, y1, p2, y2)["c"], Fraction(1, 2))

    def test_inadmissible_quotient_edge_rejected(self) -> None:
        bad = acq.verify_quotient_lower_bound([(0, 1, 1), (1, 2, 2)], {0: 4, 1: 2, 2: 0}, 0, [2])
        self.assertFalse(bad["ok"])
        self.assertEqual(bad["bellman_violations"], 1)

    def test_lean_init_auditor_catches_adversarial_mutations(self) -> None:
        adv_src = (
            'def x : Int := 1; axiom bad : False\n'
            'notation:50 a " = " b => True\n'
            'structure S where f : Float\n'
            'theorem t (p c : Int) : 320 * c * (p * p) = 0 := by omega\n'
            'theorem t2 (a b : Int) : a * b = b * a := by ac_rfl\n'
        )
        res = acq.audit_lean4_init_module(adv_src, label="planted")
        self.assertFalse(res["ok"])
        self.assertEqual(
            {f["code"] for f in res["findings"]},
            {"TRUST_BYPASS", "SYNTAX_OVERRIDE", "FLOAT_SPEC_CARRIER", "NONLINEAR_OMEGA_PRODUCT", "NON_INIT_TACTIC"},
        )

    def test_python_exact_checker_flags_float_literals(self) -> None:
        self.assertFalse(acq.audit_python_exact_checker("def check(x):\n    return abs(x - 0.5) < 1e-9\n")["ok"])


if __name__ == "__main__":
    unittest.main()
