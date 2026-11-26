# Thread: a referee's read of the elastic theorem and the fold

Follow-up to the science pass, 15 November 2026. Pinned head `incentre-lattices@2d374ff`. Marks: **[F]** fact, **[I]** inference.

## Question

The repository states the elastic constants of its lattice in every dimension, and an exact proof that the open cubic arrangement folds into the densest packing without any two balls overlapping. Both had been read only by AI agents. Do they hold under separate code and a step-by-step read, and are they new?

## The structure, restated

[F] In dimension n the joints sit at plus and minus c along each axis in every cell of the lattice 2Z^n, with c = 2 - sqrt(2). Bars join touching balls: the edges of each cross-polytope, plus one bridge per axis. Each bar is a unit spring that resists stretch only. In two dimensions this is the square-and-octagon tiling. In three it is the boron net of calcium hexaboride.

## The elastic theorem

Statement: C11/C12 = (n-1)^2, C44 = 0, and Poisson ratio 1/(n^2-n-1) along an axis.

- [F] Separate exact code (`checks/incentre/elastic_indep.py`, arithmetic in Q(sqrt 2), bars found by a distance search) gives these values for every n from 2 to 9. It shares no code with the repository.
- [F] The values do not change when the bridge-to-edge ratio changes. This was tried at three rational ratios, for n from 2 to 6 only.
- [F] A target corrupted by 1% is rejected, also under `python3 -O`.
- [F] Each step of the written proof was re-derived and follows.

Verdict: **VERIFIED** for n = 2 to 9. The general proof reads as complete, given two assumptions it does not state: the bars carry no stress at rest, and the constants are the relaxed ones, measured after the joints settle.

### One wording error

The repository says every shear modulus is zero. [F] That is true only for n = 2. The second shear modulus, (C11 - C12)/2, equals 2(n-2)/(n 2^n). It is 1/12 at n = 3 and positive for every n above 2. The correct statement is "C44 = 0".

### Why zero shear does not contradict a textbook rule

Springs that act along the line between points usually force C12 = C44. [F] Before the joints settle, this lattice obeys that rule exactly in every dimension. [F] No joint is a centre of symmetry, so the joints do settle. Each cross-polytope turns as a rigid body, which removes C44 and lowers C12. At n = 3, C12 falls from 0.0858 to 1/18.

[F] Each joint has 2n-1 bars, one fewer than the 2n needed for rigidity by counting. The relaxed stiffness has rank n. In three dimensions that leaves three soft modes.

## The fold

[F] The motion keeps the motif fixed and moves the lattice along one parameter. Every one of the 15 bars keeps its length. Each bridge swings through 90 degrees. The end state is the face-centred cubic packing with 12 contacts per ball, and the density rises all the way.

- [F] Both repository verifiers pass and the certificate regenerates identically.
- [F] Separate exact code (`checks/incentre/fold_indep.py`) proves no overlap for 6,516 pairs over the whole interval, against the repository's 3,248. It bounds distant pairs by a different argument and proves the density rises strictly.
- [F] Flipping one sign in the motion keeps every bar and makes balls overlap. The check then fails.

Verdict: **VERIFIED**. The certificate is in `results/fold-continuous-fcc/`.

## Is it new?

- [F] The closest source found is Borcea and Streinu (2021, section 7). It describes the same bar framework in any dimension and sketches a fold. It gives no spring constants and no proof that balls stay apart.
- [I] No earlier report was found of the ratio (n-1)^2 or the Poisson ratio 1/(n^2-n-1). The derivation is short, so a specialist may call it a worked example.
- [I] No earlier report was found of an explicit motion of this framework to the densest packing with every bar kept and an exact proof of no overlap. Known paths between packings, such as the Bain path, move bare balls with no bars.

Three sources were not read in full. This is "no earlier report found".

## Rerun

```
python3 -I checks/incentre/elastic_indep.py --nmax 9     # about 5 minutes, needs python-flint
python3 -I checks/incentre/fold_indep.py                 # about 2 seconds
```

## Next steps

1. Fix the wording to "C44 = 0, and (C11 - C12)/2 is positive above two dimensions". State the two assumptions.
2. Ask a specialist in frameworks whether the relaxed constants are the right ones to quote.
3. Offer the fold to the authors of the 2021 paper as an explicit, certified case of their sketch.
