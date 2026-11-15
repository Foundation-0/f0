# The Single Thread: a synthesis pending review

**Status: synthesis, pending review.** Nothing here has been reviewed by a maintainer or checked against the
repositories it cites. Read every claim in the essay as the author's, with its evidence still to be traced.

This folder holds an essay and a small Python kernel received on 13 November 2026 from the gem-nexus seat,
an AI agent working for Ahraz Arifuddin. The essay argues that work across Foundation-0/gravity,
Foundation-0/project-asma, Foundation-0/exoplanets-frontier, Moissanite-Labs/weft, ahrazzle/soko and
Proven-Commons shares one four-gate pattern, which it calls an Anchored Conservation Quotient: a null or
boundary anchor, an exact conservation law, a linearised pivot coordinate, and a machine-checked receipt.

The same pattern is the subject of [f0#39](https://github.com/Foundation-0/f0/pull/39), a longer monograph with a
Lean module and a hardened reference kernel, which has open change requests. This folder is the short essay that
preceded it. It is kept separate so each can be reviewed on its own terms.

## Files

| File | What it is |
|---|---|
| [`the-single-thread.md`](the-single-thread.md) | The essay, converted from the Google Doc to Markdown with pandoc 3.1.3, then corrected 2026-11-15 against ahrazzle's review of f0#41 (see Corrections below). The original conversion was text-unchanged; the text in the tree is the corrected version. |
| [`quotient_anchor_kernel.py`](quotient_anchor_kernel.py) | The kernel, corrected 2026-11-15 against ahrazzle's review of f0#41. The Drive file is the original (see Provenance for its SHA-256). Python 3, standard library only. |
| [`kernel-output.txt`](kernel-output.txt) | Its output. |
| [`test_quotient_anchor_kernel.py`](test_quotient_anchor_kernel.py) | Tests: receipt match, `-O` run, and witness-break copies that must exit non-zero. |

## Provenance

| Item | Drive id | Modified (UTC) | SHA-256 |
|---|---|---|---|
| Essay (Google Doc, exported as .docx) | `1s52jDXUmsWTGRym_ykxVqSXKRl76tkeELi7Wq3EIJcs` | 2026-11-13T07:24:38Z | docx export `2c15bc0ae494094e48d718fa1456a97f66f0f6c395260eb19ccdbf65a5953696` |
| `quotient_anchor_kernel.py` | `141Tx2rCI8eNsw66wFskt8_Fho3-DNq11` | 2026-11-13T07:24:25Z | `7843074c3067752ac9851424505d0ec8fda65fee99505e2e9355750ce9163f43` |
| Handoff note (JSON) | `1JcLyt06Zh1fmaQYWKE9HgxYWBOoxLAAe` | note timestamp 2026-11-13T07:25:00Z | `45abdd819deb6760f131f24b85004a2a5e28d4c2e532f6010590e82faad0c88e` |

A Google Doc export is regenerated on each download, so the .docx digest identifies this copy only.

## Running the kernel

```bash
python3 quotient_anchor_kernel.py
```

Output (same line on Python 3.12.3 and 3.13.5):

```
SINGLE_THREAD_KERNEL_OK: 7/7 checks passed | 5 domains | Proven-Commons not exercised | SHA-256: 8ff47efe0a8d2885a59af396cf9f001ad41314359d2ccc1a6f0cda85c53ff1a5
```

## Tests

```bash
python3 -m unittest discover -s deep-fields/scouting/single-thread -p 'test_*.py'
```

## What the kernel shows, and its limits

- **The essay now quotes the digest this file prints.** The essay originally cited
  `64b7bf0f578c3f64f34f874b025617cffc6562f676ea92ba5da0aa10363453a1`; this file prints `8ff47efe...`.
  That digest is the hash of the six result objects, so the essay and this file came from different versions
  of the kernel or a different run — the quoted digest was the digest of a kernel version that is not in the
  tree. The kernel fails if its recomputed receipt differs from `kernel-output.txt`.
- **The print counts the checks that ran.** It runs seven checks: three on one
  formula for project-asma, weft and exoplanets-frontier, one on fold-wise ranks, one on a gravity-style trapping
  fraction, one on a four-node graph for soko, and one negative control for the `p = 0` confound. The five
  domains are project-asma, weft, gravity, soko and exoplanets-frontier. Proven-Commons is named in the essay
  and is not exercised by any check.
- **The checks raise real exceptions.** `WitnessFailure` survives `python3 -O`, and every recovered value is
  checked, including weft's and the exoplanets' `r`. The tests run witness-break copies under `-O` that must
  exit non-zero. f0#39's kernel raises real exceptions for this reason.
- **The examples are synthetic.** Each check builds its inputs from the same model it then inverts, so a pass
  shows the algebra is consistent. It does not show that any cited repository's data fits the model.
- **The anchor is assumed.** The bleed rate `alpha` is passed in as known. The inversion is correct only if the
  anchor batch measures bleed alone; the essay does not show how each program obtains such a batch. The `p = 0`
  confound is recorded in the kernel as a negative control: with `alpha = 3/20` and `c = 1/4`, `y(0) = 29/80`,
  and using that endpoint as the anchor returns `c = 0`.
- **The four-node soko bound is a toy.** `verify_quotient_conservation_bound` fails on an empty goal set, on a
  goal unreachable over the supplied edges, and — when given the transition function — on any reachable
  transition missing from the edge list.
- **Claims in the essay are the author's.** Figures such as hash-collision counts, cut ratios, CI states and
  certificate commits are quoted from other work and are pending reproduction here. Some links in the essay point
  to Google Drive files that are not public.

## Corrections (2026-11-15, against ahrazzle's review of f0#41)

- Essay receipt: quoted digest corrected from `64b7bf0f…` to the digest this file prints (`8ff47efe…`); the
  "5/5 domains verified" line replaced with the counted receipt (7 checks, 5 domains, Proven-Commons not
  exercised); the "proved and shipped" claim and the "discrepancies closed" claim removed.
- Essay ledger figures corrected against the source ledgers: project-asma split 862 within / 3,454 cross (not
  863 / 3,453), no `|b| <= 1/20` bound found, `(1/20, 3/8)` are mixture fractions not a point of `Phi`,
  `30cdc3a` has four green checks and is not on main, #83 closed unmerged (superseded by merged #87), C20
  still open; gravity crossover `0.02897 a_0` (C-23, no Lean lemma), 39-entry SHA256SUMS, no QPos found;
  weft division-free gate proposed in unmerged weft#179, v2 suite merged as external/unreviewed (#128);
  soko floor `>= 38` at 117,766,522 canonical states with 105,495,450 collisions prevented, 181,027,454
  collisions and the ~282M raw-state ceiling belonging to the later `f = 38` chunk, zero violations across
  250,000 states / 439,038 transitions / 255,924 stutters, 34-step route only under sticky doors (Druid
  crushed at step 30 under crushing doors), NUL-byte differential as an open review finding (zip#5);
  exoplanets Sectors 1–107, pre-DR4 Gaia DR3 catalog, DR4 on 2 December 2026 as falsifier.
- Kernel: asserts replaced with `WitnessFailure` exceptions; every recovered value checked; empty goals,
  unreachable goals and uncovered reachable transitions fail; the `p = 0` confound is a required negative
  control; the receipt is counted (7/7) and checked against `kernel-output.txt`.
- Disposition: this folder can close in favor of f0#39 once #39's open requests are fixed. That is a
  maintainer call, not made here.
