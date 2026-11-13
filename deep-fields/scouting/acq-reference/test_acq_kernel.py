import os
import subprocess
import sys
import unittest
from unittest import mock
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
        # Pure selection (c=0, r=6) with bleed alpha=1/2 equals true conversion (c=1/2, r=6, alpha=0) at all p
        for num in range(0, 11):
            p = Fraction(num, 10)
            y_bleed = acq.observe_contaminated_fraction(p, Fraction(6, 1), Fraction(0, 1), Fraction(1, 2))
            y_conv = acq.observe_contaminated_fraction(p, Fraction(6, 1), Fraction(1, 2), Fraction(0, 1))
            self.assertEqual(y_bleed, y_conv)
        # Measuring p=0 anchor separates them deterministically
        p1, p2 = Fraction(1, 20), Fraction(3, 8)
        y1 = acq.observe_contaminated_fraction(p1, Fraction(6, 1), Fraction(0, 1), Fraction(1, 2))
        y2 = acq.observe_contaminated_fraction(p2, Fraction(6, 1), Fraction(0, 1), Fraction(1, 2))
        self.assertEqual(acq.recover_anchored_parameters(Fraction(1, 2), p1, y1, p2, y2)["c"], 0)
        self.assertEqual(acq.recover_anchored_parameters(Fraction(0, 1), p1, y1, p2, y2)["c"], Fraction(1, 2))

    def test_inadmissible_quotient_edge_rejected(self) -> None:
        # Planted F-11 over-estimating heuristic edge (h(0)=4 > 1 + h(1)=2) must fail closed
        bad = acq.verify_quotient_lower_bound([(0, 1, 1), (1, 2, 2)], {0: 4, 1: 2, 2: 0}, 0, [2])
        self.assertFalse(bad["ok"])
        self.assertEqual(bad["bellman_violations"], 1)
        self.assertIsNone(bad["certified_floor"])

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
        codes = {f["code"] for f in res["findings"]}
        self.assertEqual(
            codes,
            {"TRUST_BYPASS", "SYNTAX_OVERRIDE", "FLOAT_SPEC_CARRIER", "NONLINEAR_OMEGA_PRODUCT", "NON_INIT_TACTIC"},
        )

    def test_python_exact_checker_flags_float_literals(self) -> None:
        res = acq.audit_python_exact_checker("def check(x):\n    return abs(x - 0.5) < 1e-9\n")
        self.assertFalse(res["ok"])


HERE = os.path.dirname(os.path.abspath(__file__))


class TestKernelFailsClosed(unittest.TestCase):
    def test_empty_goal_set_raises(self) -> None:
        with self.assertRaises(ValueError):
            acq.verify_quotient_lower_bound([(0, 1, 1)], {0: 1, 1: 0}, 0, [])

    def test_missing_h_values_raise(self) -> None:
        with self.assertRaises(ValueError):
            acq.verify_quotient_lower_bound([(0, 9, 1)], {0: 1, 1: 0}, 0, [1])
        with self.assertRaises(ValueError):
            acq.verify_quotient_lower_bound([(0, 1, 1)], {0: 1, 1: 0}, 5, [1])
        with self.assertRaises(ValueError):
            acq.verify_quotient_lower_bound([(0, 1, 1)], {0: 1, 1: 0}, 0, [7])

    def test_empty_or_degenerate_shards_raise(self) -> None:
        with self.assertRaises(ValueError):
            acq.evaluate_shift_quotient_pooling([])
        with self.assertRaises(ValueError):
            acq.evaluate_shift_quotient_pooling([([Fraction(1, 1)], [])])

    def test_invalid_domains_raise(self) -> None:
        one = Fraction(1, 1)
        with self.assertRaises(ValueError):
            acq.observe_contaminated_fraction(Fraction(2, 1), one, Fraction(0, 1), Fraction(0, 1))
        with self.assertRaises(ValueError):
            acq.observe_contaminated_fraction(Fraction(1, 2), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1))
        with self.assertRaises(ValueError):
            acq.check_division_free_mitosis(one, one, Fraction(-1, 1), one, one, one, one)

    def test_every_witness_is_checked(self) -> None:
        """Break each witness in turn. The suite must raise, not return a certificate."""
        wrong_pool = {"shard_mean_auc": Fraction(1, 1), "raw_pooled_auc": Fraction(3, 4), "midrank_pooled_auc": Fraction(1, 2)}
        mutations = {
            "check_division_free_mitosis": lambda *a, **k: {"trigger_mitosis": False, "regime": "WRONG"},
            "evaluate_shift_quotient_pooling": lambda *a, **k: wrong_pool,
            "verify_quotient_lower_bound": lambda *a, **k: {"ok": False, "certified_floor": None},
            "gravity_trap_fraction": lambda *a, **k: Fraction(1, 2),
            "audit_lean4_init_module": lambda *a, **k: {"ok": False, "findings": []},
        }
        for name, replacement in mutations.items():
            with self.subTest(mutated=name):
                with mock.patch.object(acq, name, replacement):
                    with self.assertRaises(acq.WitnessFailure):
                        acq.run_portfolio_suite()
        with self.subTest(mutated="soko floor value"):
            ok_but_wrong = lambda *a, **k: {"ok": True, "certified_floor": 99}
            with mock.patch.object(acq, "verify_quotient_lower_bound", ok_but_wrong):
                with self.assertRaises(acq.WitnessFailure):
                    acq.run_portfolio_suite()
        with self.subTest(mutated="C25 ceiling divisor"):
            with mock.patch.object(acq, "EPS_C25_DIVISOR", 5):
                with self.assertRaises(acq.WitnessFailure):
                    acq.run_portfolio_suite()

    def test_cli_exits_nonzero_and_prints_no_ok_on_failed_witness(self) -> None:
        bad = lambda *a, **k: {"trigger_mitosis": False, "regime": "WRONG"}
        with mock.patch.object(acq, "check_division_free_mitosis", bad):
            with mock.patch("sys.stdout") as out, mock.patch("sys.stderr"):
                code = acq.main()
        self.assertEqual(code, 1)
        printed = "".join(str(c.args[0]) for c in out.write.call_args_list if c.args)
        self.assertNotIn("ACQ_REFERENCE_SUITE_OK", printed)

    def test_cli_runs_with_assertions_stripped(self) -> None:
        """Witness checks must not depend on `assert`, which `python -O` removes."""
        proc = subprocess.run(
            [sys.executable, "-I", "-O", os.path.join(HERE, "acq_kernel.py")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ACQ_REFERENCE_SUITE_OK", proc.stdout)


if __name__ == "__main__":
    unittest.main()
