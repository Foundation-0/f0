"""
Builds verdicts.csv from the H1 index files.  One row per in-scope claim or indexed result.
Usage: python3 -I build_verdicts.py <claims-index.csv> <results-index.csv> <out.csv>
Every verdict below was set by the reviewing seat.  This script only applies them to the rows,
so the same judgment lands on every copy of the same statement.
"""
import csv, sys

N = "notes/"
G_SCRIPT = {**{i: "verify_all.py" for i in range(1, 8)}, 8: "wave3_empirical_audit.py",
            **{i: "wave4_unified_field_solver.py" for i in (9, 10, 11)},
            **{i: "wave5_unified_forces_stochastic_qm.py" for i in range(12, 18)},
            **{i: "wave6_convergence_unification.py" for i in (18, 19, 20)},
            **{i: "wave7_group_cluster_threshold_audit.py" for i in (21, 22)},
            **{i: "wave9_scale_convergence_audit.py" for i in (23, 24)},
            **{i: "wave10_covariant_jeans_unification.py" for i in (25, 26, 27)},
            **{i: "wave11_machian_pairing_unification.py" for i in (28, 29, 30)},
            **{i: "wave12_cosmic_dawn_quasar_collapse.py" for i in (31, 32, 33)}}
LEAN = {1, 2, 4, 9, 12, 14, 16, 18, 19, 20, 21, 22, 25, 26, 28, 30, 31, 32, 33}

def V(statement, evidence, label, verdict, link, plain, status="judged", owner=""):
    return dict(statement=statement, evidence=evidence, label_judgment=label, verdict=verdict,
                evidence_link=link, plain_language=plain, status=status, needs_owner_call=owner)

NOT_CLAIM = lambda why, link="ties.md": V("", "", "", "", link, why, status="not a claim")
NOT_YET = lambda why, link="theories.md": V("", "", "", "", link, why, status="not yet judged")

GRAVITY = {
 3: V("True. The soliton constant 3.9251 is the published value.", "Repository code regenerates it from a fresh clone.",
      "Accurate.", "KNOWN", N + "gravity.md",
      "This number is from Hui and co-authors (2017) and the script gets the same value. The ledger says it is a reproduction, which is right."),
 8: V("The fits regenerate. The four lens counts are not in the cited paper.",
      "Float code. The citation for the counts fails against the paper's text.",
      "EMPIRICAL-FIT is fair for the fits. The lens-count citation is wrong.", "CONTRADICTED (in part)", "recheck-1114.md",
      "The four numbers of lenses per bin do not appear in the paper they are cited to, which gives different numbers per bin. Their total does match the paper's counts added up, and the fits themselves reproduce.", owner="yes"),
 16: V("True. 2.42 +/- 0.20 is the published value.", "A citation, plus a Lean check of the two inequalities.",
       "Accurate.", "KNOWN", N + "gravity.md",
       "This records a published experiment (Hensen and co-authors, 2015). The ledger says it does not test anything about galaxies."),
 21: V("The fit regenerates from the table in the script.",
       "The table is typed into the script. 28 rows are computed from a halo model with an assumed baryon fraction, and 10 rows are scaled by a factor with a knee at 180 km/s.",
       "EMPIRICAL-FIT is defined as a fit to published tables. 38 of 126 rows are not published values.", "OVERSTATED", N + "gravity.md",
       "The curve fit runs as described. Part of the data it is fitted to was produced by a model inside the script, so it is not purely a fit to published measurements.", owner="yes"),
 22: V("The comparison regenerates.", "Same table as C-21. The plateau is carried mostly by the 28 computed rows.",
       "The same limit as C-21.", "OVERSTATED", N + "gravity.md",
       "The plateau in the mass ratio comes largely from rows the script computed with an assumed baryon fraction. It is weaker evidence than a plateau seen in measured values.", owner="yes"),
 23: V("Parts 1 and 2 regenerate. The crossover value was also checked by hand. Part 3, the one-parameter fit, compares two different ratios.",
       "Float code. The prediction is a ratio of accelerations and the table holds ratios of mass.",
       "COMPUTED is fair for parts 1 and 2. The fit quality in part 3 is overstated.", "OVERSTATED", N + "gravity.md",
       "The first two parts are straightforward evaluations and they reproduce. The fit in the third part compares the model's acceleration ratio with a table of mass ratios, which are different things at these radii.", owner="yes"),
 26: V("185.59 km/s recomputes independently. Chi-squared 60.26 reproduces as the scripts compare. Like for like it is 256.53.",
       "Float code. The halo convention is a choice (153 to 216 km/s). The fit compares unlike ratios.",
       "\"Zero free parameters\" and \"chi-squared per degree of freedom 1.004\" claim more than the evidence shows.", "OVERSTATED", "checks/g185_independent.out",
       "The scale of 185.59 km/s is computed correctly from one convention, and other common conventions give 153 to 216. A threshold near 185 to 200 km/s does describe the table, but only if the dark-to-baryon ratio is fitted to about 4 instead of being fixed at 8.5.", owner="yes"),
 27: V("All four numbers reproduce.", "Three of the four are set by a choice the claim does not derive. The fourth comes from the C-26 fit.",
       "CONJECTURE is right for the common origin. \"Independently defined\" is not supported.", "OVERSTATED", "ties.md",
       "Four speeds near 185 km/s are compared, and each is computed correctly. Three of them move by tens of percent with choices made in the script, so their agreement is not independent evidence.", owner="yes"),
}

def gravity(cid):
    n = int(cid.split("-")[1])
    if n in GRAVITY: return GRAVITY[n]
    lean = " The Lean lemma for this claim builds on standard axioms and states only integer arithmetic." if n in LEAN else ""
    return V("The stated numbers regenerate byte for byte.",
             f"`python3 {G_SCRIPT[n]} --check` exits 0 on a fresh clone at 8f96c4b. Float code with bare asserts. Not recomputed with separate code in this pass.",
             "Modest and consistent with the evidence." + lean, "REPRODUCED", N + "gravity.md",
             "The repository's own script gives the numbers in the ledger. The ledger presents this as an evaluation of published equations under chosen inputs, not as new physics.")

EXO = {
 "C-01": V("The results file holds 22 passing rows from 18 stars.", "File at the pinned head. The pass rule is a signal-to-noise of 3.0. Not re-run, which needs survey downloads.",
           "\"Blind confirmation of 22 candidates\" overstates 22 rows from 18 stars at 3 sigma.", "OVERSTATED", N + "exoplanets-frontier.md",
           "The file shows 22 detections that passed, and they belong to 18 different stars. The bar for passing is low, so these are consistent re-detections, not confirmations of planets.", owner="yes"),
 "C-02": V("A null result. The ledger's row count and values differ from the results file.", "Reader finding: 33 rows in the file against 24 in the claim, and one quoted value is from a different column.",
           "FALSIFIED is a reasonable reading of a null result. The numbers need reconciling.", "OPEN", N + "exoplanets-frontier.md",
           "No planet signal was found in this sample, which is a useful negative result. The numbers in the ledger do not match the file at the pinned commit, so the claim is not established as written."),
 "C-03": V("Not re-run.", "The quoted hash prefix does not match the file.", "VERIFIED with a hash that does not match is overstated.", "OVERSTATED", N + "exoplanets-frontier.md",
           "The claim points to a results file by its fingerprint, and the fingerprint does not match the file in the repository. The benchmark itself may be fine, and it was not re-run here.", owner="yes"),
 "C-04": V("The ledger's period and timing values differ from the results file.", "The quoted hash prefix does not match the file.", "VERIFIED is overstated.", "OVERSTATED", N + "exoplanets-frontier.md",
           "The numbers in the claim and the numbers in the results file disagree, and the file's fingerprint does not match the one quoted. The file was regenerated after the claim was written.", owner="yes"),
 "C-05": V("The 14.35 day signal is in no results file.", "Reader finding. The cited files hold no such row.", "CONJECTURE is the right label.", "NOT CHECKABLE", N + "exoplanets-frontier.md",
           "The signal this claim describes cannot be found in the repository's results. It is labelled a conjecture, and the data to check it is missing."),
 "C-06": V("The ledger's offsets differ from the results file.", "The quoted hash prefix does not match the file. Reader finding: the file's verdict for the named star is not the one claimed.",
           "VERIFIED is overstated.", "OVERSTATED", N + "exoplanets-frontier.md",
           "The positions in the claim differ from those in the results file, and the fingerprint does not match. The file gives the named star a less certain verdict than the claim does.", owner="yes"),
 "C-07": V("A null result. The file and its hash agree.", "Not re-run, which needs survey downloads.", "Consistent.", "OPEN", N + "exoplanets-frontier.md",
           "None of the six leads survived the repository's own tests. The record is consistent, and the test was not repeated in this pass."),
 "C-08": V("The 348 rows exist. Their RUWE is 1.0 in every row.", "The Gaia check fell back to a default value for all 348 rows.", "\"Clean targets\" and VERIFIED are not supported.", "OVERSTATED", "recheck-1114.md",
           "The list of 348 targets is described as cleaned with Gaia data. Every row carries the same placeholder value, so the Gaia binary-star check did not run on them.", owner="yes"),
}

RR = {
 "L344": V("True and published.", "Bartzos and co-authors (arXiv:1811.12800) state that all embeddings of L344 can be real. No certificate is in the repository.",
           "KNOWN is accurate.", "KNOWN", N + "rigid-realizations.md", "This is a published result and the repository labels it as such. It holds no certificate of its own for it."),
 "L880": V("880 real realizations exist for the stored lengths.", "Independent exact check in this pass, fail-closed and tested on corrupted input. The complex count of 880 is taken from the literature.",
           "\"Claimed, pending independent verification\" is accurate. This pass supplies one independent verification.", "VERIFIED", "checks/l880_independent.out",
           "For these bar lengths the framework can be assembled in 880 different ways, which is every way the algebra allows. A separate program written for this review confirms it in exact arithmetic."),
 "G160": V("At least 132 real realizations at the published lengths.", "The repository's verifier passes from a fresh clone and rejects a corrupted input (reader run). The value 132 is already reported numerically by Bartzos and co-authors.",
           "Accurate.", "REPRODUCED", N + "rigid-realizations.md", "This certifies a number that a 2021 paper found numerically. The repository's own check passes, and a separate check has not been written yet."),
}

def results_row(r):
    repo, cid, f, label, text = r["repository"], r["claim_id"], r["file"], r["label"], r["text"]
    k = cid.split("/")[-1]
    if "fact-check" in f:
        return NOT_CLAIM("This row is a check that a quoted fact matches its source. It is not a result of this repository.")
    if repo in ("astr0", "physics0") or (repo == "math0" and f == "README.md"):
        return NOT_CLAIM("This row is a status cell in a project table about another repository.")
    if repo == "formal-claims-audit":
        return NOT_CLAIM("The table says \"none yet\". The repository holds no verdicts.", "theories.md")
    if repo == "gfq-codes":
        g9 = "gf9" in f
        return V("True. No such code exists.", "Independent exact check of all 18 certificates in this pass, fail-closed and tested on corrupted input.",
                 "\"Claimed research result, exact\" is accurate." + (" The GF(9) bound is already in Maruta's table (n_9(4,26) = 32, n_9(4,27) = 33), and the higher dimensions follow by shortening." if g9 else " codetables.de showed the weaker bound on 15 November 2026."),
                 "KNOWN" if g9 else "VERIFIED", "checks/delsarte_independent.out",
                 ("The bound is correct and was checked with a separate program. It is already known from Maruta's tables, so it is a correction to one online table and not a new result." if g9 else
                  "The bound is correct and was checked with a separate program. It improves by one the upper bound shown at codetables.de for this length and dimension."),
                 owner="yes" if g9 else "")
    if repo == "rigid-realizations": return RR["L880"]
    if repo == "point-charges":
        return V("The counts 4, 9, 24, 29 and 44 are returned by the repository's second verifier.", "`verify_arb.py certificates/*.json` exits 0 on a fresh clone at a2fd159 (lead run). Not yet recomputed with separate code.",
                 "\"Computer-certified\" is fair. The five-charge case builds on a published counterexample.", "REPRODUCED", N + "others.md",
                 "The repository's checker confirms the exact number of balance points for each arrangement of charges. Three of the five counts exceed the bound Maxwell proposed.")
    if repo == "finite-state-proofs":
        return V("Eleven recurrences hold.", "Reader run: two exact-integer verifiers pass, also under -O, and reject corrupted input. The link from the count to the transfer matrix is a prose argument.",
                 "\"Computer-assisted proof\" is fair.", "REPRODUCED", N + "others.md",
                 "Both of the repository's programs confirm the recurrences with whole-number arithmetic. The recurrences were already listed as observed patterns, and this supplies a proof that awaits human review.")
    if repo == "cfrp-strengthening":
        return V("The checker matches ten printed values.", "Reader run: verify.py passes and rejects five corruptions in both modes. The worked example it is compared with is not in the repository.",
                 "VERIFIED here means agreement with a printed example inside tolerances the author set. Under the shared glossary that is REPRODUCED.", "REPRODUCED", N + "others.md",
                 "The calculation agrees with ten numbers from a published design example. The example itself is not in the repository, so the reference values cannot be checked from it.")
    if repo == "incentre-lattices":
        if "must be rejected" in label: return NOT_CLAIM("This row is a negative control: an input the verifier is built to reject.", N + "incentre-lattices.md")
        if f.endswith("review-ledger.md"): return NOT_CLAIM("This row records an internal review step, not a result.", N + "incentre-lattices.md")
        if label.strip().lower() == "open": return V("", "", "", "OPEN", N + "incentre-lattices.md", "The repository itself marks this as open.")
        proven = "PROVEN" in label
        return V("The finite checks pass.", "Lead run: `make verify` exits 0 on a fresh clone at 2d374ff with 15 checksums OK and a clean tree. Reader run: the verifiers also pass under -O and none relies on a bare assert.",
                 ("The PROVEN part rests on a written proof reviewed by AI agents only. It was not checked line by line in this pass." if proven else "VERIFIED here is a finite computation, in floating point for the sampled paths."),
                 "REPRODUCED", N + "incentre-lattices.md",
                 ("The repository's checks pass for the cases they cover. The general proof is written out and still needs a line-by-line check by a reviewer." if proven else
                  "The repository's checks pass for the cases they cover. A sampled path is evidence of a motion, not a proof of one."))
    if repo == "vitruvian3d":
        return NOT_YET("The first 22 replay steps pass on a fresh clone. The written proofs were not checked in this pass, and one verifier accepts a corrupted certificate under -O.", "recheck-1114.md")
    if repo == "plate-eclipses" and k == "R-1":
        return V("The period reproduces.", "Reader re-fit offline: 4343.28 +/- 1.06 days against 4343.3 +/- 1.1. Two of the timing errors are assumed values.", "\"Claimed\" is accurate.", "REPRODUCED", N + "others.md",
                 "A separate fit of the same eclipse times gives the same period. The prediction for 2033 depends on error bars that were assumed for two of the eclipses.")
    return NOT_YET("In scope, not reached in this pass.")

def claims_row(r):
    repo, cid = r["repository"], r["claim_id"]
    if repo == "gravity":
        if cid.startswith("C-"): return gravity(cid)
        if cid.startswith("M-"): return NOT_CLAIM("This row is a method entry, not a claim.", N + "gravity.md")
        return NOT_CLAIM("This row is a review disposition. The ledger text for the claim it names already carries the correction.", N + "gravity.md")
    if repo == "exoplanets-frontier": return EXO[cid]
    if repo == "rigid-realizations": return RR[cid]
    if repo == "incentre-lattices":
        return V("The check passes on the 18 named cases.", "Reader run: floating point check with a 1e-9 tolerance.", "The index recorded the label as CLAIMED. The file says VERIFIED for the 18 cases, which is fair for a finite check.",
                 "REPRODUCED", N + "incentre-lattices.md", "The mirror property holds on the 18 shapes that were tested. Which shapes satisfy it in general is open.")
    raise SystemExit("unmapped claim " + repo + " " + cid)

cols = ["id", "repository", "claim_id", "source_file", "source_line", "label_as_written", "statement", "evidence",
        "label_judgment", "verdict", "status", "needs_owner_call", "evidence_link", "plain_language"]
out = []
for r in csv.DictReader(open(sys.argv[1])):
    if r["scope"] != "in": continue
    v = claims_row(r)
    out.append({"id": f'{r["repository"]}/{r["claim_id"]}', "repository": r["repository"], "claim_id": r["claim_id"], "source_file": r["file"],
                "source_line": r["line"], "label_as_written": r["label"], **v})
for r in csv.DictReader(open(sys.argv[2])):
    v = results_row(r)
    out.append({"id": r["claim_id"], "repository": r["repository"], "claim_id": r["claim_id"].split("/")[-1], "source_file": r["file"],
                "source_line": r["line"], "label_as_written": r["label"], **v})
with open(sys.argv[3], "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader()
    for o in out: w.writerow({c: o.get(c, "") for c in cols})
import collections
c = collections.Counter((o["status"], o["verdict"]) for o in out)
print(len(out), "rows")
for (s, v), n in sorted(c.items(), key=lambda x: -x[1]): print(f"  {n:4d}  {s:15s} {v}")
print("  needs owner call:", sum(1 for o in out if o["needs_owner_call"] == "yes"))
