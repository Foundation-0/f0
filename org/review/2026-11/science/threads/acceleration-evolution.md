# Thread: does the acceleration scale follow the expansion rate?

Follow-up to the science pass, 15 November 2026. Pinned head `gravity@8f96c4b`, folder `acceleration-evolution/`. Marks: **[F]** fact, **[I]** inference.

## Question

The folder sets up the idea that the acceleration scale seen in galaxy rotation grows with redshift in step with the expansion rate. It designs a test and stops before fitting data. This thread does the fit.

## The hypothesis, as the folder writes it

[F] `a0(z) = A E(z)^q`, with A = 1.2e-10 m/s^2 and E the expansion rate relative to today (`README.md:12-21`, `model.py:37-59`). q = 1 is the hypothesis. q = 0 is a constant scale. The folder keeps this separate from the formula c H / (2 pi).

[F] The three numbers in `comparison.json` are ratios of curve values at the two ends of a published sample: 1.9207 for the hypothesis, 2.1575 and 1.9341 for two fitted lines in Ciocan et al. 2026 (arXiv:2604.22613). Separate exact code reproduces all of them.

## Result

**Undecided.** The one like-for-like fit that could be done leans against the hypothesis. The lean does not survive plausible errors in the masses.

### The fit

[F] Data: 100 star-forming galaxies at redshift 0.6 to 2.5 (Nestor Shachar et al. 2023, arXiv:2209.12199, Table 3). For each galaxy the rotation speed at the half-light radius was predicted from the published baryonic mass and size, and compared with the measured speed. p is the power in `a0(z) = A E(z)^p`.

| Treatment of A | Best p | 95% range | How much worse p = 1 fits |
|---|---|---|---|
| Fixed at 1.2e-10 | 0.10 | -0.25 to 0.40 | 32.8 |
| Within 20% of 1.2e-10 | -0.01 | -0.50 to 0.45 | 18.4 |
| Free | -0.74 | -1.8 to 0.25 | 9.8 |

The last column is the difference in -2 ln L.

[F] In four redshift bins the fitted scale is 1.82, 1.51, 1.15 and 1.26 in units of 1e-10, at redshift 0.81, 1.41, 2.11 and 2.30. The hypothesis predicts 1.92, 2.71, 3.83 and 4.16.

### Why it does not settle the matter

- [F] If baryonic masses are biased low by 0.2 dex per unit of redshift, the preference flips to p near 1.2.
- [F] If the correction for pressure support is 1.5 times the published one, the preference for a constant scale shrinks to about 4.
- [F] About half the baryonic mass is gas, and the gas masses come from scaling relations, not from measurement.
- [F] The sample does reach the regime where the scale matters. The median baryonic acceleration at the half-light radius is 1.6 times a0. So the limit is systematic error, not lack of signal.

### The folder's named sample

[F] The per-galaxy data of the 79-galaxy sample in `evidence.json` could not be retrieved. Its two servers timed out. At summary level its fitted lines correspond to p between 1.0 and 1.15. It agrees with the fit above near redshift 0.8 and disagrees near 1.4.

### Other work

- [F] Milgrom (arXiv:1703.06110) writes that early rotation-curve data "all but exclude" a scale of about four times a0 at redshift 2.
- [F] Simulations with ordinary dark matter also give a scale that grows about threefold by redshift 2.3 (Mayer et al. 2023, arXiv:2206.04333).
- [I] So a rising scale would not by itself favour modified gravity. Only the slope of the speed-mass line and the outermost speeds separate the two.

## The observation that would decide it

Outer rotation speeds, where the baryonic acceleration is below 0.3 a0, for 50 to 100 discs each near redshift 1 and 2, with measured gas masses and stellar masses from the same method used locally. The hypothesis predicts a shift of the speed-mass line of -0.25 dex in mass at redshift 1 and -0.48 at redshift 2. A constant scale predicts none. Mass errors that drift with redshift must be below about 0.08 dex.

## Rerun

Programs and saved outputs are in `checks/accel/`. The fit takes about 6 minutes in the check script (the review recorded about 45 minutes on a loaded machine). `python3 checks/check_all.py --full` re-runs it and compares the saved output byte for byte. The KMOS3D bound needs the table that `checks/gravity/fetch_sources.py` downloads.

The 100-galaxy table was typed in from an image of the paper's table and checked by a second reading. The two agreed on 1,295 of 1,300 cells, and the five were resolved on enlarged images. The second reading is saved output, not re-runnable here, because the page images are not in the folder. `check_transcription.py` re-runs the internal consistency check of the table.

## Not verified

- No test with injected signals was run, so the fit's ability to recover a known p is assumed.
- The two samples used come from the same team, so they are not independent.
- The baryon model is a thin disc with one global thickness factor.
