import os
import subprocess
import sys
import unittest
from unittest import mock
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import acq_kernel as acq


CHANNEL = "assay-channel"


def control(y: Fraction) -> acq.NullControl:
    return acq.NullControl(y, "independent-c0-control", CHANNEL, Fraction(0, 1))


class TestAnchoredConservationQuotient(unittest.TestCase):
    def test_portfolio_witness_suite(self) -> None:
        cert = acq.run_portfolio_suite()
        self.assertTrue(cert["lean_source_lint_ok"])
        self.assertEqual(cert["project_asma_c25_ceiling"], "10179/563920")
        self.assertEqual(cert["weft_dust_regime"], "OPTIMIZER_STUCK")
        self.assertEqual(cert["weft_midrank_restored_auc"], "1")
        self.assertEqual(cert["soko_certified_floor"], 3)

    def test_unanchored_pgl2_indistinguishability(self) -> None:
        """Pure selection with bleed 1/2 equals true conversion c = 1/2 at every p."""
        for num in range(0, 11):
            p = Fraction(num, 10)
            y_bleed = acq.observe_contaminated_fraction(p, Fraction(6, 1), Fraction(0, 1), Fraction(1, 2))
            y_conv = acq.observe_contaminated_fraction(p, Fraction(6, 1), Fraction(1, 2), Fraction(0, 1))
            self.assertEqual(y_bleed, y_conv)

    def test_independent_control_separates_bleed_from_conversion(self) -> None:
        r, p1, p2 = Fraction(6, 1), Fraction(1, 20), Fraction(3, 8)
        # Bleed world: c = 0, alpha = 1/2. The independent c = 0 control reads 1/2.
        y1 = acq.observe_contaminated_fraction(p1, r, Fraction(0, 1), Fraction(1, 2))
        y2 = acq.observe_contaminated_fraction(p2, r, Fraction(0, 1), Fraction(1, 2))
        bleed = acq.recover_anchored_parameters(control(Fraction(1, 2)), "sample", CHANNEL, p1, y1, p2, y2)
        self.assertEqual((bleed["c"], bleed["r"]), (0, r))
        # Conversion world: c = 1/2, alpha = 0. The independent control reads 0.
        y1 = acq.observe_contaminated_fraction(p1, r, Fraction(1, 2), Fraction(0, 1))
        y2 = acq.observe_contaminated_fraction(p2, r, Fraction(1, 2), Fraction(0, 1))
        conv = acq.recover_anchored_parameters(control(Fraction(0, 1)), "sample", CHANNEL, p1, y1, p2, y2)
        self.assertEqual((conv["c"], conv["r"]), (Fraction(1, 2), r))

    def test_conversion_recovered_with_nonzero_bleed(self) -> None:
        r, c, alpha = Fraction(6, 1), Fraction(1, 2), Fraction(1, 10)
        p1, p2 = Fraction(1, 20), Fraction(3, 8)
        y1 = acq.observe_contaminated_fraction(p1, r, c, alpha)
        y2 = acq.observe_contaminated_fraction(p2, r, c, alpha)
        rec = acq.recover_anchored_parameters(control(alpha), "sample", CHANNEL, p1, y1, p2, y2)
        self.assertEqual((rec["c"], rec["r"]), (c, r))

    def test_sample_own_endpoint_is_rejected_as_anchor(self) -> None:
        r, c, alpha = Fraction(6, 1), Fraction(1, 2), Fraction(0, 1)
        p1, p2 = Fraction(1, 20), Fraction(3, 8)
        endpoint = acq.observe_contaminated_fraction(Fraction(0, 1), r, c, alpha)
        self.assertEqual(endpoint, Fraction(1, 2))  # conversion shows up as apparent bleed
        y1 = acq.observe_contaminated_fraction(p1, r, c, alpha)
        y2 = acq.observe_contaminated_fraction(p2, r, c, alpha)
        own = acq.NullControl(endpoint, "sample", CHANNEL, Fraction(0, 1))
        with self.assertRaises(ValueError):
            acq.recover_anchored_parameters(own, "sample", CHANNEL, p1, y1, p2, y2)

    def test_why_the_endpoint_cannot_anchor(self) -> None:
        """If the endpoint is passed off as an independent control, conversion is erased.

        The kernel checks declared provenance only. This test records the failure
        the provenance check exists to prevent.
        """
        r, c = Fraction(6, 1), Fraction(1, 2)
        p1, p2 = Fraction(1, 20), Fraction(3, 8)
        endpoint = acq.observe_contaminated_fraction(Fraction(0, 1), r, c, Fraction(0, 1))
        y1 = acq.observe_contaminated_fraction(p1, r, c, Fraction(0, 1))
        y2 = acq.observe_contaminated_fraction(p2, r, c, Fraction(0, 1))
        disguised = acq.NullControl(endpoint, "other-name", CHANNEL, Fraction(0, 1))
        self.assertEqual(acq.recover_anchored_parameters(disguised, "sample", CHANNEL, p1, y1, p2, y2)["c"], 0)

    def test_missing_or_invalid_control_raises(self) -> None:
        p1, p2 = Fraction(1, 20), Fraction(3, 8)
        y1, y2 = Fraction(1, 5), Fraction(1, 2)
        args = ("sample", CHANNEL, p1, y1, p2, y2)
        with self.assertRaises(ValueError):
            acq.recover_anchored_parameters(None, *args)
        with self.assertRaises(ValueError):
            acq.recover_anchored_parameters(Fraction(0, 1), *args)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            acq.recover_anchored_parameters(acq.NullControl(Fraction(0, 1), "ctrl", CHANNEL, Fraction(1, 4)), *args)
        with self.assertRaises(ValueError):
            acq.recover_anchored_parameters(acq.NullControl(Fraction(0, 1), "ctrl", "other-channel", Fraction(0, 1)), *args)
        with self.assertRaises(ValueError):
            acq.recover_anchored_parameters(control(Fraction(1, 1)), *args)

    def test_inadmissible_quotient_edge_rejected(self) -> None:
        # Planted F-11 over-estimating heuristic edge (h(0)=4 > 1 + h(1)=2) must fail closed
        bad = acq.verify_quotient_lower_bound([(0, 1, 1), (1, 2, 2)], {0: 4, 1: 2, 2: 0}, 0, [2])
        self.assertFalse(bad["ok"])
        self.assertEqual(bad["bellman_violations"], 1)
        self.assertIsNone(bad["certified_floor"])

    def test_lean_lint_catches_adversarial_mutations(self) -> None:
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

    def test_lean_lint_is_labelled_a_source_lint(self) -> None:
        res = acq.audit_lean4_init_module("def x : Int := 1\n")
        self.assertEqual(res["scope"], "source-lint-not-proof-check")
        self.assertIn("not a proof check", (acq.audit_lean4_init_module.__doc__ or "").lower())

    def test_lean_lint_planted_vectors(self) -> None:
        planted = {
            "direct sorryAx": ("theorem forged : False := sorryAx False true\n", "TRUST_BYPASS"),
            "qualified sorryAx": ("theorem forged : False := Lean.sorryAx False true\n", "TRUST_BYPASS"),
            "guillemet sorry": ("theorem forged : False := \u00absorry\u00bb\n", "TRUST_BYPASS"),
            "sorry": ("theorem forged : False := by sorry\n", "TRUST_BYPASS"),
            "axiom": ("axiom bad : False\n", "TRUST_BYPASS"),
            "native_decide": ("theorem t : 1 + 1 = 2 := by native_decide\n", "TRUST_BYPASS"),
            "skip kernel": ("set_option debug.skipKernelTC true\n", "TRUST_BYPASS"),
            "custom import": ("import Custom.Untrusted\n\ntheorem t : True := trivial\n", "NON_INIT_IMPORT"),
            "Mathlib import": ("import Mathlib.Tactic\n", "NON_INIT_IMPORT"),
            "Std import": ("import Std\n", "NON_INIT_IMPORT"),
            "Lean import": ("import Lean\n", "NON_INIT_IMPORT"),
            "mixed import line": ("import Init Custom.Untrusted\n", "NON_INIT_IMPORT"),
            "lookalike prefix": ("import InitEvil\n", "NON_INIT_IMPORT"),
            "prelude": ("prelude\n", "NON_INIT_IMPORT"),
            "syntax": ('syntax "foo" : term\n', "SYNTAX_OVERRIDE"),
            "macro_rules": ("macro_rules | `(foo) => `(True)\n", "SYNTAX_OVERRIDE"),
            "macro": ('macro "foo" : term => `(True)\n', "SYNTAX_OVERRIDE"),
            "#eval": ("#eval IO.println \"hi\"\n", "ELABORATION_TIME_EXEC"),
            "#exit": ("#exit\ntheorem later : False := sorry\n", "ELABORATION_TIME_EXEC"),
            "unsafe": ("unsafe def f : Nat := 0\n", "UNSAFE_CODE"),
            "extern": ('@[extern "c_f"] def f : Nat := 0\n', "UNSOUND_ATTR"),
            "implemented_by": ("@[implemented_by g] def f : Nat := 0\n", "UNSOUND_ATTR"),
            "attribute implemented_by": ("attribute [implemented_by g] f\n", "UNSOUND_ATTR"),
            "multi-line attribute": ("@[simp,\n  implemented_by g]\ndef f : Nat := 0\n", "UNSOUND_ATTR"),
            "char literal hides code": (
                "def q : Char := '\"'\n"
                "theorem forged : False := sorryAx False true\n"
                "def q2 : Char := '\"'\n",
                "TRUST_BYPASS",
            ),
        }
        for name, (src, code) in planted.items():
            with self.subTest(vector=name):
                res = acq.audit_lean4_init_module(src)
                self.assertFalse(res["ok"], res)
                self.assertIn(code, {f["code"] for f in res["findings"]})

    def test_lean_lint_accepts_clean_sources(self) -> None:
        clean = {
            "no import": "theorem t : 1 + 1 = 2 := by decide\n",
            "Init import": "import Init\n\ntheorem t : 1 + 1 = 2 := by decide\n",
            "Init submodule": "import Init.Data.Nat\n",
            "forbidden words only in comments": "/- sorry, sorryAx, import Mathlib, #eval -/\n-- axiom unsafe\ndef x : Nat := 1\n",
            "forbidden words only in strings": 'def s : String := "sorryAx import Mathlib"\n',
            "identifier with prime": "def x' : Nat := 1\ndef y : Nat := x'\n",
        }
        for name, src in clean.items():
            with self.subTest(source=name):
                res = acq.audit_lean4_init_module(src)
                self.assertTrue(res["ok"], res)
        with open(os.path.join(HERE, "AnchoredConservationQuotient.lean"), encoding="utf-8") as fh:
            self.assertTrue(acq.audit_lean4_init_module(fh.read())["ok"])

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
