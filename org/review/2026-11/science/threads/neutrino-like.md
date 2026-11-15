# Thread: a neutrino-like component in clusters, taken seriously

Follow-up to `gravity.md`, 15 November 2026. Marks: **[F]** fact from data or a run, **[P]** a published value, **[I]** inference. Papers are cited by arXiv number.

## Question

The unified study in `gravity.md` scored a law in which a particle is packed to its maximum density everywhere, and that law did badly. A first draft of that note took this as a reason to set the idea aside. That was too quick. A real halo of fermions is packed only in its core. This thread asks where a neutrino-like particle fails to line up with the data, and what could explain each mismatch.

"Extra mass" below means the mass that must be added to the baryons so that the standard relation, acting on all sources, gives the measured total. The sample is 51 groups and clusters with masses at an inner radius (r2500) and an outer one (r500).

## The four mismatches, as measured

1. [F] **The extra mass falls with radius.** In 41 of 51 systems the extra mass inside the outer radius is smaller than inside the inner one. The median ratio is 0.58, and in 8 systems it is negative at the outer radius. No mass component can do that.
2. [F] **Groups need a heavier particle.** The mean extra density inside the inner radius sets a lower limit on the particle mass of 1.6 to 2.8 eV for two spin states. The limit rises toward cooler systems.
3. [F] **The amount is small.** A species with the full thermal relic abundance and mass m supplies m / 2.084 eV times the baryons. Inside the outer radius the median system holds the equivalent of 1.2 eV, and the six richest hold 3.3 eV. An 11 eV species would supply 11 eV.
4. [F] **Galaxies.** Early-type galaxies and giant spirals sit 0.08 dex above the standard relation inside a few kiloparsecs. The packing limit allows a 12 eV particle to supply under 1% of that.

## What each explanation does to the first mismatch

The value needed is the one that makes the enclosed extra mass stop falling in 95% of systems.

| Explanation | Size needed | Published size | Verdict |
|---|---|---|---|
| X-ray masses read low, more so outward | 30% at the outer radius, none at the inner | 6% (X-ray outskirts, 1805.00034) to 31% (lensing, 1402.2670) at the outer radius. The difference between radii is 3 to 7 points in X-ray data and simulations (1404.4636) | closes part |
| Gas clumping in the outskirts | none works, even three times the published value | at most about 1.1 at the outer radius (1310.8389) | does not close |
| Field of the surrounding structure | about 0.25 a0 | 0.01 to 0.05 a0 is plausible | closes part |
| Interpolating function and a0 | none works | a0 between 1.0 and 1.2e-10 | does not close |
| Stars and intracluster light inside the inner radius | none works | 40 to 50% of the stars | does not close |

### A correction to the external-field numbers

[F] The halo study reported that an external field of 0.05 a0 closes the radial mismatch almost alone. In the formula used, the field entered is the Newtonian one. A Newtonian field of 0.05 a0 is a physical field of 0.25 a0, which is larger than a cluster's own field at the outer radius. The check `checks/neutrino/n3_efe_check.py` restates everything in physical fields and reproduces the study's numbers at 0.10 and 0.25 a0.

[F] With physical fields of plausible size the effect is real but smaller:

| Physical field | Mass shortfall (inner, outer) | Systems where extra mass no longer falls |
|---|---|---|
| none | none | 20% |
| 0.03 a0 | none | 33% |
| 0.03 a0 | 5%, 20% | 88% |
| 0.03 a0 | 10%, 31% | 98% |
| 0.05 a0 | 10%, 31% | 98% |

[I] So the first mismatch closes with a mass shortfall near the top of the published range together with a modest external field. It does not close with the low values that X-ray studies of outskirts report. The size of the shortfall at the outer radius is the single most important unknown.

## A halo with no free normalisation

[F] The halo study computed the largest halo a fermion can make: an isothermal Fermi gas at the gas temperature, in each cluster's measured field, with its central occupation at the maximum a thermal relic allows. The particle mass needed for that halo to hold the extra mass is 4.7 to 5.9 eV in the median system and 8 to 17 eV for 95% of systems, depending on the corrections. The hardest systems are cool groups.

[F] The 95% figure hides one system. For the group 3C442A (kT 1.34 keV) no fermion of 100 eV or less, at occupation 1/2, holds its extra mass in three of the four correction sets (nominal, observation-low and simulation). The search stops at 100 eV. Only the lensing-high set brings it to 15.6 eV. So the window of 8 to 17 eV closes for every system only with the strongest corrections. `checks/neutrino/model/m3_fermion_halo.out` gives the maximum for each set.

[F] The trend with temperature weakens under the halo model (correlation -0.44, against -0.87 for mean densities). It mostly disappears if the fermions in groups are 1.3 times hotter than the measured gas temperature. [I] Cool cores would do that. The factor was not checked against published temperature profiles.

[P] This agrees with published work. An 11 eV sterile neutrino reaches its packing limit at the centre of all 30 systems of one study (0906.3322), and well-measured clusters need more than about 10 eV (2405.08557).

## How much the clusters hold

[F] Abundance-equivalent mass inside the outer radius, in eV of fully thermal relic:

| Physical field, mass shortfall at the outer radius | All 51 | Richest six |
|---|---|---|
| none, none | 1.2 | 3.3 |
| 0.01 a0, 6% | 1.9 | 4.0 |
| 0.03 a0, 20% | 3.8 | 6.3 |
| 0.03 a0, 31% | 5.3 | 8.4 |
| 0.05 a0, 31% | 5.9 | 8.8 |

[F] Under every choice, richer systems hold more. The ratio rises with velocity dispersion with a slope between 0.9 and 2.3.

[P] A published simulation of modified gravity with sterile neutrinos reports the same pattern: a neutrino share near the cosmic value in the most massive systems and near zero in small ones (2305.05696). [I] The data here and that simulation are independent, so the agreement is worth noting.

## One species: mass against population

Let the species have mass m and be populated at a fraction chi of the thermal relic number. Three conditions apply.

- **Cluster cores:** chi m^4 must be at least K_lo^4, where K_lo is 8 to 17 eV from the halo study.
- **Galaxy lensing:** chi m^4 must be at most K_hi^4. Lensing around isolated galaxies (2406.09685) limits the extra mass inside 300 kpc to 0.6 to 2.7 times the baryons at two standard errors. A halo filled to its packing limit stays under that for K_hi of 10.4 to 13.4 eV with a 5 kpc core, or 7.4 to 21 eV for cores of 2 to 10 kpc.
- **Abundance:** chi m equals the abundance-equivalent mass A divided by the share of the cosmic supply the cluster holds.

[I] The first two are the same kind of statement, so a species exists only if K_lo is below K_hi. That holds for the stronger corrections and is marginal for the weaker ones.

[I] This is a construction, not a fit with a test. K_lo is set by requiring the largest halo to hold the extra mass of the same 51 clusters. A is that same extra mass over the baryons, rescaled. The mass m and the fraction chi are then solved from those two numbers. Only K_hi comes from other data, the galaxy lensing. So a species exists whenever K_lo is below K_hi, by construction.

[F] The one test that does not reuse the fitted numbers is the per-system abundance test in `m3_fermion_halo.out`.

It predicts each system's extra mass from the particle mass and compares it with the need. For one fully thermal species the correlation between predicted and needed is +0.05, +0.02, +0.02 and +0.03 for the four correction sets. Across all 16 rows it runs from +0.00 to +0.18. The rms error is 1.47, 0.90, 0.56 and 0.11 dex for those four sets.

[F] As a per-system predictor it fails in every row. The good rms of 0.11 dex for the lensing-high set comes with the packing cap binding in only 1 of 51 systems, so the prediction is close to one constant value. [I] The correction set that makes it work was itself chosen to close the radial mismatch on the same clusters (`n2_bias_scan.py`, `n3_efe_check.py`).

[F] If the richest clusters hold their full share, the solution is chi = (A/K)^(4/3) and m = K (K/A)^(1/3):

| Corrections | A, richest six | m and chi at K = 10.4 eV | m and chi at K = 13.4 eV |
|---|---|---|---|
| none | 3.3 eV | 15 eV, 0.21 | 21 eV, 0.15 |
| 0.03 a0, 20% | 6.3 eV | 12 eV, 0.51 | 17 eV, 0.36 |
| 0.03 a0, 31% | 8.4 eV | 11 eV, 0.75 | 16 eV, 0.54 |

There are two readings.

1. [I] **A fully thermal species near 11 eV whose clusters do not hold their full share.** The richest clusters would hold 30% of it inside the outer radius with no corrections and about 80% with the strongest. Then the ratio of extra mass to baryons should keep rising beyond the outer radius, toward 5.
2. [I] **A species of 11 to 21 eV populated at 15 to 75% of the thermal level, with the richest clusters holding all of it.** Then the ratio should level off beyond the outer radius. The load on the early universe is chi extra species, 0.15 to 0.75 in place of 1. The cosmic density is 0.035 to 0.09 in units where the standard cold component is 0.12.

[I] The second reading was not found in the literature searched. It lowers the two things the published tests object to: the early-universe load, and the amount of clustering matter that drives structure. Whether it lowers them enough has not been simulated.

## Galaxies

- [F] A halo at its packing limit in a galaxy with a flat speed of 200 km/s holds 0.00, 0.06 and 0.95 times the baryons inside 300 kpc at 3, 6 and 12 eV.
- [F] The lensing data give central values of 0.09 to 0.92 for that ratio, positive in every bin, with upper limits of 0.6 to 2.7 at two standard errors.
- [P] Relic particles of 12 eV move at about 13 km/s today (hep-ph/0408241). [I] Nothing keeps them out of galaxy-scale wells, so those wells should fill to the packing limit. At 10 to 13 eV that limit is where the lensing bound sits. Above it galaxies would overfill.
- [F] Inside the half-light radius of galaxies at redshift 1 to 2.5 the same halo is 1% of the total mass. That is consistent with the result that the standard relation alone describes them.
- [I] The excess inside early-type galaxies is not from such a particle. A stellar mass-to-light ratio 0.135 dex higher accounts for it, which is inside the span between the two usual choices.

[I] So the model makes a prediction that is within reach. Around isolated galaxies it expects extra mass of roughly half to once the baryons inside 300 kpc. Today's two-standard-error limits sit there. Lensing with errors halved would see it or exclude masses of 10 eV and above.

## What published work says against it

- [P] Simulations of modified gravity with 11 eV neutrinos produce too many very rich clusters and too few poor ones (1104.5040, 1309.6094). Poor clusters need more than 30 eV in those runs. Structure forms late (2305.05696).
- [P] A 2026 study finds the combination overproduces large-scale flows and excludes it at more than five standard errors (2602.21975).
- [P] A fully thermal 11 eV species adds about one light species. The standard analysis of the microwave background allows 2.99 ± 0.17 in all (1807.06209). [I] That limit assumes the standard cold-matter model.
- [P] Laboratory searches exclude a sterile state near 1 eV with large mixing. A heavier one with small mixing is not excluded (2503.18667, 2405.08557).
- [P] Two 2026 papers attribute the missing mass to ordinary matter: stellar remnants (2602.06082) and cold gas clouds that follow the hot gas (2611.08702).
- [I] The packing-limit formula appears in print with coefficients that differ by about three. If the smaller is right, published lower limits near 11 eV rise to about 13 eV. This was found by arithmetic on the published formulas and not checked with the authors.

[I] The objections are about how structure forms on large scales. The evidence for the particle is inside clusters. A proposal that keeps the second and eases the first has to lower the cosmic supply or change the large-scale force law, and both are outside what this pass could test.

## Can it be told apart from ordinary cold dark matter?

[I] Not with the data in hand. At 10 to 12 eV the halo's core is 30 to 50 kpc, well inside the inner radius used here.

## Observations that would decide

1. **Inner cluster profiles** from strong lensing and central-galaxy kinematics at 10 to 100 kpc. The particle predicts a ceiling on central density that scales as chi m^4 T^(3/2), about 2.6e8 solar masses per cubic kiloparsec for a thermal 11 eV species at 8 keV, and a core. Cold dark matter predicts a cusp.
2. **The ratio of extra mass to baryons beyond the outer radius.** Rising toward 5 favours the first reading. Levelling off favours the second.
3. **Lensing and X-ray masses for the same clusters at both radii.** The radial mismatch needs the X-ray shortfall to grow by about 20 points between them.
4. **Lensing around isolated galaxies at 50 to 300 kpc** with errors halved.

## Rerun

Programs and outputs are in `checks/neutrino/`. The scripts whose names start with `n` are the reviewer's. Those under `model/` are the halo study. Both read `checks/gravity/unified/unified_table.csv`. The scripts in `model/` also read cluster tables in `checks/gravity/sources/`.

From a fresh checkout, run `python3 checks/gravity/fetch_sources.py` once. It downloads the published tables and checks each against a recorded sha256. Then run `python3 checks/check_all.py` from `checks/`. It re-runs every program in a temporary copy and compares each output byte for byte with the saved file. That includes `n4_window.out`, `m2_combos.json` (written by `m2_radial.py`) and the halo model.

The program for `n4_window.out` was missing. It was rewritten from the description at the top of the file and reproduces the saved output exactly. The [P] values (published limits and simulations) are read from the papers and are not re-run.

## Not verified

- The halo study's profiles are simple curves through two radii. Published density models and larger radii were not used.
- The external field is treated with a one-dimensional formula.
- The radial, halo, galaxy and group programs are all re-run by `checks/check_all.py` and reproduce the saved outputs.
- The per-system abundance test fails as a predictor (see above), and the correction sets were chosen on the same clusters.
- Whether a species with the lower cosmic supply of the second reading forms structure acceptably.
- The factor of three in the packing-limit formula.
