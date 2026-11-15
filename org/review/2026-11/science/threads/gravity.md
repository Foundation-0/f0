# Thread: the 185 km/s threshold against published data

Follow-up to the science pass, 15 November 2026. Pinned head `gravity@8f96c4b`. Marks: **[F]** fact, **[I]** inference.

## Question

The wave series says extra dark mass switches on in systems whose velocity scale is above a threshold. It says the threshold is the collapse scale of the standard cosmology, 185.59 km/s today and lower in the past.

The science pass found that the repository's own table cannot test this, because part of it is computed by the model. This thread tests the claim against published measurements, predicting the same quantity the data holds.

## The model, as the scripts write it

`g_tot = g_b (nu(g_b/a0) + f_trap R)`, with `f_trap = max(0, 1 - (sigma_J/sigma)^2)` and `nu(y) = 1/(1 - exp(-sqrt(y)))` (`wave10_covariant_jeans_unification.py:219-231`). Two parameter sets were tested.

| Set | Threshold | Dark-to-baryon ratio R | Origin |
|---|---|---|---|
| A | 185.59 km/s | 8.524 | the repository's "zero fitted parameters" claim, C-26 |
| B | 200 km/s | 4.0 | best like-for-like fit to the repository's table in the science pass |

The repository states the redshift prediction itself: the trapped fraction in a 200 km/s system rises from 0.14 today to 0.67 at redshift 0.5 and 0.88 at redshift 1 (its issue 6).

## Results

| Test | Data | Set A | Set B | Standard relation alone |
|---|---|---|---|---|
| Early-type galaxies inside the half-light radius | ATLAS3D, 187 galaxies, 36 above threshold | fails, 9 standard errors | fails, 3.4 to 8 | passes |
| Galaxies at redshift 0.7 to 2.5 | Genzel et al. 2020, 41 galaxies | fails, 0 of 41 | fails if the threshold falls, 2 of 41 | passes |
| Giant spirals | SPARC with Di Teodoro et al. 2021 and 2023, 179 galaxies | fails | passes | passes |
| Groups and clusters at two radii | 51 systems | fails | fails unless a mass bias grows outward | not applicable |
| Groups and clusters at the outer radius | 63 systems | fails | marginal | fails |

### Early-type galaxies

[F] Above the threshold, the measured total mass inside the half-light radius equals the stellar mass for a Salpeter mix of stars, to within 0.05 dex, in every bin of velocity dispersion. Set A predicts 0.21 to 0.75 dex more, rising with dispersion. Set B predicts up to 0.46 dex more.

[F] A comparison that does not depend on the assumed star mix uses galaxies at 120 to 186 km/s as the control. The step above the threshold falls short of set A by 0.35 ± 0.04 dex and of set B by 0.10 ± 0.03 dex. For set B above 230 km/s the shortfall is 0.34 ± 0.05 dex.

[I] These galaxies were sorted by velocity dispersion, which also enters the mass. That bias pushes the high bins up, toward the model. The failure is therefore conservative.

### High redshift

[F] The measured dark fraction inside the half-light radius has median 0.25. The standard relation alone predicts 0.21. Set A predicts at least 0.79 for every galaxy and set B with a falling threshold at least 0.64. No galaxy of 41 reaches the set A value and two reach the set B value.

[F] A second sample, 135 galaxies from KMOS3D, sits 0.09 to 0.13 dex above today's speed-mass line. The model's extra term alone would add 0.29 to 0.45 dex for set A and 0.18 to 0.31 for set B.

[I] The falling threshold is the part of the idea that is specific to this repository. It is the part these data reject. For set A to hold, the published baryonic masses would have to be about seven times too large.

### Giant spirals

- [F] Sorted by speed, the eight fastest SPARC spirals sit 0.10 dex above the standard relation. Sorted by baryonic mass the excess is gone, and no SPARC galaxy is above the threshold mass of 2.98e11 solar masses. Sorting by speed picks galaxies that are fast for their mass, so the first result is a selection effect.
- [F] Solved at fixed mass, set A predicts no spirals between about 262 and 435 km/s. Spirals fill that range. Set A gives chi-squared 167 to 391 against 71 for the standard line.
- [F] Above 1.6e11 solar masses, 55 spirals sit 0.047 dex above the standard line in speed. Set B predicts 0.02 to 0.04 and gives chi-squared 47 to 56.
- [F] A bend in the speed-mass line is not significant with flat-part speeds (p about 0.08) and is significant with peak speeds from optical lines (p below 0.02). Either way it is a gentle steepening near 5e10 solar masses, six to nine tenths of a dex below the model's threshold mass, not a jump at it.

### Groups and clusters

- [F] Set A takes R from the full non-baryonic share at the inner radius and then adds the boost nu on top. That counts the boost twice. Measured the model's own way, R at the inner radius is 4 to 7 per system, not 8.5.
- [F] The model needs R to be one number. Within the same system, the residual at the inner radius is 2.1 times the residual at the outer radius (median of 51). The two agree only if the hydrostatic mass bias at the outer radius exceeds the inner one by about 0.23.
- [F] At the outer radius a threshold form fits better than a constant or a power law in all four treatments of stars and mass bias. The best threshold moves between 230 and 345 km/s and R between 3.4 and 6.2. A threshold of 200 km/s is excluded in three of the four.
- [F] No system in these samples lies between 200 and 280 km/s. The lowest is at 296.

## What is dead, and what survives

- **Dead:** the zero-parameter version (set A), at galaxy scale and at cluster scale.
- **Dead:** a threshold that falls with redshift, for either set.
- **Dead:** extra mass in proportion to the baryons at every radius. Fast galaxies have none inside the half-light radius, and clusters have more at small radii than at large ones.
- **Survives:** an excess over the standard relation in every massive class of system, growing with baryonic mass. A threshold form fits the groups and clusters with an onset between 230 and 345 km/s, but across all classes a smooth rise fits as well (next section).

[I] What survives is close to a known result: modified gravity fits galaxies and falls short in groups and clusters (Sanders 2003, Pointecouteau and Silk 2005, Tian et al. 2020).

[I] Proposals that add a component only in deep potentials already exist. They include neutrinos of a few electronvolts, an 11 eV sterile neutrino (Angus 2010), dark baryons in clusters (Milgrom 2008), and an acceleration scale that grows with potential depth (Zhao and Famaey 2012).

## One law across every class?

A second study put every system into one table: 663 local rows in six classes, from dwarf galaxies to clusters, plus 100 galaxies at high redshift kept apart (`checks/gravity/unified/unified_table.csv`).

The extra mass is defined as the mass that must be added to the baryons for the standard relation to give the measured total. Each law is scored by how well it predicts the total mass, with every class weighted equally. The standard relation alone scores 0.190 dex.

### What the fits say

- [F] A law in the measured velocity scale and the radius fits best: extra mass proportional to sigma^4.2 r^0.4, score 0.126 dex. A separate fit written for this review gives the same exponents, 4.17 and 0.42.
- [F] Three reference laws do worse: a component packed to a fixed phase-space density (0.170), an isothermal halo (0.161), and extra mass in proportion to the baryons (0.174).
- [F] Left free, the onset is as gradual as the fit allows. Its position moves from 55 to 356 km/s with the shape assumed and with a shift of 0.2 dex in stellar masses.

### How much of that is forced

[F] The velocity scale is itself a dynamical quantity. At low accelerations the definition of the extra mass gives, identically, baryons plus extra mass equal to 4 sigma^4/(G a0). With no free parameter that identity already reproduces the clusters to 0.05 and 0.10 dex. So the exponent near 4 is partly built in.

[F] Laws that use the baryons alone cannot be circular. The best is extra mass = 10^10.38 (M_b / 1e11 solar masses)^1.36 solar masses, score 0.148 dex. The exponent is 1.36 with a 95% range of 1.32 to 1.39, and it was above 1 in all 300 resamples. Shuffling the velocity scale within each class gives 0.171.

[F] A threshold in baryonic mass with the same number of parameters scores 0.147. The data cannot tell a threshold from a smooth rise.

### Does one class predict another?

| Fitted on | Predicts | Median offset before | After |
|---|---|---|---|
| galaxies only | clusters at the inner radius | +0.29 dex | +0.03 dex |
| galaxies only | clusters at the outer radius | +0.12 dex | -0.23 dex |
| clusters only | early-type galaxies | +0.08 dex | -0.06 dex |
| clusters only | ordinary spirals, outer points | -0.05 dex | -0.15 dex |

[F] A law fitted to galaxies alone predicts the inner regions of clusters, three orders of magnitude up in mass, to 0.03 dex. It then overshoots at the outer radius. A law fitted to clusters puts extra mass into ordinary spirals that they do not have.

[F] Applied to the high-redshift galaxies with no refitting, the baryon-only law gives a median offset of -0.04 dex. The standard relation alone gives +0.01.

### What this establishes

- [F] Every massive class sits above the standard relation: early-type galaxies and giant spirals by 0.08 dex, clusters by 0.12 dex at the outer radius and 0.29 at the inner. The excess grows faster than the baryonic mass.
- [F] No law in one variable describes all classes and both cluster radii.
- [I] The law in which a particle is packed to its maximum density everywhere does badly. That law is not a fair test of a real halo of fermions, which is packed only in its core. `neutrino-like.md` takes that case up properly.
- [I] The excess in early-type galaxies depends on the assumed mix of stars and vanishes for a Salpeter mix. The excess in clusters grows if hydrostatic masses are biased low. So the shared trend may be a real component, or two separate systematic effects that happen to point the same way.

## The four speeds near 185 km/s, with honest ranges

| Speed | Repository value | Range from defensible choices |
|---|---|---|
| Collapse scale | 185.59 | 141 to 261 km/s |
| Knee of the galaxy mass function | 175.82 | 152 to 221 km/s |
| Cooling scale | 178.42 | 89 to 446 km/s |
| Onset in the data | 180 to 190 | 95 to 356 km/s |

- [F] The chance that four speeds drawn independently between 30 and 1,500 km/s land as close as the repository's values is about 1 in 100,000. With the ranges above it is about 2% (0.4% to 5%). With wider but still defensible ranges it is about 6%.
- [F] The cooling scale is linear in an overdensity that the script sets to 1,000. The knee speed is a rotation speed and the others are dispersions. As a dispersion it would be 107 to 157 km/s.
- [I] The four are not independent. The largest galaxies sit where gas stops cooling within the age of the universe, which is a standard result of galaxy formation (Rees and Ostriker 1977, White and Rees 1978). The collapse scale and the cooling scale are both built from the critical density and the Hubble time. There are about two independent scales here, not four.


## The observation that would decide what survives

Weak-lensing mass over baryonic mass at a fixed 100 to 300 kpc, for isolated galaxies and fossil groups, in bins of baryonic mass from 2e11 to 3e12 solar masses. That fills the empty range from 200 to 300 km/s. A threshold predicts a kink at one speed. A smooth law predicts none.

## Rerun

Programs and saved outputs are in `checks/gravity/`. `t1`, `t1b` and `t2` read the SPARC tables from `astroweb.case.edu/SPARC/` and the TeX source of arXiv:2109.03828. `t3` to `t6` read the published tables named at the top of each script. `model.py` re-implements the model without importing the repository.

## Not verified

- Stars inside the inner cluster radius come from a prescription, not a measurement.
- The high-redshift test uses a thin-disc approximation at the half-light radius.
- The bootstrap for the bend has 60 simulations.
- The lens sample SLACS was not used.
