# Thread: can a ring of charges beat a flat point?

15 November 2026. This answers one of the open avenues in the review's exploration note (pull request 60, `pr58-addendum/EXPLORATION.md`, avenue 3). Marks: **[F]** fact from a proof or a run, **[I]** inference, **[C]** conjecture.

## The question

The exploration note observes that one flat point gives at most order n^(3/2) balance points, and asks whether a degeneracy that is not a single point could give more. It names the cheapest test: families of rings on a common axis, where high-order vanishing along the axis costs few parameters.

The observation about cost is right, and it is worth stating exactly.

## Why rings make flatness cheap

[F] Take rings of N equal charges on a common axis, so that the configuration is unchanged by a turn of 1/N. At a point of the axis, every term of the Taylor series below degree N is unchanged by any turn about the axis. Such a term is a multiple of one zonal harmonic.

[F] So below degree N the potential near an axis point is fixed by its values on the axis, A(z):

```
f(rho, z) = sum over j of a_j r^j P_j(z / r),      A(z) = sum over j of a_j z^j
```

[I] The point is flat to order k as soon as a_1 to a_k vanish. That is k conditions. A general flat point of order k costs k² + 2k. Each ring brings three numbers, its radius, height and charge, so about k/3 rings are enough.

## What such a point is worth

Unfold it inside the family: small a_1 to a_k under a leading term of degree k + 1. The critical points of f are of two kinds. On the axis they are the real roots of A'(z), at most k. Off the axis they are whole circles.

**Claim.** If every critical point of f is non-degenerate, then

```
(critical points on the axis) + 2 (critical circles) = k
```

[F] Proof. Work in the plane of rho and z, with f continued evenly to negative rho. Off the axis f satisfies f_rho_rho + f_zz = -f_rho / rho. At a critical point the right side is zero, so the two-by-two Hessian has zero trace and the point is a saddle. On the axis f_zz = A'' and f_rho_rho = -A''/2, again a saddle.

Far from the origin the gradient is that of the leading term, r^(k+1) P_(k+1)(cos theta). Around a large circle that function of theta has 2(k + 1) simple zeros, so its gradient turns 1 - (k + 1) = -k times. The indices of the critical points add up to that number. Every critical point is a saddle with index -1, so there are exactly k in the plane. Each circle appears twice, at rho and at -rho.

[F] `checks/rings/circles_exact.py` tests the claim with exact resultants on 240 random polynomials with integer coefficients, for k from 2 to 7. It holds in 239. The one exception has a double root, which the claim excludes.

| k | Splits seen as (points on the axis, circles) |
|---|---|
| 3 | (1, 1) and (3, 0) |
| 5 | (1, 2) and (3, 1) |
| 7 | (1, 3) and (3, 2) |

## The answer for rings on one axis

[I] A point of the axis that is flat to order k gives at most k/2 circles. The charges are N to a ring, not a continuous ring, and the first term that sees this has degree N. It breaks each circle into 2N points. So the point is worth at most about N k balance points.

[I] The cost is about k/3 rings of N charges, which is N k / 3 charges. That is about 3 balance points per charge, however large k and N are. The known constructions give 10 per charge.

[I] So rings on one axis do not beat a flat point. They do worse than what is already known. The reason is the identity above: with one axis, the count behaves as it does in two dimensions, where a harmonic polynomial of degree d has d - 1 critical points and no more.

## What this says about the growth result

[I] The n^(3/2) growth in `growth.md` comes from crossing two families of zero circles, one about the z axis and one about the x axis. The number of crossings grows like the square of the degree. A single axis has no crossings. So the second axis is not a detail of that construction. It is what makes the count three-dimensional.

[C] The exploration note's wider question stays open. A critical curve that is not a circle of symmetry, or two ring systems on different axes, is not covered by the identity. The second is close to what `growth.md` already does.

## Rerun

```
python3 checks/rings/circles_exact.py 1 40
```

It needs SymPy. Saved output is `checks/rings/circles_exact.out`.

## Not verified

- The proof was written for this note and has not been checked by anyone else.
- The step from a ring of N charges to "each circle breaks into 2N points" is the standard picture for a small term with N-fold symmetry. It was not tested with actual charges.
- Only rings on one axis are covered.
