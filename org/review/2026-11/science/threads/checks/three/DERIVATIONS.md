# Three charges: derivations behind the structural lemmas and the equilateral certificate

This file writes out every hand argument that `three-charges.md` and `NOTES.md` state in one line. Each statement carries one label.

- **Proved here.** The full argument is in this file.
- **Checked by program.** A program evaluates a finite list of inequalities. The file names the program and says which inequalities it checks.
- **Numerical.** Floating-point evidence, not a proof.

File names are relative to `checks/three/`.

## 1. Setting and notation

Three sites a1, a2, a3 in space are not on one line. They span a plane, called the plane below. The charges q1, q2, q3 are positive. Write r_i = |x - a_i|.

```
V(x) = q1/r1 + q2/r2 + q3/r3        x in R^3, x not a site
v    = V restricted to the plane    (the planar potential)
```

Coordinates put the plane at z = 0. In the plane, a1 = (0,0), a2 = (1,0) and a3 = (a,b) with b > 0, so the triangle T = a1 a2 a3 is counterclockwise. T° is its open interior.

Each site is a pole of v, since v tends to plus infinity there. At infinity v tends to 0 from above.

Only the ratios of the charges matter for the critical points. The charge-ratio simplex is the set of positive triples up to a common positive factor. We often use the chart rho2 = q2/q1, rho3 = q3/q1.

A balance point is a critical point of V. The words minimum, saddle and degenerate refer to v and its 2 by 2 Hessian unless stated otherwise.

## 2. L1: every balance point lies in the plane (proved here)

Differentiate V across the plane:

```
dV/dz = - z * sum_i q_i / r_i^3
```

The sum is positive, so dV/dz vanishes only at z = 0. At z = 0 the in-plane partial derivatives of V are those of v. So the balance points of V are exactly the critical points of v.

At a point of the plane the mixed derivatives d2V/dx dz and d2V/dy dz equal z times a smooth function, so they vanish. The Hessian of V is block diagonal there. One block is the Hessian of v. The other entry is

```
V_zz = - sum_i q_i / r_i^3  <  0.
```

So V is non-degenerate at a balance point exactly when v is. The Morse index of V is the index of v plus 1.

## 3. L2 and L3: the planar Laplacian and the index count (proved here)

**L2.** V is harmonic away from the sites. So, in the plane,

```
v_xx + v_yy = - V_zz = C(x),    C(x) = sum_i q_i / r_i^3 > 0.
```

The Hessian of v has positive trace everywhere. So v has no local maximum. A non-degenerate critical point is a minimum (index +1 for the gradient field) or a saddle (index -1). At a degenerate critical point the Hessian eigenvalues are 0 and C, so there is exactly one soft direction.

**Critical points lie in the open triangle.** This is proved in section 4 and used here only to know that the critical points form a compact set away from the sites.

**L3.** Assume every critical point of v is non-degenerate. Then they are isolated, and by the remark above they lie in a compact subset of T°, so there are finitely many. Let m be the number of minima and s the number of saddles. Then s - m = 2.

*Proof.* Let g = grad v = - sum_i q_i (x - a_i)/r_i^3. Take a disk D_R of radius R centred at a1 that contains T, and disks D_i of small radius e around the sites. In the region G = D_R minus the three small disks, g has only the critical points as zeros. The sum of their indices equals the winding number of g along the boundary of G. Here the outer circle is taken counterclockwise and each inner circle clockwise.

*The outer circle (infinity).* Put Q = q1 + q2 + q3 and h(x) = -Q x/|x|^3. For |x| = R each term obeys |(x - a_i)/|x - a_i|^3 - x/|x|^3| <= c/R^3 for a constant c that depends only on the sites. So |g - h| <= Q c/R^3, which is less than |h| = Q/R^2 once R > c. The straight-line homotopy from h to g has no zero on the circle. The field h points along -x, and x -> -x has degree 1. So the winding number is +1.

*The small circles (the poles).* On |x - a_i| = e, g = -q_i (x - a_i)/e^3 + B with |B| bounded independently of e. For small e the first term dominates. Taken counterclockwise its winding number is +1, so clockwise it is -1 for each site.

The total is 1 - 3 = -2. Each minimum contributes +1 and each saddle -1, so m - s = -2. ∎

**Consequences (proved here).** For a non-degenerate configuration the number of balance points is N = s + m = 2m + 2. So N <= 4 exactly when m <= 1, and N <= 6 exactly when m <= 2. The second statement is the bound of arXiv:2607.28785. Its last section also states that m <= 1 is equivalent to Maxwell's bound.

## 4. L4: the inverse map (proved here)

**Critical points lie in T°.** Let x be a point of the plane outside the closed triangle. A line strictly separates x from T. So there is a unit vector e with e.(x - a_i) > 0 for i = 1, 2, 3. Then

```
e . g(x) = - sum_i q_i e.(x - a_i)/r_i^3 < 0.
```

Now let x lie on an open edge, say between a1 and a2. Take e normal to that edge and pointing away from a3. Then e.(x - a1) = e.(x - a2) = 0 and e.(x - a3) > 0, so again e.g(x) < 0. The same separating-plane argument in space shows that V has no balance point outside the closed triangle.

**The inverse map.** Put c_i = q_i/r_i^3 > 0. The equation g(x) = 0 reads sum_i c_i (x - a_i) = 0, that is

```
x = sum_i (c_i / sum_j c_j) a_i .
```

The sites are affinely independent, so barycentric coordinates are unique. Hence x is critical for q exactly when c_i / sum_j c_j = beta_i(x), the barycentric coordinates of x. Equivalently:

```
x is critical for q   <=>   q is proportional to ( beta_1 r_1^3 , beta_2 r_2^3 , beta_3 r_3^3 ).
```

For x in T° all beta_i are positive, so the right side is a valid charge vector. Define the inverse map Z from T° to the simplex by Z(x) = [beta_i(x) r_i(x)^3].

Then the critical points of v_q are exactly the points of Z^{-1}([q]). Every interior point is a balance point for exactly one charge ratio. Z is real analytic on T°.

## 5. L5: the minimum criterion (proved here)

For f(y) = 1/|y| in space, the Hessian is (3 y y^T - |y|^2 I)/|y|^5. At a point of the plane, with an in-plane unit vector u_i = (x - a_i)/r_i, its in-plane block is (3 u_i u_i^T - I)/r_i^3. So

```
Hess v(x) = sum_i c_i (3 u_i u_i^T - I),     c_i = q_i / r_i^3 .
```

At a critical point, c_i = C beta_i with C = sum_j c_j (section 4). So

```
Hess v = C (3M - I),     M = sum_i beta_i u_i u_i^T,     trace M = 1.
```

Write u_i = (cos t_i, sin t_i), where t_i is the direction from a_i to x. Then u u^T = I/2 + (1/2) [[cos 2t, sin 2t], [sin 2t, -cos 2t]]. So, with the complex number

```
m(x) = sum_i beta_i(x) exp(2 i t_i(x)),
M = I/2 + (1/2) [[Re m, Im m], [Im m, -Re m]].
```

The eigenvalues of M are (1 ± |m|)/2. Those of Hess v are therefore C(1/2 + 3|m|/2) and C(1/2 - 3|m|/2). Hence, at a critical point x:

- x is a non-degenerate minimum exactly when |m(x)| < 1/3,
- x is degenerate exactly when |m(x)| = 1/3,
- x is a saddle exactly when |m(x)| > 1/3,
- the Hessian is positive semi-definite exactly when |m(x)| <= 1/3. This holds at every local minimum, strict or not.

The equivalent form det M > 2/9 in `NOTES.md` follows from det M = (1 - |m|^2)/4.

**A bound used by the certificate.** By the triangle inequality, |m| >= beta_i - sum over j != i of beta_j = 2 beta_i - 1. So |m| <= 1/3 forces beta_i <= 2/3 for every i.

Call R = { x in T° : |m(x)| < 1/3 } the minimum region. By the above, Z restricted to R lists the charge ratios with a non-degenerate minimum, together with where that minimum sits.

## 6. L6: every triangle has a point with m = 0 (proved here)

m is continuous on the closed triangle minus the three vertices, because the formula needs only x different from each site.

**On an open edge.** On the edge a1 a2, beta_3 = 0 and u1, u2 are plus or minus the edge direction. So exp(2i t_1) = exp(2i t_2) = exp(2i phi_12), where phi_12 is the angle of the edge. Hence m = (beta_1 + beta_2) exp(2i phi_12), and |m| = 1. The other edges are the same.

**Near a vertex.** Let x = a_i + p (cos t, sin t) with small p > 0 and t in the vertex's angular range. Then beta_i = 1 - p * (a bounded factor), since 1 - beta_i is the distance to the opposite side measured in units of the height. So |m - exp(2it)| <= 2(1 - beta_i) <= K p, uniformly in t.

**The loop.** Fix p so small that K p < 1. Let Gamma be the boundary of T with a circular arc of radius p cut out at each vertex, traversed counterclockwise. Gamma lies in the closed triangle minus the vertices. It bounds the region G_p, which is T with three small sectors removed.

On the edge pieces m is a constant of modulus 1. On the arc at a_i, m stays within distance K p < 1 of exp(2it). So m is homotopic in C minus 0 to the loop that equals exp(2it) on the arcs and the same constants on the edges. The pieces join continuously, because the arc ends point along the edges.

**Its winding.** Traversing Gamma counterclockwise, the arc at a_i is followed clockwise as seen from a_i. Along it t decreases by the interior angle alpha_i, so arg m decreases by 2 alpha_i. The edges contribute nothing. The total change is -2(alpha_1 + alpha_2 + alpha_3) = -2 pi, so the winding number is -1.

If m had no zero in G_p, then m/|m| would extend over the disk G_p and the winding number would be 0. So m has a zero in G_p. It is not on the edges, where |m| = 1, so it lies in T°. ∎

At that point |m| = 0 < 1/3, so the minimum region R is not empty. Every triangle carries a non-degenerate minimum for the charges Z(x*).

## 7. The equivalences

**7a. Regular values (proved here).** Write F(x, rho) = grad v_q(x) with q = (1, rho2, rho3). Then F(x, Z(x)) = 0 on T°. Differentiating gives

```
Hess v(x) + F_rho(x) DZ(x) = 0,    F_rho = [ grad(1/r_2) , grad(1/r_3) ] = [ -u_2/r_2^2 , -u_3/r_3^2 ].
```

For x in T°, u_2 and u_3 are not parallel, so F_rho is invertible. Hence det DZ(x) = 0 exactly when x is a degenerate critical point of v_{Z(x)}. In particular det DZ is non-zero on R.

On each connected component of R, det DZ therefore keeps one sign.

By Sard's theorem the critical values of Z have measure zero. So for almost every charge ratio q, every critical point of v_q is non-degenerate.

**7b. Maxwell for one triangle (proved here).** For a fixed triangle T the following are equivalent.

1. Every non-degenerate configuration on T has at most 4 balance points.
2. Z is one-to-one on R.
3. For every positive q, v_q has at most one strict local minimum.

*(3) implies (1).* Non-degenerate minima are strict, and L3 gives N = 2m + 2.

*(1) implies (2).* Suppose x ≠ y in R with Z(x) = Z(y) = q. Both are non-degenerate minima of v_q. By the implicit function theorem they persist as two minima of v_q' for q' near q. Choose q' a regular value of Z (7a). Then v_q' is non-degenerate with m >= 2, so N >= 6, contradicting (1).

*(2) implies (3).* Let v_q have two strict local minima x, y. Take disjoint small circles around them on which v_q exceeds its value at the centre by some h > 0. For q' close enough to q, v_q' still has a local minimum inside each circle. Choose q' regular (7a). Those minima are non-degenerate, so they lie in R. They are distinct with the same image q', contradicting (2).

**7c. A sufficient condition (proved here).** Suppose the closure of R is a closed topological disk whose boundary is the fold curve F = {|m| = 1/3}, and suppose Z is one-to-one on F. Then Z is one-to-one on R.

*Proof.* Take q not in Z(F). Z has no zero of det DZ in R, and det DZ has one sign there. By degree theory the number of preimages of q in R equals, up to sign, the winding number of the closed curve Z(F) around q. Z(F) is a Jordan curve, so that number is 0 or 1.

For q in Z(F), two preimages in R would give two preimages for every nearby q', since R is open and det DZ ≠ 0. Some of those q' lie off the curve Z(F), which is a contradiction. ∎

The converse (simple fold image is necessary) holds only under genericity assumptions, described in 7d. It is labelled an inference in `three-charges.md`, which is accurate.

**7d. Degenerate events that would force two minima.** At a degenerate critical point p the Hessian has eigenvalues 0 and C > 0 (L2). By the splitting lemma (the Morse lemma with parameters), near p and for nearby parameters there are coordinates in which

```
v = phi(t) + s^2 .
```

Critical points of v near p correspond to critical points of phi, and minima to minima. The family has four parameters: two for the shape and two for the charge ratios.

**(i) A cusp of the plus kind (proved here, under one condition).** The cusp is phi''' = 0 with phi'''' > 0, so phi is like t^4. Assume the family unfolds it versally. That means the parameters move the coefficients (a, b) of the unfolding t^4 + a t^2 + b t independently, which is a rank condition and holds generically.

For a < 0 and b = 0 the unfolding has two local minima and one local maximum. So v has two minima and one saddle near p, which gives m >= 2 and N >= 6.

At a cusp of the minus kind (phi'''' < 0) the unfolding gives two saddles and one minimum, which is harmless.

**(ii) A point of fourth order (proved here, under the same kind of condition).** This is phi''' = phi'''' = 0 with a non-zero fifth derivative. The versal unfolding t^5 + a t^3 + b t^2 + c t contains, for example, the case phi' = k (t^2 - 1)(t^2 - 4). Its sign pattern is +, -, +, -, + with sign changes from minus to plus at t = -1 and t = 2. That is two minima, so m >= 2.

**(iii) A fold while another minimum exists (proved here).** Suppose at parameter p0 the point p is a fold (phi''' ≠ 0) and v has a non-degenerate minimum y ≠ p. On the side of the fold where a minimum and a saddle are born near p, y persists, so m >= 2.

**(iv) A transversal double fold (proved here).** Suppose that at p0 there are two distinct fold points, so p0 lies on two fold hypersurfaces S and S' that cross transversally. Near p0 they cut the parameters into four regions.

Crossing S changes m by a fixed e = +1 or -1, and crossing S' by e' = +1 or -1. The two folds are independent and all other critical points persist. So the four regions have m equal to m0, m0 + e, m0 + e' and m0 + e + e'.

These values contain three consecutive integers, all at least 0, so the largest is at least 2.

**(v) The converse for one generic triangle (inference).** Fix a triangle and let only the charges move. Suppose F is a smooth curve and Z(F) consists of fold arcs and finitely many cusps. Z(closure of R) is compact in the open simplex, so m = 0 for charges outside it.

Join a point with m = 2 to a point with m = 0 by a path that crosses Z(F) transversally at fold points. m changes by 1 at each crossing. The first crossing where m drops from 2 to 1 is a fold while another minimum exists, which is event (iii).

The genericity assumptions in (v) are not proved for every triangle. So the full equivalence "Maxwell exactly when no event (i) to (iv) occurs" is an inference. Each event forcing 6 is proved, given the versality condition in (i) and (ii).

## 8. L7: one small charge near the saddle of the other two (proved here)

**The model.** Two positive charges have a single balance point, on the segment between them. In space its Hessian is diag(2C', -C', -C'). The axial term is the second derivative of the sum of q/|x| along the axis, which is 2 sum q/r^3. Harmonicity and the symmetry about the axis give the other two.

In the plane the background is therefore C' diag(2, -1). Adding a small charge near that point and rescaling gives the model

```
F_L(X) = X1^2 - X2^2/2 + 1/|X| - L.X ,      X in the plane minus 0,   L in R^2.
```

That this model describes the limit of a flat triangle with a small third charge is an inference. The lemma below concerns the model itself.

**Lemma L7.** For every L, F_L has at most one strict local minimum.

**Critical points as roots in one variable.** grad F_L = (2 X1, -X2) - X/|X|^3 - L. Write X = r (cos f, sin f) and c = r^{-3} in (0, infinity), so r = c^{-1/3}. Then grad F_L = 0 reads

```
L1 = h(c) cos f,    L2 = - g(c) sin f,    h(c) = (2 - c) c^{-1/3},    g(c) = (1 + c) c^{-1/3}.
```

Assume first that L1 ≠ 0. Then c ≠ 2, since h(2) = 0. For c ≠ 2 the pair (cos f, sin f) = (L1/h, -L2/g) is a unit vector exactly when

```
P(c) = c^{2/3} [ L1^2/(2-c)^2 + L2^2/(1+c)^2 ] = 1 ,
```

and then f is unique. So the critical points correspond one to one with the roots of P = 1 in (0,2) and (2, infinity).

**The Hessian.** Hess F_L = diag(2, -1) + c (3 u u^T - I) with u = (cos f, sin f). Its trace is 1 + c > 0. Its determinant is

```
det = (2 - c + 3c cos^2 f)(-1 - c + 3c sin^2 f) - 9 c^2 cos^2 f sin^2 f = 9 c sin^2 f - 2 (1 + c)^2 .
```

A minimum needs 9c > 2(1+c)^2, that is (2c - 1)(c - 2) < 0, so c lies in (1/2, 2).

**Minimum means P decreasing.** Let Phi(c,f) = (h cos f, -g sin f) and X(c,f) = c^{-1/3}(cos f, sin f). Phi equals G(X), where G is the gradient of X1^2 - X2^2/2 + 1/|X|. Its derivative is Hess F_L. So det DPhi = det Hess F_L times det DX.

Here det DX = r dr/dc < 0. Direct computation gives det DPhi = -h' g cos^2 f - h g' sin^2 f. At a root, where cos f = L1/h and sin f = -L2/g,

```
P'(c) = -2 L1^2 h'/h^3 - 2 L2^2 g'/g^3 = (2/(h g)) det DPhi .
```

For c in (0,2), h g > 0. So the sign of det Hess F_L is minus the sign of P'(c). A root in (0,2) is a non-degenerate minimum exactly when P'(c) < 0.

**Counting on (2, infinity).** There P = L1^2 p1 + L2^2 p2 with p1 = c^{2/3}(2-c)^{-2} and p2 = c^{2/3}(1+c)^{-2}. Here p1'/p1 = 2/(3c) - 2/(c-2) < 0, since 3c > c - 2. Also p2'/p2 = (2 - 4c)/(3c(1+c)) < 0. So P falls strictly from +infinity to 0, giving exactly one root. It is a saddle, since c > 2.

**Counting on (0,2).** P(0+) = 0 and P(2-) = +infinity. p1 is increasing on (0,2). p2 is increasing on (0, 1/2] and decreasing after, so P' > 0 on (0, 1/2]. On (1/2, 2), -p2' > 0 and

```
P'(c) = (-p2'(c)) * ( L1^2 R(c) - L2^2 ),      R(c) = p1'/(-p2') = 2 (1+c)^4 / ( (2-c)^3 (2c-1) ).
```

Derivation of R: p1'/p1 = (4 + 4c)/(3c(2-c)), -p2'/p2 = (4c - 2)/(3c(1+c)) and p1/p2 = (1+c)^2/(2-c)^2. Multiplying gives the formula above.

**R has a single critical point on (1/2, 2).**

```
(log R)' = 4/(1+c) + 3/(2-c) - 2/(2c-1).
```

Multiply by (1+c)(2-c)(2c-1) > 0:

```
4(2-c)(2c-1) + 3(1+c)(2c-1) - 2(1+c)(2-c)
  = (-8c^2 + 20c - 8) + (6c^2 + 3c - 3) + (2c^2 - 2c - 4) = 21 c - 15 .
```

This vanishes only at c = 5/7 and changes from negative to positive there. R tends to +infinity at both ends, so R decreases on (1/2, 5/7] and increases on [5/7, 2).

**Conclusion for L1 ≠ 0.** The set where R exceeds L2^2/L1^2 is (1/2, c1) together with (c2, 2), and the set below is (c1, c2), possibly empty. So P increases on (0, c1], decreases on [c1, c2] and increases on [c2, 2).

The equation P = 1 has at most three roots in (0,2) and at most one root with P' < 0. Hence F_L has at most one non-degenerate minimum.

**All L, strict minima.** Suppose F_L had two strict local minima. They persist as local minima for L' near L. Choose L' with L1' ≠ 0 and L' a regular value of G, which is possible by Sard's theorem. Then those minima are non-degenerate, which contradicts the conclusion above. ∎

`l7_check.py` compares a two-dimensional Newton count with the root count of P on 400 random L, and finds agreement and never two minima. This is numerical.

## 9. The certificate for the equilateral triangle

### 9.0 What is checked by which program

- `run_cert3.py` with `cert3.py` and `iv.py` is the primary engine. It does the full run: coverage, every leaf certificate, and the pair step. Its saved output is `out/c3_equi.json`, `out/c3_equi_leaves.npy` and `out/c3_equi.log`.
- `verify_arb3.py` is an independent re-check in ball arithmetic. It re-checks coverage and every leaf certificate.
- `verify_pairs_arb3.py` re-checks the pair step on 200 random non-trivial leaf pairs only.

The statements in 9.1 to 9.5 below are proved here. Each says that a set of inequalities, if it holds, implies a conclusion. The programs check the inequalities.

The shape is a = 1/2 with b in the interval [0.8660254037844385, 0.8660254037844387]. This interval contains sqrt(3)/2, since the squares of its endpoints straddle 3/4. Every formula is evaluated with b as an interval, so each conclusion holds for every b in it, and in particular for the exact equilateral triangle.

### 9.1 Soundness of the arithmetic (proved here)

The primary engine uses float64 intervals. After every +, -, *, / and square root, it widens the lower end down by one unit in the last place and the upper end up by one. IEEE 754 rounds these five operations correctly, so every computed interval contains the exact range. No other function is used in a proof step.

Where a box touches a site, 0 times infinity can produce NaN. The code then falls back to the bounds [-1, 1] for cos and sin of 2t, which are always true.

### 9.2 Coverage: every local minimum lies in a candidate box (proved here, checked by program)

Coordinates are (beta2, beta3), so x = beta2 a2 + beta3 a3. The dyadic grid of side 2^-5 on the unit square, restricted to boxes whose lower-left corner has beta2 + beta3 < 1, covers T. A box whose lower-left corner has beta2 + beta3 >= 1 lies where beta1 <= 0, which is outside T°.

A box is discarded when one of two things holds. Either a rigorous lower bound of |m|^2 over the box exceeds 1/9, or some beta_i exceeds 2/3 on the whole box, which gives |m| > 1/3 by section 5. Otherwise it is split, down to side 2^-8.

The boxes that remain are the candidate boxes. Every local minimum of every v_q has |m| <= 1/3 (section 5), so it lies in a candidate box.

The lower bound of |m|^2 uses enclosures of cos 2t_i, sin 2t_i and beta_i. cos 2t is enclosed both as 1 - 2 y^2/r^2 and as 2 x^2/r^2 - 1, and the two enclosures are intersected.

Checked by `run_cert3.py` (2645 candidate boxes) and again by `verify_arb3.py`.

### 9.3 The Jacobian test (proved here, checked by program)

Let N be a box (in beta coordinates) on which each beta_i is bounded away from 0. N is convex and meets T°, so each beta_i keeps its sign on N and is positive there. Set

```
Lam(x) = ( log rho2 , log rho3 ),   rho_i = beta_i r_i^3 / (beta_1 r_1^3),
d log rho_i / d beta_k = delta_ik / beta_i + 1/beta_1 + 3 d_i . P_k / r_i^2 - 3 d_1 . P_k / r_1^2 ,
```

where d_i = x - a_i, P_2 = (1, 0) and P_3 = a3 = (a, b).

Let x, y be points of N. The segment between them lies in N. By the mean value theorem, applied to each component on its own, Lam_k(y) - Lam_k(x) = grad Lam_k(xi_k).(y - x) for some xi_k on the segment. So

```
Lam(y) - Lam(x) = Jbar (y - x),     row k of Jbar = grad Lam_k(xi_k).
```

The two rows come from different points. Every entry of Jbar lies in the interval enclosure [J_kl] of that entry over N.

The expression det = J22 J33 - J23 J32 uses each entry once. So its interval evaluation contains the determinant of every matrix whose entries lie in those intervals, and in particular det Jbar. If that interval excludes 0, Jbar is invertible and Lam(y) = Lam(x) forces y = x. Then Z is one-to-one on N.

A pointwise sign of det DZ on N would not be enough here, because the rows of Jbar come from different points.

For a leaf of kind J the program checks this on N = the leaf box enlarged by two box widths on each side.

### 9.4 The valley test (proved here, checked by program)

**The setting.** Take a cell C = { c + tau t + sig s : |tau| <= ht, |sig| <= hs }, where t and s are fixed, linearly independent vectors. Take a box Q of charge ratios with q = (1, rho2, rho3). Write V for v_q, V_s for the derivative along s, and D^kV[...] for the k-th derivative applied to vectors.

The program checks, for all q in Q:

```
(V1)  V_ss > 0 on C;
(V2)  V_s < 0 on the edge sig = -hs and V_s > 0 on the edge sig = +hs, for all |tau| <= ht;
(V3)  psi3 = D3V[w,w,w] has one strict sign on C,   w = t - (V_ts / V_ss) s ;
  or
(V4)  psi4 = D4V[w,w,w,w] - 3 D3V[w,w,s]^2 / V_ss < 0 on C.
```

**Claim.** Then, for each q in Q, v_q has at most one local minimum in C.

**The valley curve.** Fix q. For each tau, the map sig -> V is strictly convex on [-hs, hs] by (V1). Its derivative is negative at the left end and positive at the right end by (V2). So there is a unique minimiser sig*(tau) in the open interval, and it is the only zero of V_s on that segment.

By the implicit function theorem, using V_ss ≠ 0, sig* is smooth on [-ht, ht]. Call its graph the valley curve. Every critical point of V in C has V_s = 0, so it lies on the valley curve.

**The reduced function.** Put psi(tau) = V(tau, sig*(tau)). Since V(tau, sig) >= psi(tau), with equality on the valley curve, the point (tau0, sig*(tau0)) is a local minimum of V exactly when tau0 is a local minimum of psi.

**Derivatives along the curve.** Write a = V_ts/V_ss, so sig*' = -a and the curve moves with velocity w = t - a s. The definition of a gives the identity

```
D2V[w, s] = V_ts - a V_ss = 0 .
```

Then:

```
psi'   = DV[w] = V_t                 (V_s = 0 on the curve)
psi''  = D2V[w,w] + DV[w'] = D2V[w,w]                       (w' = -a' s, DV[s] = 0)
psi''' = D3V[w,w,w] + 2 D2V[w,w'] = D3V[w,w,w]              (D2V[w,s] = 0)
```

Differentiating the identity D2V[w,s] = 0 along the curve gives D3V[w,w,s] - a' V_ss = 0, so a' = D3V[w,w,s]/V_ss. Hence

```
psi'''' = D4V[w,w,w,w] + 3 D3V[w,w,w'] = D4V[w,w,w,w] - 3 D3V[w,w,s]^2 / V_ss .
```

**Under (V3).** psi''' has one strict sign on the curve, which lies in C. So psi' is strictly convex or strictly concave. It has at most two zeros, and it changes sign from minus to plus at most once.

A local minimum of psi needs psi' <= 0 just before and psi' >= 0 just after. At a double zero of psi', the sign of psi' is the same on both sides and psi is strictly monotone there. So psi has at most one local minimum.

**Under (V4).** psi'' is strictly concave. So it has at most two zeros and sign pattern contained in (-, +, -). Then psi' decreases, increases and decreases on at most three intervals, strictly on each. A change of psi' from minus to plus can happen only on the increasing piece, and at most once. So psi has at most one local minimum. ∎

**How a leaf uses it.** For a leaf of kind V the program takes Q to be an enclosure of rho over the leaf box B. It also checks that B lies in C, and checks (V1), (V2) and (V3) or (V4) on a 4 by 4 split of C and a 4-piece split of each s-edge.

Conclusion (proved here): if x is in B, y is in C, and both are local minima of the same v_q, then q = Z(x) lies in Q, so x = y.

The derivatives of 1/|y| along in-plane vectors u, v, w, z are the spatial derivatives evaluated in the plane:

```
D2[u,v]     = 3 (y.u)(y.v)/r^5 - (u.v)/r^3
D3[u,v,w]   = -15 (y.u)(y.v)(y.w)/r^7 + 3[(u.v)(y.w) + (u.w)(y.v) + (v.w)(y.u)]/r^5
D4[u,v,w,z] = 105 (y.u)(y.v)(y.w)(y.z)/r^9 - 15 S6/r^7 + 3 S3/r^5
```

Here S6 sums (u.v)(y.w)(y.z) over the six ways to choose the pair that is dotted together. S3 is (u.v)(w.z) + (u.w)(v.z) + (u.z)(v.w).

### 9.5 The pair step (proved here, the inequalities checked by program)

The leaves cover the candidate boxes. Each leaf L_j has a region: the enlarged box N_j for kind J, or the cell C_j with its charge box for kind V. The pair step needs one fact about each leaf.

```
(*)  if x is in N_j (or C_j), y is in L_j, and x, y are local minima of the same v_q, then x = y.
```

For kind J this holds because Z is one-to-one on N_j, which contains L_j. For kind V it holds by 9.4.

**Claim.** No v_q has two distinct local minima in T°.

*Proof.* Suppose x ≠ y are local minima of v_q. By 9.2 they lie in candidate boxes, so in leaves L_i and L_j.

If i = j, then (*) applies directly, since L_i lies in its own region.

If i ≠ j and the rho-enclosures of L_i and L_j are disjoint, then Z(x) ≠ Z(y), which is impossible.

Otherwise the pair (L_i, L_j) is one of the 121,485 leaf pairs with overlapping enclosures, and the program processes it as follows.

The program takes a pair of sub-boxes (X, Y), with X inside L_i and Y inside L_j, and records one of three outcomes:

- **disjoint**: the rho-enclosures of X and Y do not meet. Then no x in X and y in Y have the same image.
- **contained**: X lies in the region of L_j, or Y lies in the region of L_i. Then (*) gives x = y.
- **split**: X and Y are each cut into four. Children outside the triangle, or with |m|^2 > 1/9 throughout, are dropped, since they hold no local minimum. The 16 child pairs are processed in turn.

The children of a split cover X times Y, minus points that cannot be local minima. The run ended with no unresolved pair, so (x, y) lies in a resolved sub-pair. That contradicts x ≠ y. ∎

By 7b this gives Maxwell's bound of 4 for every non-degenerate configuration on the equilateral triangle.

**What the count of 55 million means.** It is 54,941,484 sub-box pairs resolved as disjoint plus 197,271 resolved as contained. That makes 55,138,755 resolutions of sub-box pairs, produced by splitting the 121,485 overlapping leaf pairs. It is not a count of pairs among the 7,343 leaves. The source is `out/c3_equi.json` and `out/c3_equi.log`.

### 9.6 The charge-ratio window (checked by program, output not saved)

The rho-enclosures of all leaves lie in rho2 in [0.6421, 1.5836] and rho3 in [0.6635, 1.5834]. So a local minimum on this triangle needs both q2/q1 and q3/q1 in [0.642, 1.584]. Under relabelling of the vertices the equilateral triangle maps to itself, so the same window applies to every ratio q_i/q_j.

This was computed with `cert3.rho_centered` over `out/c3_equi_leaves.npy` in a one-off command. No output file for it is in the checkout.

## 10. What is still not proved

- The pair step of 9.5 rests on one program. `verify_pairs_arb3.py` re-checks 200 random non-trivial leaf pairs. A full second check was not run.
- No triangle other than the equilateral one is certified. The right isosceles and obtuse runs were stopped unfinished, and a box of shapes of width 7.6e-6 failed.
- The flat-triangle limit and the colliding-pair limit have no uniform bounds. L7 covers the model, but the passage from the model to the limit with explicit constants is not done. The uniform-field model L8 is numerical only.
- The genericity assumptions of 7d(v) are not proved for all triangles.
- The scans (`scan_shapes.py`, `cusp_scan.py`) and the sign of the cusp coefficient over the family are numerical.
- The versality condition used in 7d(i) and 7d(ii) is not checked along the family.
