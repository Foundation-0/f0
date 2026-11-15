# What the shared geometry implies

15 November 2026. Several threads in this folder turned out to have the same shape. This note states that shape exactly, tests it on the certified data, and draws out what follows. Marks: **[F]** fact from data or a run, **[P]** a published result, **[I]** inference, **[C]** conjecture.

## The shared shape

Four problems ask one question: how many real solutions can a system built from point sources have?

| Problem | Sources | What is counted | Known answer |
|---|---|---|---|
| Lensing by point masses, in a plane | n masses | images | at most 5n - 5, proved and reached [P] (math/0401188, astro-ph/0305166) |
| Balance points of point charges, in space | n charges | zeros of the field | Maxwell's (n-1)^2 is false. Linear growth is all that is known |
| Realizations of a rigid graph | edge lengths | placements | all complex ones can be real at 10 and 11 vertices [F] |
| Central configurations of equal masses | n masses | relative equilibria | proved lists to 7, certified lower bounds to 10 [F] |

In each, the configurations with the most solutions were found the same way: start at a very symmetric, degenerate arrangement and disturb it slightly.

## Walls: a picture that makes the count readable

For positive charges the potential rises without limit at each charge. Follow the field uphill from any point and you arrive at a charge. So space divides into one basin per charge.

- Each balance point of index 2 is one wall between two basins. Its two uphill branches end at the two charges it separates.
- So the walls form a network: the charges are the points and the walls are the links.
- [P] The Morse relation says index-2 points minus index-1 points equals n - 1. In the network that reads: the number of independent loops equals the number of index-1 points.
- The total count is twice the number of walls, minus n - 1.

[F] The program `checks/geometry/wall_graph.py` follows the two uphill branches of every index-2 point in each certified configuration. The loop count equals the index-1 count in every case, which confirms the picture.

| Configuration | Charges | Walls | Pairs that share a wall | Pairs with two or more walls | Loops, and index-1 points |
|---|---|---|---|---|---|
| triangle | 3 | 3 | 3 of 3 | none | 1, 1 |
| triangle and centre | 4 | 6 | 6 of 6 | none | 3, 3 |
| second four-charge family | 4 | 6 | 5 of 6 | one pair has 2 | 3, 3 |
| five charges, beats the bound | 5 | 14 | 9 of 10 | the three large pairs have 2 each | 10, 10 |
| six charges, beats the bound | 6 | 17 | 14 of 15 | the three large pairs have 2 each | 12, 12 |
| seven charges, beats the bound | 7 | 25 | 17 of 21 | the three large pairs have 3 each | 19, 19 |
| eight charges, meets the bound | 8 | 28 | 22 of 28 | the three large pairs have 3 each | 21, 21 |
| nine charges, meets the bound | 9 | 36 | 25 of 36 | the three large pairs have 4 each | 28, 28 |

The trace is numerical. In the symmetric configurations a few walls run exactly along an axis into another balance point. A tiny offset decides which charge they reach, so their endpoints are one of several equivalent choices.

## What Maxwell's bound really says

[I] Maxwell's count, (n-1)^2, is exactly the count of a network in which every pair of charges shares one wall and no pair shares two. With n(n-1)/2 walls the total is n(n-1) - (n-1) = (n-1)^2.

[F] The two configurations that meet the bound by being complete, the triangle and the triangle with a centre, are exactly that network.

[F] The configurations that beat the bound do it in one way. They put more than one wall between the same pair of charges. The three large charges share two walls per pair at five and six charges, three at seven and eight, and four at nine. Each added pair of small charges adds one more wall between each pair of large ones.

[F] The eight- and nine-charge configurations equal Maxwell's count without being his network. At nine charges 36 walls join only 25 of the 36 pairs. The equality of the totals is a coincidence. The row for nine charges was predicted in this note before it was traced.

[I] So the assumption hidden in Maxwell's bound is "one wall per pair". Nothing forces it. A pair can share as many walls as there are nested small charges to make them.

[F] The second four-charge family shows the same thing from the other side. It reaches Maxwell's 9 with one pair sharing two walls and one pair sharing none. The bound is reached without the network being complete.

## Why the planar bound is true and the spatial one is not

[P] In the plane the proof of 5n - 5 has two parts. A counting identity, the planar form of the Morse relation, ties the two kinds of image together. A second argument bounds one kind by 2n - 2. Together they give at most 3n - 3 saddles.

[I] A network drawn in a plane with n points has at most 3n - 6 links before links must cross or repeat. The planar bound on saddles is three more than that. So in the plane the number of walls is held down by flatness, and extra walls between one pair are scarce.

[I] In space there is no such limit on a network. Any number of links can join the same two points without crossing. That is the freedom the counterexamples use.

## What follows

**The right question about point charges.** [C] The question is not how many pairs there are. It is how many walls n charges can make. Three answers are possible, and each has a test.

- *Linear.* All known constructions give about 5.5 walls per charge. [F] The known count of index-1 points is (9n - 25)/2 for odd n and (9n - 30)/2 for even n.
- *Quadratic.* This needs a number of walls that grows with the number of pairs. [F] Random configurations are far from it: in the repository's sample of 25,108 random four-charge configurations, 25,054 have three walls, the least possible, and their network is a tree with no loop at all.
- *In between.* [C] The count of walls a small charge can add is set by how flat the potential can be made at the point where it is inserted. That is a local question about a single point, and it can be studied apart from the rest.

**Four charges.** [I] Beating 9 needs 7 walls. The second family already has a doubled wall and a missing pair. The target is a configuration that keeps the doubled wall and gains the missing one. The push in `maxwell-push.md` found a tenth balance point close by and blocked, which is consistent with being one wall short.

**Three charges.** [I] All balance points lie in the plane of the charges, so the network is planar. Beating 4 needs a fourth wall among three charges, which is a doubled wall. [F] At count 4 the push found no complex solution in the all-positive region in 333 of 344 configurations. [C] So a proof that three positive charges never share a doubled wall would settle the three-charge case.

**A general caution about pair-counting bounds.** [I] Maxwell's bound and the planar bound look alike and are both stated in terms of n. One is a theorem and one is false. The difference is that the planar bound rests on the shape of the plane and Maxwell's rests on counting pairs. A bound that counts pairs, in any of these problems, deserves the question: what stops a pair from being used twice?

**Constructions are nested.** [F] Each new small charge sits at a balance point of the structure before it, with a charge many orders of magnitude smaller: 4e-3, then 1e-13, then smaller still. From outside, the earlier structure is unchanged.

[I] So the count obeys a recursion, a fixed gain per insertion, and the growth rate is the gain divided by the charges spent. Raising the rate needs a better single insertion, not more insertions.

**The same device across problems.** [F] The rigid graph with all 2,288 realizations real lies within 0.8% of equal edge lengths. [P] The lens that reaches 5n - 5 is a regular polygon with a small mass at its centre, and maximal lenses can be grown one small mass at a time (1405.2785). [F] For 10 equal masses the classes that random search could not find sit beside the regular polygon.

[C] In each problem the largest counts are reached next to the most degenerate arrangement, because that is where the most sheets of solutions meet and can be pulled apart. A search for a record should start there.

**A link to the cluster question.** [I] The count of lensed images obeys the same kind of relation as the walls: for a lens with no singular centre the number of images is odd, with one of them at the centre. A halo with a capped core, as in `fabric.md`, is such a lens. A cusp suppresses the central image.

[I] So the central images of cluster lenses test the core that the particle hypothesis predicts. This is stated from memory of the lensing literature and was not re-read.

## Tests

1. Trace the wall network for the eight- and nine-charge configurations and confirm four walls per large pair at nine. Done: confirmed.
2. Search four-charge configurations near the second family for a seventh wall.
3. For three charges, look for any configuration with a doubled wall. One would give 6 balance points and disprove the bound of 4.
4. Measure, for a single small charge inserted at a balance point, the largest number of new balance points as a function of how flat the potential is there.
5. Draw the planar analogue: trace the saddle network of a maximal point-mass lens and compare with the flat-network limit.

## Rerun

```
python3 checks/geometry/wall_graph.py <result .json from indep_count.py> <certificate or config .json>
```

It needs python-flint and NumPy. Saved output is `checks/geometry/wall_graph.out`.

## Not verified

- The wall trace is numerical. The loop count agreeing with the index-1 count in eight configurations is a check, not a proof.
- The reading of the planar proof as a flatness limit is an interpretation, not a statement from the papers.
- The link to central images was not checked against the literature.
