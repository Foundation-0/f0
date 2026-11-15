# Exploration after the review of pull request 58

15 November 2026. New work by the reviewer, separate from the review verdict.

Labels follow the threads folder: [F] fact from a run or a proof, [I] inference, [C] conjecture. Programs are in checks/ beside this file.

## Three charges have no flat point

[F] No configuration of three positive charges has a point where the gradient and the whole Hessian of the potential both vanish. Four charges are the smallest case where such a point can exist.

Proof. Put the point at the origin. Write a(i) for charge i divided by the cube of its distance, and u(i) for its unit direction. A vanishing gradient gives a weighted sum of the site vectors equal to zero, with positive weights.

A vanishing Hessian gives a weighted sum of the rank-one matrices u(i) u(i)^T equal to one third of the total weight times the identity. The directions form what frame theory calls a tight frame.

For three charges the gradient condition puts all three directions in one plane through the origin. A sum of rank-one matrices in one plane has rank at most two. A multiple of the identity has rank three. The two conditions cannot both hold.

[F] A numerical search agrees. With the mean radius fixed at 1, the smallest flat residual found over 80 starts is 0.458 for three charges and 8e-14 for four. Program: checks/walls_and_flat.py.

[I] This says why the method that settled four charges cannot descend to three. It does not prove Maxwell's bound for three charges. Fold points are still possible, and the three-charge thread reduces the question to folds.

## The wall graph of the eleven-point configuration

[F] Gradient ascent from each index-2 point of the printed five-decimal configuration reaches two charges. The seven index-2 points give all six pairs of the four charges once, and the pair of charges 1 and 2 twice. Program: checks/walls_and_flat.py.

[I] This matches the wall count in four-charges-eleven.md, computed here with unrelated code. The total count is twice the number of index-2 points minus three. So thirteen points for four charges is the same question as eight walls.

[C] Open form of that question: which multigraphs on the charges can the gradient flow of a harmonic potential produce? A second doubled pair, or one tripled pair, would give thirteen.

## Both bounds are Delsarte bounds

[F] The codes thread uses Delsarte's linear programming bound for codes in Hamming space. Its polynomials are the Krawtchouk polynomials.

[F] A point flat to order p, with all charges at one distance, is a spherical design of strength p-1. Delsarte's bound for spherical designs then gives a charge count of at least about p squared over 4.

[I] One flat point gives at most its Milnor number of balance points, about (p-1) cubed. With p at most about twice the square root of the charge count, one flat point gives at most order n to the 3/2 points. Splitting the charges over several flat points gives less by the same count.

[C] Beating n to the 3/2 then needs a degeneracy that is not a single point. A critical curve forced by symmetry planes is the candidate the four-charge note already names and does not exclude. The same bound theory governs the code tables and the charge growth rate.

## The platonic ladder

[F] The centre of a platonic solid has multiplicity (d-1) cubed, where d is the degree of its first harmonic term. Cube and octahedron give 27. Icosahedron and dodecahedron give 125. The flat-centres thread proves a quartic with all 27 critical points real, and reaches 77 of 125 at the icosahedron centre.

[F] The tetrahedron is the exception: 11, not 8. Its cubic term is xyz. The gradient of xyz vanishes along all three axes, so the singularity is not isolated at cubic order. The quartic term then adds one point along each axis.

[I] The exception is what makes the four-charge count reachable. A generic cubic flat point caps at 8 nearby points. The tetrahedron gives 11 in one place.

## Where the code bound saturates

[F] Of the 2,879 improved cells, 2,440 improve the distance bound by one step. 430 improve by two steps, 8 by three, and 1 by four. Counted from improved_cells.csv in the threads folder.

[F] GF(9) has 531 table cells that the table's own closure rules already improve. GF(7) and GF(8) have none. That asymmetry sits in summary.json and is not remarked in codes.md.

[C] The one-step pile-up marks where the linear programming bound stops. Those cells are the natural targets for semidefinite bounds of Schrijver type, under the same exact-certificate discipline.

## Open avenues, ordered by cost

1. Run the dense verifier on A269766. One run closes the 237 against 238 gap in the square thread.

2. Solve for four-charge configurations by wall count. Treat the eight-wall question above as the target, in place of a direct search for thirteen points.

3. Test whether a critical curve can carry more points per charge than a flat point. Symmetric ring families are the cheapest test bed. Their axis equation is one-dimensional, so high-order vanishing along the axis costs few parameters.

4. Apply semidefinite bounds to the saturated code cells. The exact-certificate format from the codes thread carries over with rational rounding.
