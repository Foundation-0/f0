import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_lean

HERE = os.path.dirname(os.path.abspath(__file__))
HAVE_LEAN = shutil.which("lean") is not None


def write(tmp: str, name: str, text: str) -> str:
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


@unittest.skipUnless(HAVE_LEAN, "lean is not installed")
class TestLeanProofCheck(unittest.TestCase):
    def test_real_file_compiles_with_standard_axioms_only(self) -> None:
        self.assertEqual(check_lean.check(os.path.join(HERE, "AnchoredConservationQuotient.lean")), [])

    def test_sorry_ax_forgery_is_caught(self) -> None:
        src = "namespace Foundation0.ACQ\ntheorem forged : False := sorryAx False true\nend Foundation0.ACQ\n"
        with tempfile.TemporaryDirectory() as tmp:
            failures = check_lean.check(write(tmp, "Forged.lean", src))
        self.assertTrue(any("sorryAx" in f for f in failures), failures)

    def test_custom_axiom_is_caught(self) -> None:
        src = "namespace Foundation0.ACQ\naxiom bad : False\ntheorem forged : False := bad\nend Foundation0.ACQ\n"
        with tempfile.TemporaryDirectory() as tmp:
            failures = check_lean.check(write(tmp, "Forged.lean", src))
        self.assertTrue(any("bad" in f for f in failures), failures)

    def test_compile_error_is_caught(self) -> None:
        src = "namespace Foundation0.ACQ\ntheorem broken : (1 : Nat) = 2 := by decide\nend Foundation0.ACQ\n"
        with tempfile.TemporaryDirectory() as tmp:
            self.assertNotEqual(check_lean.check(write(tmp, "Broken.lean", src)), [])

    def test_file_without_theorems_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(check_lean.check(write(tmp, "Empty.lean", "def x : Nat := 1\n")), ["no public theorems found"])


if __name__ == "__main__":
    unittest.main()
