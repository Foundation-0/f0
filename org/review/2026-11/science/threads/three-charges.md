# Thread: three charges, and whether two minima can exist

Follow-up to `maxwell-push.md` and `relational-geometry.md`, 15 November 2026. Marks: **[F]** fact from a run or a hand proof, **[P]** a published result, **[I]** inference, **[C]** conjecture.

## Result

The three-charge case is still open. This thread did not prove Maxwell's bound of 4 and did not find a configuration above it.

- [F] It is proved, with a computer, that three positive charges at the corners of an equilateral triangle have at most one minimum in the plane, whatever the charges. So they have at most 4 non-degenerate balance points. Status: REPRODUCED. One program proves it in full. A second, written with a different arithmetic library, re-proves the first half in full and the second half on a sample.
- [F] Across 2,184 triangle shapes and 4,866 sampled cusps, no sign of a second minimum was found.
- [F] The problem is reduced to one statement about folds, given below.

## What is published

- [P] arXiv:2607.28785: three positive charges have at most 6 non-degenerate balance points. Its last section says that at most one minimum would be equivalent to Maxwell's bound.
- [P] arXiv:math-ph/0409009: the earlier bound of 12.
- [P] The case of three equal charges is settled in work by Tsai. That work was not read here.

## The structure of the problem

All of these are proved by hand in the thread's notes, `checks/three/NOTES.md`.

- [F] Every balance point lies in the plane of the charges. In that plane the charges are peaks, and the other critical points are saddles and minima. Saddles minus minima is 2.
- [F] Maxwell's bound of 4 is 3 saddles and 1 minimum. The proved bound of 6 allows 4 saddles and 2 minima. So the whole question is whether two minima can exist.
- [F] **The inverse map.** A point x inside the triangle is a balance point exactly when each charge is proportional to the barycentric coordinate of x at that corner times the cube of its distance from x. So every interior point is a balance point for exactly one set of charge ratios.
- [F] **When it is a minimum.** Put m(x) for the sum over corners of the barycentric coordinate times the unit complex number at twice the direction angle from the corner to x. Then x is a minimum exactly when |m(x)| is below 1/3.
- [F] Every triangle has a point where m is zero, so every triangle has a minimum for some charges.

[I] In the language of `flat-centres.md`: reflect the charges in a circle about x. The point x is a minimum when the second moments of the reflected charges are round enough, with the smaller more than half the larger.

**The reduction.** Call the set where |m| is below 1/3 the minimum region. The inverse map sends it to the charge ratios that have a minimum.

- [F] Two minima exist for some charges exactly when the inverse map sends two points of the minimum region to the same charge ratios.
- [I] For a generic triangle that happens exactly when a fold occurs while another minimum exists. A cusp of the kind that splits into two minima and a saddle, a fold of higher order, or two folds crossing would each force 6 balance points.
- [I] So Maxwell's bound for three charges is the statement that the image of the fold curve under the inverse map is a simple closed curve with only the harmless kind of cusp, for every triangle.

## Evidence

- [F] `scan_shapes.py` traced the fold curve for 2,184 triangle shapes, down to very flat ones. In every shape the minimum region is one piece, the image of its boundary has 3 cusps and does not cross itself.
- [F] `cusp_scan.py` sampled 4,866 cusps over the whole family. The coefficient that decides the kind of cusp, scaled, is at most -1/3 in all of them. A positive value would mean two minima. The value -1/3 is approached only when one charge is small and near the saddle of the other two.
- [F] A separate search by the reviewer, `degenerate3_reviewer.py`, solves for cusps directly from 400 random starts with its own reduction to one variable. It found 88 cusps. The fourth derivative is negative at all 88, the harmless kind.
- [F] The same program, asked for points of fourth order, which would force 6 balance points, found none from 250 starts.
- [F] **A local lemma.** A small charge near the saddle of the other two has at most one minimum. The proof reduces to counting roots of one equation in one variable. A numerical check on 400 random cases agrees.
- [F] The limit where two charges collide, modelled as two charges in a uniform field, shows the same simple picture. That model is not proved.

## The equilateral triangle, for all charges

[F] `run_cert3.py` covers the minimum region of the equilateral triangle with boxes. It then proves both of the following.

1. In each of 7,343 small boxes the inverse map is one-to-one. The test is a sign of the Jacobian, or, near the fold, a sign of the third or fourth derivative across a valley.
2. No two different boxes share a set of charge ratios. That is 55 million pairs, each shown to have disjoint images or one image inside a region already handled.

- [F] The arithmetic is interval arithmetic with outward rounding. The run takes about six minutes and ends with `RESULT PROVED`.
- [F] A separate program, `verify_arb3.py`, uses ball arithmetic from another library and shares no code with the first. It re-proves the coverage and all 7,343 box certificates. For the pairs it re-proves 200 chosen at random, and all 200 pass.
- [F] Three corrupted certificates are rejected, also under `python -O`.
- [F] The certificate shows as a by-product that a minimum exists only when every ratio of two charges lies between 0.642 and 1.584.

[I] The pair step is the part that rests on one program. A full second check of the 55 million pairs was not run.

## What did not work

- [F] The same method on a box of triangle shapes around the equilateral one, of width 7.6e-6, left 4,693 pairs unresolved. Near the fold the method loses the link between the shape and the image.
- [F] Runs for a right isosceles triangle and an obtuse triangle were stopped unfinished. Neither had failed.
- [I] So the proved cases are single triangles, a set of measure zero in the family of shapes.

## A lesson from the four-charge result

[I] For four charges, random search and pushes found nothing above 9, and the answer was a needle that survives changes of one part in a million. It was found only by solving for a degenerate point. So the absence of a second minimum in random searches is weak evidence. This thread did look for degenerate points directly, which is the right test, and found only the harmless kind.

## Open

1. A proof that the image of the fold curve is simple for every triangle. That would settle the three-charge case.
2. A certificate method that keeps the link between shape and image, so that it works on boxes of shapes.
3. Uniform bounds in the two limits, a flat triangle and two colliding charges.

## Rerun

From `checks/three/`, with NumPy, SciPy and python-flint installed. `run_all.sh` lists every command.

```
python3 run_cert3.py 0.5 0.5 0.8660254037844385 0.8660254037844387 out/c3_equi 5 8 2 6
python3 -O verify_arb3.py out/c3_equi 3000
python3 -O verify_pairs_arb3.py out/c3_equi 200 12
sh run_corrupt.sh
python3 cusp_scan.py 200
```

## Not verified

- The equilateral result rests on one program for the pair step.
- The scans of shapes and cusps are numerical.
- The reviewer re-ran the second program. It again proved the coverage and all 7,343 box certificates, and resolved 400 of 400 sampled pairs, 200 of them beyond the thread's own sample. The reviewer did not re-run the first program or write a third.
- Whether the equilateral result is new was not checked beyond the three papers named above.
