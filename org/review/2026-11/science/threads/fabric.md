# A woven hypothesis

15 November 2026. This file is a conjecture, not a result. It weaves the threads in this folder into one picture, states what that picture predicts in numbers, and lists what would kill it. Every strand is marked: **[F]** fact from data or a run, **[P]** a published value, **[I]** inference, **[C]** conjecture.

It is written down because the threads began to fit together, and a picture that is stated exactly can be tested. One that is only hinted at cannot.

## The strands

| Strand | Where | Status |
|---|---|---|
| Galaxies follow one relation with one acceleration scale, up to redshift 2.5 | `gravity.md`, `acceleration-evolution.md` | [F] holds in every sample tested |
| That scale does not grow with the expansion rate | `acceleration-evolution.md` | [I] the one fit possible leans against growth, not decided |
| Every massive class of system sits above the relation, more so with mass | `gravity.md` | [F] |
| No threshold speed is needed, and the "four speeds" are about two scales | `gravity.md` | [F] |
| A light fermion at its packing limit fits cluster cores | `neutrino-like.md` | [F] with published support, for strong corrections |
| The share a system holds rises with its depth | `neutrino-like.md` | [F], and a published simulation finds the same |
| The packing limit lets galaxy halos hold about as much as lensing allows | `neutrino-like.md` | [F] |
| Published simulations with such a particle overproduce rich clusters and large flows | `neutrino-like.md` | [P] |

## The hypothesis

1. [C] Gravity in galaxies follows the standard relation with one constant acceleration scale.
2. [C] There is one new light fermion, of about 11 eV, with no direct coupling to ordinary matter.
3. [C] It is populated at three quarters of the thermal level. That is the level reached if it shares particles equally with the three ordinary neutrinos after they have stopped interacting. Lower populations with a higher mass are also allowed (see the table).
4. [C] Its density is capped everywhere by the exclusion principle. It reaches that cap in the cores of clusters and in the outer halos of galaxies, and nowhere inside galaxies.
5. [C] The excess inside giant galaxies is not this particle. It is a matter of how much the stars weigh.

## What it predicts

Computed in `checks/fabric/fabric_numbers.py`. K is the mass of a fully thermal species with the same packing capacity. A is the mass of a fully thermal species with the same cosmic density.

| Species | K | A | Cosmic density (standard cold matter is 0.120) | Extra mass over baryons, cosmic | Same ratio inside 300 kpc of a 200 km/s galaxy |
|---|---|---|---|---|---|
| 11 eV, fully thermal | 11.0 eV | 11.0 eV | 0.118 | 5.3 | 0.67 |
| 11 eV at three quarters | 10.2 eV | 8.3 eV | 0.089 | 4.0 | 0.50 |
| 12 eV at three quarters | 11.2 eV | 9.0 eV | 0.097 | 4.3 | 0.71 |
| 15 eV at 0.40 | 11.9 eV | 6.0 eV | 0.064 | 2.9 | 0.93 |

For the central case, 11 eV at three quarters:

- [C] **Clusters.** The ratio of extra mass to baryons levels off near 4.0 in the richest clusters and is lower in poorer ones. [F] The six richest hold the equivalent of 8.4 to 8.8 eV if X-ray masses read 31% low at the outer radius, 6.3 eV at 20%, and 3.3 eV with no correction.
- [C] **Cluster cores.** The central density cannot exceed about 2.0e8 solar masses per cubic kiloparsec in an 8 keV cluster, and it scales as temperature to the power 3/2. The core is a few tens of kiloparsecs across.
- [C] **Galaxy halos.** Extra mass of about half the baryons inside 300 kpc of an isolated galaxy. [P] Lensing gives central values of 0.09 to 0.92 and upper limits of 0.6 to 2.7.
- [C] **High redshift.** Nothing changes inside galaxies at redshift 1 to 2.5. [F] That is what is seen.
- [C] **Large scales.** Structure grows faster than in the standard model and slower than in the published runs, because the supply is three quarters of theirs.
- [C] **The early universe.** No extra light species at nucleosynthesis. At recombination the count of light species is 2.3, because a quarter of the ordinary neutrinos have become this particle and it is already slow.

## What would kill it

1. **Galaxy lensing with errors halved** finds less than about 0.2 times the baryons inside 300 kpc.
2. **A cluster core** denser than the cap, or a cusp inside 30 kpc.
3. **The ratio of extra mass to baryons** keeps rising past 4 beyond the outer radius, or stays below 2 in the richest clusters once X-ray and lensing masses agree.
4. **The X-ray mass shortfall** at the outer radius turns out to be near 6%, as X-ray studies of outskirts report. Then the cores need more packing capacity than galaxy halos allow, and no single species fits.
5. **The light-species count at recombination.** [P] The standard analysis gives 2.99 ± 0.17. The central case predicts 2.3. Taken at face value this already disfavours it by four standard errors. That analysis assumes the standard cold-matter model, so the test is a re-analysis without that assumption.
6. **A simulation with three quarters of the supply** that still overproduces rich clusters and flows.

Item 5 is the weakest point of the central case. A species produced before the ordinary neutrinos decoupled avoids it and instead adds its population to the count at nucleosynthesis, which is constrained separately.

## Three suggestions, turned into tests

**Space may be less uniform than the scale on which the particle moves.**

- [P] This is close to the mechanism behind the published failure. A light particle streams freely and stays smooth below a scale that shrinks with time, while baryons clump. Growth is then held back on small scales and boosted on large ones, which is what the runs show.
- [P] The real universe is itself less uniform than the standard model expects. The measured bulk flow on scales of about 200 megaparsecs is in tension with it at 4.8 standard errors (2302.02028, 2311.17988). The published runs with this kind of particle overshoot in the same direction (2602.21975).
- [I] So the data sit between the two. A smaller supply moves the prediction down from the overshoot. This is testable by simulation and by nothing done here.

**The particle may be absent from the early-universe analysis.**

- [I] There is no point of origin for it to be far from: the hot early phase happened everywhere. But the suggestion has an exact counterpart in time. The limit counts species that were present and fast at two early moments. A species populated after the first of them is not counted there.
- [C] That is the central case above, and it makes the prediction in item 5.

**Observation itself may be skewing the results.**

- [I] Not through quantum measurement. Objects of this size are not disturbed by being observed.
- [F] Selection does skew results, and this pass met it twice: sorting galaxies by speed produced an excess that sorting by mass removed, and a slope that looked like confirmation was produced by the way the sample was chosen.
- [I] Every large-scale test also assumes a model in order to turn redshifts into distances and counts into masses. A five-standard-error exclusion is a statement inside those assumptions.
- [I] One quantum effect is central here, and it is not subtle. The cap in statement 4 is the exclusion principle acting on a gas tens of kiloparsecs across. [P] One of the papers reviewed notes that the published runs left out the pressure this produces (2009.11292).

## The mathematical weave

**Extreme counts come from unfolding a degenerate arrangement.**

- [F] The rigid graph with all 2,288 realizations real was found within 0.8% of equal edge lengths, where many solutions coincide.
- [F] The point-charge configurations that beat or meet Maxwell's bound add a very small charge at a balance point of a symmetric arrangement.
- [P] The same device settled a problem in gravitational lensing. A lens of n point masses can form at most 5n - 5 images (math/0401188). The bound is reached by placing masses on a regular polygon and adding a small one at the centre (astro-ph/0305166), and maximal lenses can be grown one small mass at a time (1405.2785).
- [I] Counting lensed images and counting balance points of charges are the planar and the spatial form of one question. The planar bound is proved. The spatial one, Maxwell's, was open for 150 years and is now known to be false. The planar proof and the growing construction are the natural places to look for the true spatial bound.
- [F] For 10 equal masses, the configurations hardest to find sit beside the regular polygon.

**Three threads are about packing.**

- [F] The code bounds limit how many codewords fit at a given distance. The lattice fold ends in the densest packing of spheres. The fermion cap limits how many particles fit in a region of position and speed.
- [I] Each is a bound proved by an exact certificate, and each was found by the same working method.

**One defect squares the denominator.**

- [F] `square-law.md` proves that allowing one defect in a strip squares the recurrence. [I] It is the counting form of a first-order response.

## What this picture does not explain

- Why the acceleration scale has the value it has.
- How structure forms with this supply. Nothing here computes it.
- The excess inside early-type galaxies, beyond saying it is stellar.
- Anything about the nature of the particle beyond its mass and population.

It is a hypothesis about what the missing mass in clusters is. It is not a theory of gravity and not a unification.

## Next steps, in order of cost

1. Fit the same cluster sample with published density profiles out to the largest measured radius, to see whether the ratio levels off.
2. Compare inner cluster profiles from lensing with the density cap.
3. Redo the light-species count at recombination with the cold component replaced by this particle.
4. Run structure formation with three quarters, one half and one third of the published supply, with degeneracy pressure included.
