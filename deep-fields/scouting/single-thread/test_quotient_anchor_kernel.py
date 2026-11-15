"""Tests for quotient_anchor_kernel.py (f0#41).

These tests exist because the original kernel's defects were all silent:
a hardcoded "5/5" print, `assert` checks that `python3 -O` removes, and
recovered values (weft's and the exoplanets' `r`) that nothing tested.
Each witness-break test mutates a copy of the kernel and requires a
non-zero exit, including under `-O`.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quotient_anchor_kernel as k

HERE = os.path.dirname(os.path.abspath(__file__))
KERNEL = os.path.join(HERE, "quotient_anchor_kernel.py")
EXPECTED_DIGEST = "8ff47efe0a8d2885a59af396cf9f001ad41314359d2ccc1a6f0cda85c53ff1a5"


def run_kernel(path: str, optimize: bool) -> subprocess.CompletedProcess:
    argv = [sys.executable]
    if optimize:
        argv.append("-O")
    argv.append(path)
    return subprocess.run(argv, capture_output=True, text=True, check=False)


def mutated_copy(mutations: dict) -> str:
    """A temp copy of the kernel with the given string replacements applied."""
    with open(KERNEL, encoding="utf-8") as fh:
        src = fh.read()
    for old, new in mutations.items():
        if old not in src:
            raise AssertionError(f"mutation target not found in kernel: {old!r}")
        src = src.replace(old, new)
    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    tmp.write(src)
    tmp.close()
    return tmp.name


class TestKernelReceipt(unittest.TestCase):
    def test_kernel_runs_and_receipt_matches(self) -> None:
        proc = run_kernel(KERNEL, optimize=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("7/7 checks passed", proc.stdout)
        self.assertIn("Proven-Commons not exercised", proc.stdout)
        self.assertIn(f"SHA-256: {EXPECTED_DIGEST}", proc.stdout)
        with open(os.path.join(HERE, "kernel-output.txt"), encoding="utf-8") as fh:
            self.assertEqual(fh.read().strip(), proc.stdout.strip())

    def test_kernel_passes_with_assertions_stripped(self) -> None:
        proc = run_kernel(KERNEL, optimize=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("SINGLE_THREAD_KERNEL_OK", proc.stdout)


class TestWitnessBreaks(unittest.TestCase):
    def assert_breaks(self, path: str) -> None:
        for optimize in (False, True):
            with self.subTest(optimize=optimize):
                proc = run_kernel(path, optimize=optimize)
                self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertNotIn("SINGLE_THREAD_KERNEL_OK", proc.stdout)

    def test_broken_asma_expectation_fails(self) -> None:
        # The original kernel printed OK under -O with this expectation broken.
        path = mutated_copy(
            {'asma["c_conversion_or_synthesis"] == "1/4"': 'asma["c_conversion_or_synthesis"] == "1/5"'}
        )
        try:
            self.assert_breaks(path)
        finally:
            os.unlink(path)

    def test_weft_generator_r_change_fails(self) -> None:
        # The original kernel printed OK (with a new digest) when the weft
        # generator r changed from 8 to 99, because only c was checked.
        path = mutated_copy(
            {
                "Fraction(1, 20), obs_y(Fraction(1, 20), Fraction(8, 1), Fraction(0, 1), Fraction(2, 5)),":
                "Fraction(1, 20), obs_y(Fraction(1, 20), Fraction(99, 1), Fraction(0, 1), Fraction(2, 5)),",
                "Fraction(3, 8), obs_y(Fraction(3, 8), Fraction(8, 1), Fraction(0, 1), Fraction(2, 5)),":
                "Fraction(3, 8), obs_y(Fraction(3, 8), Fraction(99, 1), Fraction(0, 1), Fraction(2, 5)),",
            }
        )
        try:
            self.assert_breaks(path)
        finally:
            os.unlink(path)

    def test_invalid_alpha_fails(self) -> None:
        # The original kernel returned a certificate for alpha = 2 under -O.
        path = mutated_copy({"Fraction(2, 5),\n        Fraction(1, 20)": "Fraction(2, 1),\n        Fraction(1, 20)"})
        try:
            self.assert_breaks(path)
        finally:
            os.unlink(path)

    def test_empty_edge_list_and_empty_goals_fail(self) -> None:
        with self.assertRaises((k.WitnessFailure, ValueError)):
            k.verify_quotient_conservation_bound([], {0: 1000, 3: 0}, 0, [3])
        with self.assertRaises((k.WitnessFailure, ValueError)):
            k.verify_quotient_conservation_bound([(0, 1, 1), (1, 2, 1)], {0: 2, 1: 1, 2: 0}, 0, [])
        with self.assertRaises((k.WitnessFailure, ValueError)):
            k.verify_quotient_conservation_bound([], {0: 1000, 3: 0}, 0, [3])

    def test_missing_reachable_transition_fails_closure(self) -> None:
        succ = {0: [(1, 1), (2, 2)], 1: [(2, 1)], 2: [(3, 1)], 3: []}
        with self.assertRaises(k.WitnessFailure):
            k.verify_quotient_conservation_bound(
                [(0, 1, 1), (0, 2, 2), (2, 3, 1)], {0: 3, 1: 2, 2: 1, 3: 0}, 0, [3],
                successors=lambda u: succ.get(u, []),
            )

    def test_p0_confound_is_on_the_record(self) -> None:
        """With alpha = 3/20 and c = 1/4, y(0) = 29/80; using that endpoint
        as the anchor returns c = 0. The kernel requires this behaviour."""
        def obs_y(p: Fraction, r: Fraction, c: Fraction, alpha: Fraction) -> Fraction:
            q = (r * p + c * (1 - p)) / (r * p + (1 - p))
            return (1 - alpha) * q + alpha

        res = k.verify_anchored_mobius_certificate(
            "confound", Fraction(29, 80),
            Fraction(1, 20), obs_y(Fraction(1, 20), Fraction(11, 1), Fraction(1, 4), Fraction(3, 20)),
            Fraction(3, 8), obs_y(Fraction(3, 8), Fraction(11, 1), Fraction(1, 4), Fraction(3, 20)),
        )
        self.assertEqual((res["c_conversion_or_synthesis"], res["r_selection_or_snr"]), ("0", "11"))

    def test_invalid_alpha_raises_in_process(self) -> None:
        with self.assertRaises(k.WitnessFailure):
            k.verify_anchored_mobius_certificate(
                "x", Fraction(2, 1), Fraction(1, 20), Fraction(1, 2), Fraction(3, 8), Fraction(1, 2)
            )


if __name__ == "__main__":
    unittest.main()
