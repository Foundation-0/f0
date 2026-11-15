# Note: rigid-realizations

Pinned head `rigid-realizations@298926c`. Marks: **[F]** fact, **[I]** inference.

## L880

**Statement.** For the 10-vertex minimally rigid graph with integer code 4778440734593 there are 17 rational bar lengths for which 880 distinct real realizations exist, counted up to rotation and translation.

**Independent check.** `checks/l880_independent.py`, output `checks/l880_independent.out`.

- [F] It reads only the edge list, the lengths, the pinned triangle and the 440 box centres from the certificate. It does not read the repository's preconditioner matrices and shares no code with it.
- [F] It confirms the graph has 17 edges and that every set of k vertices spans at most 2k - 3 of them, and it recomputes the integer code.
- [F] It confirms in rational arithmetic that the pinned triangle has the stated side lengths.
- [F] For each centre it builds its own preconditioner and proves that the box of radius 2^-26 holds exactly one real solution with an invertible Jacobian. Worst contraction bound 2.5e-4.
- [F] It confirms the 440 boxes are pairwise disjoint. Smallest separation 0.084 against a box width of 3.0e-8.
- [F] It raises an error instead of using `assert`, so it behaves the same under `python3 -O`. Run under `-O` on a copy of the certificate, each of these makes it exit 1 with a FAIL message: one edge length changed, one coordinate of a pinned vertex changed, one edge of the list replaced, one box duplicated, and one centre moved by 2^-12. A centre moved by less than the box radius still passes, as the argument allows.
- [I] Each solution has a mirror image with the third pinned vertex below the axis. A rotation or translation that fixes two distinct points is the identity, so the 880 are distinct.

**What rests on the repository's own count.** [I] That 880 is also the number of complex realizations, so that all of them are real. The repository computes 880 with its own implementation (`verify_capco_laman.py`) of a published recurrence (Capco and co-authors, 2018). The cited paper's abstract does not state 880. This pass did not write a second implementation.

**Prior work.** [F] Bartzos, Emiris, Legersky and Tsigaridas (arXiv:1811.12800) report 868 real solutions numerically for this graph and verify 860. The edge lengths in the repository's baseline certificate match the ones that paper lists.

**Novelty.** OPEN. A search on 15 November found no report of 880. A search cannot prove absence.

## Other rows

- L344: KNOWN. The same paper states that all embeddings can be real. The repository holds no certificate.
- G160, at least 132: REPRODUCED. The paper already reports 132 numerically at these lengths. The repository adds an exact certificate.
- [F] Reader findings: the paper quotes 0.001493 as a contraction constant where the verifier prints 0.00098859, and one verifier docstring states as fact what the notes call a conjecture. The file of solutions used to find the lengths is not in the repository, so the search cannot be replayed. None of these affects the certificate.
