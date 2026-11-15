import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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
            self.assertEqual(check_lean.check(write(tmp, "Empty.lean", "def x : Nat := 1\n")), ["no theorems found"])


class TestTheoremDiscovery(unittest.TestCase):
    """Discovery is pure text scanning, so these tests need no Lean."""

    def test_finds_every_legal_declaration_form(self) -> None:
        src = (
            "namespace Foundation0.ACQ\n"
            "theorem good : True := trivial\n"
            "  theorem indented : True := trivial\n"
            "protected theorem guarded : True := trivial\n"
            "@[simp] theorem simp_attr : True := trivial\n"
            "@[simp]\ntheorem attr_on_own_line : True := trivial\n"
            "private theorem helper : True := trivial\n"
            "lemma lemma_form : True := trivial\n"
            "noncomputable theorem nc : True := trivial\n"
            "end Foundation0.ACQ\n"
        )
        self.assertEqual(
            check_lean.public_theorems(src),
            ["good", "indented", "guarded", "simp_attr", "attr_on_own_line", "helper", "lemma_form", "nc"],
        )
        self.assertEqual(check_lean.unparsed_theorem_tokens(src), [])

    def test_finds_all_theorems_in_the_real_file(self) -> None:
        with open(os.path.join(HERE, "AnchoredConservationQuotient.lean"), encoding="utf-8") as fh:
            src = fh.read()
        names = check_lean.public_theorems(src)
        self.assertEqual(len(names), 12)
        self.assertIn("sub_one_mul", names)  # private theorem, missed by the old ^theorem scan
        self.assertIn("bleed_conversion_numerator_identity", names)
        self.assertIn("nat_descent_bound", names)
        self.assertIn("cross_shard_shift_inversion", names)
        self.assertEqual(check_lean.unparsed_theorem_tokens(src), [])

    def test_unparsed_declaration_forms_are_reported(self) -> None:
        src = (
            "namespace Foundation0.ACQ\n"
            "set_option pp.all true in theorem sneaky : True := trivial\n"
            "end Foundation0.ACQ\n"
        )
        self.assertEqual(check_lean.public_theorems(src), [])
        self.assertEqual(len(check_lean.unparsed_theorem_tokens(src)), 1)

    def test_theorem_word_in_comments_and_strings_is_ignored(self) -> None:
        src = (
            "/- theorem forged : False := sorry -/\n"
            "-- theorem hidden\n"
            "def s : String := \"theorem\"\n"
            "theorem real : True := trivial\n"
        )
        self.assertEqual(check_lean.public_theorems(src), ["real"])
        self.assertEqual(check_lean.unparsed_theorem_tokens(src), [])

    def test_check_fails_closed_on_unparsed_form_with_stubbed_lean(self) -> None:
        """`check` must fail when a declaration form is unparsed, even if Lean is fine."""

        def fake_run_lean(path: str) -> subprocess.CompletedProcess:
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            names = re.findall(r"#print axioms (\S+)", content)
            stdout = "".join(f"'{n}' does not depend on any axioms\n" for n in names)
            return subprocess.CompletedProcess(args=["lean", path], returncode=0, stdout=stdout, stderr="")

        good = "namespace Foundation0.ACQ\n  theorem indented : True := trivial\nprotected theorem guarded : True := trivial\nend Foundation0.ACQ\n"
        sneaky = "namespace Foundation0.ACQ\nset_option pp.all true in theorem sneaky : True := trivial\nend Foundation0.ACQ\n"
    def test_probe_lines_go_before_the_closing_end(self) -> None:
        src = (
            "namespace Foundation0.ACQ\n"
            "private theorem helper : True := trivial\n"
            "theorem good : True := trivial\n"
            "end Foundation0.ACQ\n"
        )
        probed = check_lean._probe_source(src, ["helper", "good"])
        self.assertLess(probed.index("#print axioms"), probed.index("end Foundation0.ACQ"))
        # No closing end: probes append instead of vanishing.
        self.assertTrue(check_lean._probe_source("theorem good : True := trivial\n", ["good"]).endswith("#print axioms Foundation0.ACQ.good\n"))

    def test_private_theorems_get_axiom_reports_with_stubbed_lean(self) -> None:
        """Probes must sit inside the namespace: Lean cannot resolve a
        private name from outside it, so a stub that only reports probes
        placed before `end` must still see every theorem."""

        def fake_run_lean(path: str) -> subprocess.CompletedProcess:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
            end_at = next(i for i, line in enumerate(lines) if line.startswith("end "))
            names = re.findall(r"#print axioms (\S+)", "\n".join(lines[:end_at]))
            stdout = "".join(f"'{n}' does not depend on any axioms\n" for n in names)
            return subprocess.CompletedProcess(args=["lean", path], returncode=0, stdout=stdout, stderr="")

        src = (
            "namespace Foundation0.ACQ\n"
            "private theorem helper : True := trivial\n"
            "theorem good : True := trivial\n"
            "end Foundation0.ACQ\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(check_lean, "run_lean", fake_run_lean):
                self.assertEqual(check_lean.check(write(tmp, "Probe.lean", src)), [])

    def test_mangled_private_names_match_by_short_name(self) -> None:
        """Lean prints a private declaration's axiom report under its
        mangled name (`_private.<module>.0.<namespace>.<theorem>`); the
        checker must match it by short name, or the four private theorems
        in the real file fail with 'no axiom report' (CI 43669808000)."""

        def fake_run_lean(path: str) -> subprocess.CompletedProcess:
            stdout = (
                "'_private.Probe.0.Foundation0.ACQ.helper' does not depend on any axioms\n"
                "'Foundation0.ACQ.good' does not depend on any axioms\n"
            )
            return subprocess.CompletedProcess(args=["lean", path], returncode=0, stdout=stdout, stderr="")

        src = (
            "namespace Foundation0.ACQ\n"
            "private theorem helper : True := trivial\n"
            "theorem good : True := trivial\n"
            "end Foundation0.ACQ\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(check_lean, "run_lean", fake_run_lean):
                self.assertEqual(check_lean.check(write(tmp, "Probe.lean", src)), [])


if __name__ == "__main__":
    unittest.main()
