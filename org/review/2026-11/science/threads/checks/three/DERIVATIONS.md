# Three charges: the hand derivations

This file writes out in full the hand proofs that `three-charges.md` relies on. These are the lemmas listed as L1 to L7 in `NOTES.md`, and the lemmas behind the computer proof in `run_cert3.py` and `verify_arb3.py`: exclusion, coverage, the injectivity test (kind J), the valley test (kind V) and the pair step.

Formulas carry labels D1 to D52. The program `derivations_check.py` checks every one of them, symbolically with SymPy where it can, and otherwise at random points with mpmath at 50 digits. It also checks that the thread's programs compute these formulas (checks X1 to X9), and it reproduces the example behind one correction to the note (check N1). Its output is `derivations_check.out`.

Rerun from this directory: `python3 -O derivations_check.py`. It needs SymPy, mpmath, NumPy and python-flint, and takes about 20 seconds. `python3 -O derivations_check.py --flip psi4` corrupts one formula on purpose and must fail.

## Status: read this first

Every lemma below holds as stated here. Writing them out showed that five sentences of `three-charges.md` said more than was proved. Each was corrected with the smallest change.

1. **Lemma 3 needs non-degeneracy.** "Saddles minus minima is 2" holds when every critical point is non-degenerate. A degenerate critical point can be neither a saddle nor a minimum. Line 23 of the note now says so. The conclusion the note draws from it (at most one minimum gives at most 4 non-degenerate balance points) holds for every charge vector, by Corollary 11.1.
2. **Lemma 5 characterises non-degenerate minima.** |m| < 1/3 is exactly a non-degenerate minimum. At |m| = 1/3 the Hessian is singular and decides nothing. Line 26 now says "non-degenerate minimum". The certificate uses only the safe direction: every local minimum, degenerate or not, has |m| <= 1/3.
3. **Lemma 7 is about a limit model.** It is proved for the scaling model F_L, the limit of a small charge near the saddle of the other two. The step from the model to actual small charges is not proved, here or elsewhere in the thread. Line 43 now says "In the limit model".
4. **The inverse map is not one-to-one on every box.** Line 50 said it is. That holds for the 3,015 boxes of kind J. It fails for boxes of kind V that cross the fold, where the inverse map is two-to-one: a minimum and a saddle share their charges. Check N1 exhibits such a pair inside one valley box at 50 digits. In floating point, 375 of the 4,328 valley boxes cross the fold. What the valley test proves is that no two minima share their charges there (Lemma 13). Line 50 now says "one-to-one on the minima".
5. **Different boxes can share charge ratios.** Line 51 said no two different boxes share a set of charge ratios. Neighbouring boxes do, and 197,271 pairs were resolved by containment rather than by separation. What is proved is that no two different boxes hold minima for the same ratios (Lemma 14). Line 51 now says so, and "one image inside a region" now reads "one box inside a region".

Nothing in the mathematics of the certificate turned out false. The valley formulas and the injectivity argument are the ones the reviewer reconstructed. Two hypotheses that the code relies on are now explicit, and both hold for the archived run (check D47). Every J region lies inside the open triangle (Lemma 12). Every leaf box lies inside it too, so every enclosure of the charge ratios is finite (remark after Lemma 14).

## 0. Setting and notation

- Sites A_1, A_2, A_3 lie in a plane and are not on one line. Charges q_1, q_2, q_3 are positive. In space the plane is z = 0.
- V(X) = sum_k q_k / |X - A_k| for X in R^3. A balance point is a critical point of V. On the plane, V also denotes the restriction of V.
- The index k runs over 1, 2, 3. When (k, l, n) appears, it is a cyclic order of (1, 2, 3). The letter i is the imaginary unit.
- For a point x of the plane other than a site: y_k = x - A_k, r_k = |y_k|, u_k = y_k / r_k = (cos θ_k, sin θ_k). So θ_k is the direction angle from A_k to x.
- β_1, β_2, β_3 are the barycentric coordinates of x: x = sum_k β_k A_k with sum_k β_k = 1. T is the open triangle, where every β_k > 0.
- m(x) = sum_k β_k exp(2iθ_k).
- For plane vectors, u × v = u_1 v_2 - u_2 v_1.
- D^nV(x)[v_1, ..., v_n] is the n-th derivative of V at x in the directions v_1, ..., v_n. For fixed vectors t and s, V_s = DV[s], V_ts = D^2V[t, s], V_tts = D^3V[t, t, s], and so on. H is the 2 by 2 Hessian of V on the plane.
- The certificate's coordinates are A_1 = (0, 0), A_2 = (1, 0), A_3 = (a, b) with b > 0. A point is given by (β_2, β_3), and β_1 = 1 - β_2 - β_3. Σ_0 is the open simplex {β_2 > 0, β_3 > 0, β_2 + β_3 < 1}, which is T in these coordinates. The charge ratios are ρ_2 = q_2/q_1 and ρ_3 = q_3/q_1.
- Every triangle is similar to one in these coordinates. A similarity (rotation, translation, scaling, reflection) does not change the number or the kind of critical points, so nothing is lost.

## Part A. The structure lemmas (L1 to L7 of NOTES.md)

### Lemma 1 (planarity)

**Statement.** Every balance point lies in the plane of the charges. At a point of the plane that is not a site, ∂V/∂z = 0, the mixed derivatives ∂²V/∂x∂z and ∂²V/∂y∂z vanish, and ∂²V/∂z² = -C with C = sum_k q_k / r_k^3. So the balance points are exactly the critical points of V on the plane. At such a point the 3 by 3 Hessian is the block matrix diag(H, -C). In particular a balance point is non-degenerate in space exactly when it is non-degenerate on the plane.

**Proof.** Write X = (p, z) with p in the plane, and R_k = (|p - A_k|^2 + z^2)^(1/2). Direct differentiation gives:

- [D1] ∂(1/R_k)/∂z = -z / R_k^3.
- [D2] ∂²(1/R_k)/∂z² = -1/R_k^3 + 3z^2/R_k^5. At z = 0 this is -1/r_k^3.
- [D3] ∂²(1/R_k)/∂p_j∂z = 3z (p_j - A_k,j) / R_k^5. At z = 0 this is 0.

By D1, ∂V/∂z = -z sum_k q_k/R_k^3. The sum is positive, so ∂V/∂z = 0 forces z = 0. At z = 0 the gradient of V in space is the gradient on the plane with third component 0. So the critical points in space are the critical points on the plane. D2 and D3 give the block form of the Hessian. Its determinant is -C det H, and C > 0. ∎

### Lemma 2 (the Laplacian on the plane)

**Statement.** Away from the sites, the Laplacian of V on the plane is ΔV = sum_k q_k / r_k^3 = C > 0. So trace H = C > 0 at every point. Hence V has no local maximum on the plane away from the sites. A non-degenerate critical point is a minimum (det H > 0) or a saddle (det H < 0). At a degenerate critical point the eigenvalues of H are 0 and C. Near each site V tends to +∞, so the sites are peaks.

**Proof.** [D4] On the plane, the Hessian of 1/|y| is (3 y yᵀ - |y|^2 I) / |y|^5. Its trace is (3|y|^2 - 2|y|^2)/|y|^5 = 1/|y|^3. Summing with weights q_k gives ΔV = C. (The same follows from Lemma 1: 1/|X| is harmonic in space, so ΔV = -∂²V/∂z² = C.) At a local maximum H would be negative semidefinite, with trace <= 0, which is impossible. If det H > 0 and the trace is positive, both eigenvalues are positive. If det H < 0, they have opposite signs. If det H = 0, one eigenvalue is 0 and the other equals the trace. ∎

### Lemma 3 (index count)

**Statement.** Suppose every critical point of V on the plane is non-degenerate. Then there are finitely many, each is a minimum or a saddle, and s - m = 2, where s is the number of saddles and m the number of minima.

**The hypothesis matters.** At a degenerate critical point V can look like t^3 + s^2 (a fold point), which is neither a minimum nor a saddle. Configurations with degenerate points are handled in Corollary 11.1.

**Proof.**

(a) Each critical point is a minimum or a saddle, by Lemma 2.

(b) Finiteness. Lemma 4 below puts every critical point in T. Near a site A_k, |∇V(x)| >= q_k/r_k^2 - sum over l ≠ k of q_l/r_l^2, which is positive once r_k is small. So all critical points lie in a compact set K inside T, at positive distance from the sites. A non-degenerate critical point is isolated (inverse function theorem applied to ∇V). Infinitely many critical points in K would accumulate at a point of K. By continuity that point is critical, and it is not isolated, which is a contradiction. So there are finitely many.

(c) Count. Let F = ∇V, a smooth vector field on the plane minus the sites. For a closed curve γ on which F has no zero, w(F, γ) is the winding number of F along γ. Three standard facts are used.

- Poincaré-Hopf in the plane (the argument principle for vector fields). Let Ω be a closed disc with finitely many disjoint open discs removed from its interior, F smooth on Ω, and F without zeros on the boundary of Ω. Orient every circle counterclockwise. Then w(F, outer circle) is the sum of w(F, inner circle) over the inner circles plus the sum of the indices of the zeros of F in Ω.
- The index of a non-degenerate zero is the sign of det DF = det H: +1 at a minimum and -1 at a saddle.
- Dog on a leash. If |F - G| < |G| along γ, then w(F, γ) = w(G, γ).

Small circle |x - A_k| = ε. Here F(x) = -q_k (x - A_k)/ε^3 + E(x), with |E(x)| <= sum over l ≠ k of q_l/r_l^2, which stays bounded as ε → 0. The main term G has length q_k/ε^2, so |E| < |G| for small ε. G points from x towards A_k and turns once as x goes once around. So w = +1.

Big circle |x| = R. [D5] F(x) = -Q x/R^3 + E(x), where Q = sum_k q_k and |E(x)| <= sum_k 2 q_k |A_k| / (R - |A_k|)^3. To see the bound, write F(x) = -sum_k q_k f(x - A_k) with f(y) = y/|y|^3. Then Df(y) = (I - 3 ŷŷᵀ)/|y|^3, whose eigenvalues are 1/|y|^3 and -2/|y|^3, so its operator norm is 2/|y|^3. Along the segment from x to x - A_k we have |y| >= R - |A_k|. The mean value inequality gives |f(x - A_k) - f(x)| <= 2|A_k|/(R - |A_k|)^3. The main term has length Q/R^2, which beats the error of order R^-3. It points inwards and turns once. So w = +1.

Take Ω to be the disc of radius R minus the three ε-discs. The zeros of F in Ω are all the critical points. So 1 = 3 + (m - s), that is, s - m = 2. ∎

[D6] The check computes these winding numbers for random configurations and finds +1 each time.

### Lemma 4 (the inverse map)

**Statement.** A point x of the plane, not a site, is a critical point of V exactly when x lies in T and q = λ (β_1 r_1^3, β_2 r_2^3, β_3 r_3^3) for some λ > 0. So every critical point lies in T, and each x in T is a critical point for exactly one ray of charge vectors. Write Z(x) = [β_1 r_1^3 : β_2 r_2^3 : β_3 r_3^3] for that ray. In the certificate's coordinates:

- [D7] ρ_k = q_k/q_1 = (β_k/β_1)(r_k/r_1)^3 for k = 2, 3. (`cert3.rho` writes (r_k/r_1)^3 as s√s with s = r_k^2/r_1^2.)

Moreover, for x in T and (k, l, n) cyclic:

- [D8] β_k = (A_l - x) × (A_n - x) / ((A_2 - A_1) × (A_3 - A_1)) = r_l r_n (u_l × u_n) / (2 Area), where Area is the signed area of (A_1, A_2, A_3). So Z(x) = [r_1^2 w_1 : r_2^2 w_2 : r_3^2 w_3] with w_k = u_l × u_n. This is the form `lib3.lami` uses (Lami's theorem).

**Proof.** [D9] The gradient of 1/|y| is -y/|y|^3. So ∇V(x) = -sum_k c_k (x - A_k) with c_k = q_k/r_k^3 > 0. This vanishes exactly when (sum_k c_k) x = sum_k c_k A_k, that is, when x = sum_k (c_k/C) A_k with C = sum_k c_k. The weights c_k/C are positive and sum to 1. Barycentric coordinates are unique because the sites are not on one line. So x lies in T and β_k = c_k/C, which says q_k = C β_k r_k^3. Conversely, if x is in T and q_k = λ β_k r_k^3, then c_k = λ β_k and ∇V(x) = -λ sum_k β_k (x - A_k) = -λ (x - sum_k β_k A_k) = 0.

For D8: β_k is the ratio of the signed area of the triangle (x, A_l, A_n) to that of (A_1, A_2, A_3). This is the standard area formula for barycentric coordinates. Twice the first area is (A_l - x) × (A_n - x) = (-r_l u_l) × (-r_n u_n) = r_l r_n (u_l × u_n). So β_k r_k^3 = r_1 r_2 r_3 r_k^2 w_k / (2 Area), and the common factor drops out of the ray. ∎

### Lemma 5 (the Hessian at a balance point, and the minimum criterion)

**Statement.** Let x be in T and q = λ (β_k r_k^3). Put M = sum_k β_k u_k u_kᵀ. Then:

- [D10] H = λ (3M - I), and λ = C = sum_k q_k / r_k^3.
- [D11] M = (1/2) [[1 + Re m, Im m], [Im m, 1 - Re m]].
- [D12] det M = (1 - |m|^2)/4. The eigenvalues of M are (1 ± |m|)/2. The eigenvalues of H are λ (1 ± 3|m|)/2.

Hence:

- (a) |m| < 1/3 exactly when H is positive definite, that is, when x is a non-degenerate local minimum of V.
- (b) |m| > 1/3 exactly when x is a non-degenerate saddle.
- (c) |m| = 1/3 exactly when x is degenerate.
- (d) Every local minimum, degenerate or not, has |m| <= 1/3.

Equivalent forms used by the programs:

- [D13] For |m| >= 0: det M > 2/9 holds exactly when |m| < 1/3, and exactly when λ_min(M)/λ_max(M) > 1/2. (`lib3.mu` returns λ_min/λ_max - 1/2.)
- [D14] Write m = |m| exp(iφ). At |m| = 1/3 the kernel of H is spanned by (-sin(φ/2), cos(φ/2)). In particular the kernel is the direction (1, 0) exactly when m = -1/3. (`cuspset.py` uses this.)
- [D15] |m| >= 2β_k - 1 for each k. (`cert3.m2_lower` and `verify_arb3.py` use this as an extra lower bound.)

**The word non-degenerate matters in (a).** At |m| = 1/3 the second derivative test says nothing, and whether x is a minimum depends on higher derivatives (Appendix A2). This is why line 26 of the note now says "non-degenerate minimum".

**Proof.** By D4, H = sum_k q_k (3 u_k u_kᵀ - I)/r_k^3 = sum_k c_k (3 u_k u_kᵀ - I). With c_k = λ β_k and sum_k β_k = 1 this is λ (3M - I), and λ = sum_k c_k = C. This is D10.

By the double angle formulas, u_k u_kᵀ = (1/2) [[1 + cos 2θ_k, sin 2θ_k], [sin 2θ_k, 1 - cos 2θ_k]]. Summing with weights β_k and using sum_k β_k = 1 gives D11, because Re m = sum_k β_k cos 2θ_k and Im m = sum_k β_k sin 2θ_k.

D12: by D11, det M = ((1 + Re m)(1 - Re m) - (Im m)^2)/4 = (1 - |m|^2)/4. M has trace 1, so its eigenvalues are (1 ± |m|)/2. So H has eigenvalues λ (3μ - 1) = λ (1 ± 3|m|)/2.

(a) to (c): λ > 0 and λ (1 + 3|m|)/2 > 0, so the sign of det H is the sign of 1 - 3|m|. (d) is the second order necessary condition: at a local minimum H is positive semidefinite, so 1 - 3|m| >= 0.

D13: (1 - |m|^2)/4 > 2/9 is |m|^2 < 1/9. And (1 - |m|)/(1 + |m|) > 1/2 is 2 - 2|m| > 1 + |m|, which is |m| < 1/3.

D14: H = (λ/2)(I + 3N) with N = |m| [[cos φ, sin φ], [sin φ, -cos φ]]. N is |m| times the reflection in the line at angle φ/2. So N v = -|m| v for v = (-sin(φ/2), cos(φ/2)), which is perpendicular to that line. At |m| = 1/3 this gives H v = 0. For m = -1/3 we have φ = π and v = (-1, 0).

D15: by the triangle inequality, |m| >= |β_k exp(2iθ_k)| - sum over l ≠ k of β_l = β_k - (1 - β_k), since the β_l are positive in T. ∎

**Remark (line 29 of the note, marked [I]).** Inversion in the unit circle about x sends the charge q_k at A_k to the charge q_k/r_k at x - u_k/r_k (Kelvin's rule for a point charge). [D16] Their second moment about x is sum_k (q_k/r_k)(u_k/r_k)(u_k/r_k)ᵀ = sum_k c_k u_k u_kᵀ = λ M. So by D13, x is a non-degenerate minimum exactly when the smaller principal moment of the inverted charges is more than half the larger.

### Lemma 6 (the isotropic point)

**Statement.** For every triangle, m has a zero x* in T. By Lemma 5(a), x* is a non-degenerate minimum of V for the charges Z(x*). So every triangle has a minimum for some charges.

**Proof.**

Step 1 (edges). [D17] On the open edge from A_l to A_n we have β_k = 0, and x - A_l and x - A_n point in opposite directions along the edge. So θ_l and θ_n differ by π, and exp(2iθ_l) = exp(2iθ_n) = exp(2iα), where α is the direction angle of the edge. Hence m = (β_l + β_n) exp(2iα) = exp(2iα). On each open edge, m is a constant of modulus 1.

Step 2 (corners). [D18] |m(x) - exp(2iθ_k(x))| <= 2(1 - β_k(x)). Indeed m - exp(2iθ_k) = (β_k - 1) exp(2iθ_k) + sum over l ≠ k of β_l exp(2iθ_l), and its modulus is at most (1 - β_k) + sum over l ≠ k of β_l = 2(1 - β_k). Also β_l = dist(x, line A_k A_n) / dist(A_l, line A_k A_n) <= r_k / h_l, where h_l is the height from A_l. So 1 - β_k = β_l + β_n <= c r_k for a constant c.

Step 3 (winding). Fix a small ε > 0. Let K_ε be the closed triangle minus the open discs of radius ε around the three vertices. K_ε is a closed topological disc, and m is continuous on it, since every r_k > 0 there and the formula for m is continuous up to the open edges. Orient the boundary of K_ε counterclockwise. It consists of three pieces of edges and three circular arcs. Define g on the boundary by g = exp(2iα) on each edge piece (so g = m there), and g = exp(2iθ_k) on the arc around A_k. At an end of that arc the point lies on an edge through A_k, and θ_k is that edge's direction modulo π, so g is continuous. |g| = 1, and on the arcs |m - g| <= 2cε < 1 for small ε. By the dog on a leash fact, m and g have the same winding number along the boundary.

The arc around A_k is traversed clockwise as seen from A_k, because the vertex lies outside K_ε. It runs from the direction of the incoming edge to the direction of the outgoing edge. So θ_k decreases by the interior angle γ_k, and arg g decreases by 2γ_k. On the edge pieces g is constant. In total arg g changes by -2(γ_1 + γ_2 + γ_3) = -2π. So the winding number of m along the boundary of K_ε is -1.

[D19] The check computes this winding number on random triangles and finds -1 each time.

Step 4. If m had no zero in K_ε, then m/|m| would be a continuous map from the disc K_ε to the circle. Its restriction to the boundary would then have winding number 0, because a loop that extends over a disc is null-homotopic. This contradicts Step 3. So m has a zero in K_ε, which lies in T. ∎

### Lemma 7 (the small-charge model)

**Where the model comes from (motivation only).** Put two charges q_2 and q_3 on the first axis at (-d_2, 0) and (d_3, 0), in balance at the origin: q_2/d_2^2 = q_3/d_3^2. [D20] The gradient of their potential V_0 vanishes at the origin, and its Hessian there is C_0 diag(2, -1) with C_0 = q_2/d_2^3 + q_3/d_3^3. So V_0(y) = V_0(0) + C_0 (y_1^2 - y_2^2/2) + O(|y|^3). Add a small charge ε = C_0 λ^3 at a point p near the saddle, and write y = p + λX. [D21] Then, leaving out the cubic remainder,

C_0 ((p_1 + λX_1)^2 - (p_2 + λX_2)^2/2) + ε/(λ|X|) = C_0 (p_1^2 - p_2^2/2) + C_0 λ^2 F_L(X),

with L = (-2p_1/λ, p_2/λ) and

F_L(X) = X_1^2 - X_2^2/2 + 1/|X| - L·X.

When p is of order λ, the remainder is of order λ^3, small against the main term C_0 λ^2. So F_L is the limit of the rescaled potential near the small charge as ε → 0 with p/λ fixed.

**What is and is not proved.** The lemma below is a statement about F_L only. Passing to actual small charges would need uniform convergence of the rescaled potential with two derivatives on the scaling window, control of minima outside the window, and uniformity in L near the L where F_L is degenerate. None of this is written in the thread. So line 43 of the note is a statement about the limit model, and it now says so.

**Statement.** Let L = (L_1, L_2) with L_1 ≠ 0. Then F_L has at most one local minimum on the plane minus the origin.

**Proof.**

Step 1 (critical points are roots of one equation). [D22] ∇F_L = (2X_1 - X_1/r^3 - L_1, -X_2 - X_2/r^3 - L_2) with r = |X|. Put c = 1/r^3 > 0. A critical point satisfies X_1 (2 - c) = L_1 and -X_2 (1 + c) = L_2. Since L_1 ≠ 0, c ≠ 2, and X = (L_1/(2 - c), -L_2/(1 + c)). Substituting into r^2 = c^(-2/3) gives

- [D23] g(c) := c^(2/3) [A/(2 - c)^2 + B/(1 + c)^2] = 1, with A = L_1^2 > 0 and B = L_2^2 >= 0.

Conversely, every root c in (0, 2) or (2, ∞) of g = 1 gives the point X = (L_1/(2 - c), -L_2/(1 + c)). It has |X|^2 = c^(-2/3) g(c) = c^(-2/3), so 1/|X|^3 = c, and the gradient equations hold. Different roots give different points, since they give different r. So critical points and roots correspond one to one.

Step 2 (the Hessian). [D24] Hess F_L = diag(2 - c, -1 - c) + 3c u uᵀ with u = X/r, and its trace is 1 + c > 0. Put a = u_1^2 and b = u_2^2. [D25] For D = diag(2 - c, -1 - c), det(D + 3c u uᵀ) = (2 - c)(-1 - c) + 3c [(-1 - c) a + (2 - c) b], by the rule det(D + v vᵀ) = det D + vᵀ adj(D) v. At a critical point, a = c^(2/3) A/(2 - c)^2 and b = c^(2/3) B/(1 + c)^2, so a + b = 1. The logarithmic derivative of g gives g'(c) = (2/(3c))(a + b) + 2a/(2 - c) - 2b/(1 + c). A direct computation gives the identity

det H = -(3c/2)(2 - c)(1 + c) g'(c) + (2 - c)(-1 - c)(1 - a - b).

So at a critical point, det H = -(3c/2)(2 - c)(1 + c) g'(c).

Step 3 (which roots can be minima).

- (i) If c > 2: for v perpendicular to u, vᵀ H v = (2 - c) v_1^2 + (-1 - c) v_2^2 < 0. So H is not positive semidefinite, and X is not a local minimum.
- (ii) If 0 < c < 2: (2 - c)(1 + c) > 0, so det H has the sign of -g'(c). A local minimum needs det H >= 0, so g'(c) <= 0. Since the trace is positive, a non-degenerate minimum is exactly g'(c) < 0.

Step 4 (the shape of g on (0, 2)).

- [D26] g'(c) = (c^(2/3)/(3c)) [4A(1 + c)/(2 - c)^3 - 2B(2c - 1)/(1 + c)^3].

On (0, 1/2] the first term in the bracket is positive and the second is >= 0, so g' > 0. On (1/2, 2):

- [D27] g'(c) = (2(2c - 1) c^(2/3) / (3c (1 + c)^3)) (A R(c) - B), with R(c) = 2(1 + c)^4 / ((2 - c)^3 (2c - 1)).

The prefactor is positive, so g' has the sign of A R(c) - B.

- [D28] R'(c)/R(c) = 4/(1 + c) + 3/(2 - c) - 2/(2c - 1) = 3(7c - 5) / ((1 + c)(2 - c)(2c - 1)).

So on (1/2, 2), R decreases strictly up to c = 5/7 and increases strictly after it, and R → +∞ at both ends.

- [D29] R(5/7) = 512/27.

Hence the set I = {c in (1/2, 2) : R(c) <= B/A} is a closed interval, a single point, or empty. On (0, 2), g' <= 0 exactly on I, and g' < 0 in the interior of I.

Step 5 (conclusion). By Step 3, a local minimum has its c in I. If I is a single point, there is at most one such c. Otherwise g is strictly decreasing on I, so g = 1 has at most one root in I. By Step 1, roots and critical points correspond one to one. So F_L has at most one local minimum. ∎

**Further facts, also checked.**

- [D30] On (2, ∞) both terms in D26 are negative. So g decreases strictly from +∞ to 0 there, and g = 1 has exactly one root, which is a saddle.
- On (0, 2), g rises from 0, may fall on I, and rises to +∞ as c → 2. So g = 1 has one or three roots there, counted with multiplicity, and a minimum needs 1/2 < c < 2. This is the "at most 3 roots on (0, 2)" of `NOTES.md`.
- [D31] If B/A < 512/27, that is |L_2| < (512/27)^(1/2) |L_1|, then I is empty and F_L has no minimum. The check finds every critical point for 80 random L as roots of the degree 12 polynomial y^2 [A(1 + y^3)^2 + B(2 - y^3)^2] - (2 - y^3)^2 (1 + y^3)^2 (put c = y^3 in D23), and confirms all of the above.

## Part B. The lemmas behind the computer proof

`run_cert3.py` proves, for a box S of triangle shapes (a, b), that V has at most one local minimum on every triangle in S. It works in three steps: exclusion and coverage (Lemmas 8 and 9), a local certificate for each leaf box (Lemma 12 for kind J, Lemma 13 for kind V), and a pair step (Lemma 14). It computes with interval arithmetic with outward rounding. The only property used here is the inclusion property: if every input lies in its interval, the computed interval contains the exact result. The shape enters through intervals for a and b, so every statement below holds for every triangle in S at once.

### Lemma 8 (exclusion)

**Statement.** Let B be a box in the (β_2, β_3) plane. Suppose a computed number ℓ satisfies ℓ <= |m(x)|^2 for every x in B that lies in Σ_0, and 9ℓ > 1. Then no point of B is a local minimum of V, for any charges.

Formulas used by `cert3.m2_lower` and `verify_arb3.m2_lower_bound`, with (dx, dy) = y_k:

- [D32] cos 2θ_k = 1 - 2dy^2/r_k^2 = 2dx^2/r_k^2 - 1, and sin 2θ_k = 2 dx dy / r_k^2.
- [D33] x = β_2 A_2 + β_3 A_3 = (β_2 + aβ_3, bβ_3), so y_1 = x, y_2 = x - (1, 0) and y_3 = x - (a, b).
- D15, used when the interval for 2β_k - 1 is positive.

**Proof.** Points outside T are never critical (Lemma 4). For x in B and in Σ_0, |m(x)|^2 >= ℓ > 1/9, so |m(x)| > 1/3, and x is not a local minimum by Lemma 5(d). The programs obtain ℓ as follows. Both expressions in D32 equal cos 2θ_k exactly, so the intersection of their interval enclosures with [-1, 1] still contains cos 2θ_k. The same holds for sin 2θ_k and [-1, 1]. Multiplying by the interval for β_k and summing gives intervals that contain Re m and Im m, and the lower end of Re^2 + Im^2 is a valid ℓ. When the interval for 2β_k - 1 is positive, D15 gives |m|^2 >= (2β_k - 1)^2 at every point of B in Σ_0, so the larger of the two lower bounds is still valid there. D15 needs every β_l >= 0, which is why the bound is claimed only on Σ_0. Points of B outside the triangle do not matter. ∎

### Lemma 9 (coverage: where a minimum can be)

**Statement.** If phase A of `run_cert3.py` ends with no box left to split, then every local minimum of V, on every triangle of S and for every charge vector, lies in one of the leaf boxes.

**Proof.** A local minimum is a critical point, so by Lemma 4 its coordinates (β_2, β_3) lie in Σ_0, and by Lemma 5(d) it has |m| <= 1/3. The program starts from the dyadic grid of side 2^-d_0 on [0, 1]^2 and keeps the boxes whose lower left corner has β_2 + β_3 < 1. These cover the closed simplex. Each later step keeps a box or replaces it by its four children, which cover it. A child is dropped only if its lower left corner has β_2 + β_3 >= 1, so that it has no point of Σ_0, or if Lemma 8 excludes it. A box leaves phase A only by getting a local certificate, and then it is a leaf. By induction on the steps, every point of Σ_0 with |m| <= 1/3 always lies in a kept box, and at the end in a leaf. `verify_arb3.py` re-derives this coverage with its own arithmetic. ∎

### Lemma 10 (the Jacobian of the inverse map, and where it vanishes)

**Statement.** On Σ_0 let G = (log ρ_2, log ρ_3), as a function of (β_2, β_3). Put e_2 = A_2 - A_1 = (1, 0) and e_3 = A_3 - A_1 = (a, b). For k and j in {2, 3}:

- [D34] ∂G_k/∂β_j = 1/β_1 + δ_kj/β_k + 3 (y_k · e_j)/r_k^2 - 3 (y_1 · e_j)/r_1^2.
- [D35] ∂ρ_k/∂β_j = ρ_k ∂G_k/∂β_j.
- [D36] Let E be the matrix with columns e_2 and e_3, and N the matrix with columns -y_2/r_2^3 and -y_3/r_3^3. Let H be the Hessian of V at x for the charges (1, ρ_2(x), ρ_3(x)). Then H E = -N diag(ρ_2, ρ_3) DG. Consequently, with λ = 1/r_1^3 + ρ_2/r_2^3 + ρ_3/r_3^3, det DG = λ^2 (1 - 9|m|^2) det E / (4 det N ρ_2 ρ_3), which vanishes exactly on the fold {|m| = 1/3}.

**Proof.** By D7, G_k = log β_k - log β_1 + (3/2) log r_k^2 - (3/2) log r_1^2. Since β_1 = 1 - β_2 - β_3, ∂(log β_1)/∂β_j = -1/β_1, and ∂(log β_k)/∂β_j = δ_kj/β_k. Since x = A_1 + β_2 e_2 + β_3 e_3, ∂x/∂β_j = e_j, and ∂((1/2) log r_k^2)/∂β_j = (y_k · e_j)/r_k^2. This gives D34. D35 is the chain rule for ρ_k = exp(G_k).

For D36, let Φ(x, ρ) be ∇V for the charges (1, ρ_2, ρ_3), that is Φ = -y_1/r_1^3 - ρ_2 y_2/r_2^3 - ρ_3 y_3/r_3^3. By Lemma 4, Φ(x, ρ(x)) = 0 on T. Differentiate along e_j: D_xΦ e_j + sum_k (∂Φ/∂ρ_k)(∂ρ_k/∂β_j) = 0. Here D_xΦ = H, ∂Φ/∂ρ_k = -y_k/r_k^3, and D35 gives ∂ρ_k/∂β_j. This is H E = -N diag(ρ) DG. For 2 by 2 matrices det(-X) = det X, so taking determinants gives det H det E = det N ρ_2 ρ_3 det DG. E is invertible because the triangle is non-degenerate. N is invertible because a point x of T is not on the line A_2 A_3, so y_2 and y_3 are independent. With det H = λ^2 (1 - 9|m|^2)/4 from D12 (here q = (1, ρ_2, ρ_3), so λ = sum_k q_k/r_k^3 as in D10), the formula follows. ∎

**Consequences.** A J certificate (Lemma 12) can never succeed on a box that meets the fold. Near the fold the certificate must use the valley test (Lemma 13). The critical values of Z are exactly the charge vectors for which V has a degenerate critical point.

### Lemma 11 (two consequences used by the note)

**Corollary 11.1 (counting).** Fix a triangle. Suppose that V has at most one minimum for every charge vector whose critical points are all non-degenerate. Then V has at most 4 non-degenerate balance points for every charge vector.

**Proof.** Suppose V has five distinct non-degenerate critical points for some charges q_0. By the implicit function theorem, each continues to a non-degenerate critical point for all q near q_0, and the five stay distinct. A degenerate critical point x for charges q has |m(x)| = 1/3 (Lemma 5(c)) and q = Z(x) (Lemma 4), so q is a critical value of Z (Lemma 10). By Sard's theorem the critical values have measure zero. So there are charges q arbitrarily close to q_0 for which every critical point is non-degenerate. For such q, Lemma 3 gives s - m = 2 with s + m >= 5, so m >= 2, a contradiction. ∎

So line 9 of the note holds for every charge vector, including those with degenerate balance points. The certificate gives more than the hypothesis: at most one local minimum of any kind, for every charge vector.

**Corollary 11.2 (the reduction, line 33 of the note).** V has two non-degenerate minima for some charges exactly when Z takes the same value at two different points of the minimum region {|m| < 1/3}.

**Proof.** If x ≠ y are non-degenerate minima for charges q, both are critical, so Z(x) = Z(y) = [q] by Lemma 4, and both have |m| < 1/3 by Lemma 5(a). Conversely, if x ≠ y in {|m| < 1/3} have Z(x) = Z(y) = [q], then both are critical points for q by Lemma 4, and both are non-degenerate minima by Lemma 5(a). ∎

### Lemma 12 (injectivity on a box: certificates of kind J)

**Statement.** Let N be a box [β_2^-, β_2^+] × [β_3^-, β_3^+] contained in Σ_0. Let J_kj (k, j in {2, 3}) be intervals such that ∂G_k/∂β_j(z) lies in J_kj for every z in N. Let Δ be an interval that contains M_22 M_33 - M_23 M_32 for every choice of numbers M_kj in J_kj. (The interval evaluation of J_22 J_33 - J_23 J_32 has this property, by the inclusion property.) If 0 is not in Δ, then G, and so Z, is one-to-one on N.

**Proof.** Let x and y be in N. N is convex, so the segment from x to y lies in N. By the fundamental theorem of calculus, applied to each component of G along the segment:

- [D37] G(y) - G(x) = M (y - x), with M_kj = ∫_0^1 ∂G_k/∂β_j(x + τ(y - x)) dτ.

Each integrand takes values in J_kj, so its average M_kj also lies in J_kj. Hence det M lies in Δ, so det M ≠ 0 and M is invertible. If G(y) = G(x), then M (y - x) = 0 and y = x. Finally, Z(x) = Z(y) means ρ(x) = ρ(y), which means G(x) = G(y). ∎

**Remarks.**

1. The hypothesis that N lies in Σ_0 is needed, because G is defined and smooth only there. The test enforces it. The leaf B inside N has a point in Σ_0, so if N left Σ_0, the interval of some β_k over N would contain 0. Then the enclosure of 1/β_k is unbounded (`iv.py` returns [-∞, ∞]) and the test fails. `verify_arb3.py` checks β_k > 0 explicitly. All archived J regions lie inside Σ_0 (check D47).
2. A pointwise condition, det DG(z) ≠ 0 at every z in N, would not be enough: it gives only local injectivity. For example, the complex exponential has Jacobian determinant e^(2x) > 0 everywhere but is not one-to-one on a box of height more than 2π. The argument above works because the interval determinant bounds det M for the mean value matrix M, whose entries are averages taken separately.
3. By Lemma 10, a box that meets the fold never passes this test.

### Lemma 13 (the valley lemma: certificates of kind V)

**Setting.** A cell is a parallelogram C = {c + τt + σs : |τ| <= h_t, |σ| <= h_s}, where t and s are linearly independent (they need not be orthonormal), and C contains no site. Q is a set of charge vectors. At each point put a = V_ts/V_ss and w = t - a s.

**Statement.** Suppose that for every q in Q:

- (V1) V_ss > 0 at every point of C;
- (V2) V_s < 0 at every point of the edge σ = -h_s, and V_s > 0 at every point of the edge σ = +h_s;
- and either (V3) D^3V[w, w, w] > 0 at every point of C, or D^3V[w, w, w] < 0 at every point of C;
- or (V4) D^4V[w, w, w, w] - 3 (D^3V[w, w, s])^2 / V_ss < 0 at every point of C.

Then for every q in Q, V has at most one local minimum in C.

**Proof.** Fix q and put f(τ, σ) = V(c + τt + σs), which is smooth near [-h_t, h_t] × [-h_s, h_s]. By the chain rule its partial derivatives are the directional derivatives: f_σ = V_s, f_σσ = V_ss, f_τσ = V_ts, and so on.

Step 1 (the valley floor). For fixed τ, f_σσ > 0 on [-h_s, h_s] by V1, so σ ↦ f_σ(τ, σ) is strictly increasing. By V2 it is negative at -h_s and positive at h_s. So it has exactly one zero σ*(τ), and |σ*(τ)| < h_s. By the implicit function theorem (f_σσ ≠ 0), σ* is smooth on [-h_t, h_t]. Put γ(τ) = c + τt + σ*(τ)s, a curve in C, and ψ(τ) = f(τ, σ*(τ)) = V(γ(τ)).

Step 2 (derivatives along the floor). Differentiating f_σ(τ, σ*(τ)) = 0 gives:

- [D38] σ*' = -V_ts/V_ss, so γ' = t + σ*' s = w.
- [D39] Hence D^2V[w, s] = V_ts + σ*' V_ss = 0 along γ.

Since DV(γ)[s] = 0 along γ:

- [D40] ψ' = DV(γ)[w] = DV(γ)[t].

Differentiating ψ' = DV(γ)[t], with t constant, gives D^2V[w, t]. By D39 this equals D^2V[w, w]:

- [D41] ψ'' = D^2V[w, w] = V_tt - V_ts^2/V_ss.

Differentiate ψ'' = D^2V(γ)[w, w]. The base point moves with velocity w, and w' = σ*'' s, so ψ''' = D^3V[w, w, w] + 2σ*'' D^2V[w, s]. The last term vanishes by D39:

- [D42] ψ''' = D^3V[w, w, w].

Differentiating D39, that is D^2V(γ)[w, s] = 0, gives D^3V[w, w, s] + σ*'' V_ss = 0:

- [D44] σ*'' = -D^3V[w, w, s]/V_ss.

Differentiate ψ''' = D^3V(γ)[w, w, w]: ψ'''' = D^4V[w, w, w, w] + 3σ*'' D^3V[w, w, s]. With D44:

- [D43] ψ'''' = D^4V[w, w, w, w] - 3 (D^3V[w, w, s])^2 / V_ss.

The programs expand these by multilinearity in the derivatives along t and s, with a = V_ts/V_ss:

- [D45] D^3V[w, w, w] = V_ttt - 3a V_tts + 3a^2 V_tss - a^3 V_sss; D^3V[w, w, s] = V_tts - 2a V_tss + a^2 V_sss; D^4V[w, w, w, w] = V_tttt - 4a V_ttts + 6a^2 V_ttss - 4a^3 V_tsss + a^4 V_ssss.

The programs check the signs in V3 and V4 at every point of C, not only on γ. Since γ lies in C, the signs hold along γ. Under V3, ψ''' has one strict sign on [-h_t, h_t]. Under V4, ψ'''' < 0 there.

Step 3 (a minimum of V gives a point where ψ' = 0 and ψ'' >= 0). Let x_0 = c + τ_0 t + σ_0 s in C be a local minimum of V. Then ∇V(x_0) = 0, so f_σ(τ_0, σ_0) = 0. By V2, |σ_0| < h_s, and by uniqueness σ_0 = σ*(τ_0), so x_0 = γ(τ_0). Then ψ'(τ_0) = DV(x_0)[t] = 0. The Hessian of V at x_0 is positive semidefinite (second order necessary condition), so ψ''(τ_0) = D^2V(x_0)[w, w] >= 0. Different minima have different τ_0, because x_0 = γ(τ_0).

Step 4 (there is at most one such point). Suppose τ_a < τ_b in [-h_t, h_t] with ψ'(τ_a) = ψ'(τ_b) = 0, ψ''(τ_a) >= 0 and ψ''(τ_b) >= 0.

- Under V3 with ψ''' > 0: by the mean value theorem there is ξ in (τ_a, τ_b) with ψ''(ξ) = (ψ'(τ_b) - ψ'(τ_a))/(τ_b - τ_a) = 0. Since ψ'' is strictly increasing, ψ''(τ_a) < ψ''(ξ) = 0, a contradiction. With ψ''' < 0, ψ'' is strictly decreasing and ψ''(τ_b) < ψ''(ξ) = 0, again a contradiction.
- Under V4: ψ'' is strictly concave on [τ_a, τ_b], so ψ''(τ) > min(ψ''(τ_a), ψ''(τ_b)) >= 0 for τ_a < τ < τ_b. So ψ' is strictly increasing on [τ_a, τ_b], which contradicts ψ'(τ_a) = ψ'(τ_b).

Steps 3 and 4 together prove the lemma. ∎

**Remarks.**

1. Interval soundness. The programs evaluate D45 and D43 on small sub-cells with interval arithmetic, treating V_ts, V_ss and the rest as separate intervals. By the inclusion property the result contains the true value at every point of the sub-cell, for every q in the interval box Q. They test V1 on every sub-cell and V2 on every piece of the two s-edges, so the hypotheses hold as stated. Check X9 runs the source lines of the three valley tests (`run_cert2.valley_vec`, which `run_cert3.py` uses, `cert3.valley_ok` and `verify_arb3.valley_check`) on symbols and confirms that they compute D45 and D43.
2. The lemma does not say that Z is one-to-one on C. Near the fold Z is two-to-one, since a minimum and a saddle share their charges (check N1). The lemma says that two minima cannot share their charges.
3. At a degenerate critical point with unit kernel vector t and unit s perpendicular to it, V_ts = 0 and w = t. Then ψ'''' = V_tttt - 3 V_tts^2/V_ss = 24κ, the cusp coefficient of `fold.py` (Appendix A2).

### Lemma 14 (assembly: the theorem for a shape box)

**Statement.** Let S be a shape box. Suppose the output of `run_cert3.py` has these properties.

- (E) Coverage as in Lemma 9.
- (A) Each leaf box B has a region N(B) that contains B. Either N(B) is a box that satisfies Lemma 12 (kind J), or N(B) is a cell C that satisfies Lemma 13 with Q an interval enclosure of {(1, ρ_2(x), ρ_3(x)) : x in B} (kind V).
- (B) Every pair of different leaves (B, B') is resolved. Here a pair of boxes (b, b') with b inside B and b' inside B' counts as resolved if (B1) the enclosures of ρ over b and over b' are disjoint, or (B2) b' lies in N(B), or (B3) b lies in N(B'), or (B4) every pair (c, c') of kept children of b and b' is resolved. A child is dropped only if it has no point of Σ_0 or Lemma 8 excludes it.

Then, for every triangle in S and every charge vector, V has at most one local minimum.

**Proof.** First a key fact (K): if x in B and y in N(B) are local minima of the same V, then x = y. For kind J: Z(x) = Z(y) by Lemma 4, and Z is one-to-one on N(B) by Lemma 12. For kind V: x is in B, so (1, ρ(x)) lies in Q, and the charges are a positive multiple of a member of Q. Scaling the charges does not move the minima. So x and y are two minima in C (x is in B, which lies in C) of a potential with charges in Q, and Lemma 13 gives x = y.

Now suppose x ≠ y are local minima of the same V. By (E), x lies in a leaf B and y in a leaf B'. By Lemma 4, ρ(x) = ρ(y). If B = B', then y lies in B, which lies in N(B), and (K) gives x = y. If B ≠ B', the pair (B, B') is resolved. Follow (B4) down. At each split, x lies in a kept child of the current b and y in a kept child of the current b', because the children cover their parent and a dropped child holds no local minimum. The descent ends at a pair (b, b') with x in b and y in b' that is resolved by (B1), (B2) or (B3). (B1) is impossible, because ρ(x) = ρ(y) lies in both enclosures. (B2) puts y in N(B) with x in B, and (K) gives x = y. (B3) is the same with the roles exchanged. Every case contradicts x ≠ y. ∎

**How the program meets (B).** The initial pair list sorts the leaves by the lower end of the ρ_2 enclosure and lists every pair whose enclosures overlap in both coordinates. An unlisted pair satisfies (B1). Listed pairs are split jointly, both boxes into four, until each sub-pair satisfies (B1), (B2) or (B3), with the same dropping rule as in Lemma 9. The case of one leaf uses B inside N(B), which holds by construction for kind J and is tested for kind V.

**Remark (a hypothesis the pair list needs).** The pair list compares endpoints of enclosures. An enclosure that came out as NaN would fail every comparison, so its leaf would be paired with nothing and silently treated as separated. This cannot happen in the archived run. Every leaf box lies inside Σ_0, with every β_k >= 0.21875 on it, so every enclosure is finite (check D47). The second program raises an error on any division by an interval that contains 0.

**The equilateral triangle.** [D46] The archived shape box is a = 1/2 and b in [0.8660254037844385, 0.8660254037844387], as binary floating point numbers. It contains √3/2: in exact rational arithmetic, (2b^-)^2 < 3 < (2b^+)^2. So Lemma 14 applies to the equilateral triangle, and by similarity to every equilateral triangle. By Corollary 11.1, every charge vector on it has at most 4 non-degenerate balance points.

[D47] The check also confirms the hypotheses of Lemmas 12 to 14 that concern the archived leaves: every leaf box and every J region lies inside Σ_0, each J region contains its box, and no valley cell contains a site (the margin is at least 0.43).

## Appendix A1. Derivatives of 1/|y|

[D48] For y ≠ 0, r = |y| and vectors a, b, c, e:

- D(1/r)[a] = -(y·a)/r^3.
- D^2(1/r)[a, b] = 3(y·a)(y·b)/r^5 - (a·b)/r^3.
- D^3(1/r)[a, b, c] = -15 (y·a)(y·b)(y·c)/r^7 + 3 [(a·b)(y·c) + (a·c)(y·b) + (b·c)(y·a)]/r^5.
- D^4(1/r)[a, b, c, e] = 105 (y·a)(y·b)(y·c)(y·e)/r^9 - 15 S_6/r^7 + 3 [(a·b)(c·e) + (a·c)(b·e) + (a·e)(b·c)]/r^5, where S_6 is the sum of the six terms (a·b)(y·c)(y·e), one for each way to choose the pair of vectors that are dotted with each other.

**Proof.** Each line follows from the one before by differentiating along the next vector, using D(y·a)[b] = a·b and D(r^-n)[b] = -n (y·b) r^(-n-2). This is standard. The check verifies every component in the plane. The derivatives of V are sum_k q_k times these, with y = y_k. This is what `cert3.tensors`, `verify_arb3.derivs` and `lib3.derivs` compute (checks X3 and X8).

## Appendix A2. The cusp coefficient

This appendix is not needed for the equilateral proof. It writes out the formulas behind the statements on cusps (`fold.py`, `cuspset.py`, `cusp_scan.py`).

At a degenerate critical point x, let t be a unit kernel vector of H and s a unit vector perpendicular to it. By Lemma 5, H = diag(0, λ) in the frame (t, s), so V_ts = 0, V_ss = λ and w = t. Let ψ be the valley function of Lemma 13 through x. Then ψ' = ψ'' = 0 at x, ψ''' = V_ttt, and

- [D49] ψ'''' = V_tttt - 3 V_tts^2/V_ss = 24κ, with κ = V_tttt/24 - V_tts^2/(8 V_ss), the coefficient `kap` of `fold.py`.

Near x, V(c + τt + σs) >= ψ(τ) for σ near σ*(τ), with equality on the floor, because f is convex in σ there. So x is a local minimum of V exactly when 0 is a local minimum of ψ. At a cusp point (V_ttt = 0) with κ ≠ 0, ψ(τ) = ψ(0) + κτ^4 + O(τ^5). So x is a degenerate local minimum if κ > 0, and not a local minimum if κ < 0. That nearby charges then have two minima when κ > 0 is the standard unfolding of the cusp singularity. The note uses it only as an inference [I].

**The formulas of cuspset.py.** Put t = (1, 0) and let φ_k be the angle of u_k (called psi in `cuspset.py`), so cos φ_k = u_k · t.

- [D50] D^3(1/r)[t, t, t] = -6 P_3(cos φ)/r^4, D^3(1/r)[t, t, s] = -3 sin φ (5cos^2 φ - 1)/r^4, and D^4(1/r)[t, t, t, t] = 24 P_4(cos φ)/r^5, with the Legendre polynomials P_3(c) = (5c^3 - 3c)/2 and P_4(c) = (35c^4 - 30c^2 + 3)/8. These follow from D48 with y = r (cos φ, sin φ).

By D14 the kernel is t exactly when m = -1/3. Together with sum_k β_k = 1, this condition is linear in β: β is the vector of barycentric coordinates of the point -1/3 with respect to the three points exp(2iφ_k) (`beta_of` in `cuspset.py`). By D8, β_k r_k is proportional to w_k = u_l × u_n = sin(φ_n - φ_l). Scaling the triangle makes the factor 1, so r_k = w_k/β_k, and the sites are A_k = x - r_k u_k.

- [D51] The identity sum_k w_k u_k = 0 shows that x has barycentric coordinates β with respect to these sites.
- [D52] With q_k = β_k r_k^3 (so λ = sum_k β_k = 1 and V_ss = 1): V_ttt = -6G, V_tts = -3 sum_k β_k^2 sin φ_k (5cos^2 φ_k - 1)/w_k, V_tttt = 24 sum_k β_k^3 P_4(cos φ_k)/w_k^2, and ψ'''' = 24K. Here G = sum_k β_k^2 P_3(cos φ_k)/w_k and K = sum_k β_k^3 P_4(cos φ_k)/w_k^2 - (9/8) (sum_k β_k^2 sin φ_k (5cos^2 φ_k - 1)/w_k)^2 are the functions computed by `cuspset.GK`.

So G = 0 is the cusp condition, and the sign of K is the sign of κ. Each line of D52 is D50 summed with weights q_k/r_k^4 = β_k/r_k = β_k^2/w_k or q_k/r_k^5 = β_k^3/w_k^2.

## What is not proved here

- The step from the model F_L to actual small charges (Lemma 7).
- The model of two charges in a uniform field (`l8_model.py`). The note already says it is not proved.
- The [I] statements of "The reduction" about folds, cusps and crossings, beyond Corollary 11.2 and Appendix A2.
- The soundness of the interval arithmetic itself: outward rounding in `iv.py`, and ball arithmetic in `verify_arb3.py`. This file proves the mathematical statements that the code tests. The reviewer's reading and the second program cover the arithmetic.
- The numerical scans of shapes and cusps.
