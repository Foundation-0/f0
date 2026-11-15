# Thread: how far one standard bound improves the published code tables

Follow-up to the science pass, 15 November 2026. Pinned head `gfq-codes@9200a06`. Marks: **[F]** fact, **[I]** inference.

## Question

The repository shows that a standard method, the Delsarte linear programming bound, rules out a few linear codes that the reference tables at codetables.de still allow. Two questions followed. Are its two GF(7) base facts already published? And how many table entries does the same method improve if it is run over every open entry?

## Result

Table values were read from codetables.de on 15 November 2026. An entry "improves" when the method proves that no code exists at the upper distance the table shows.

| Field | Open entries tested | Entries improved | Base entries |
|---|---|---|---|
| GF(7), length up to 100 | 4,071 | 94 | 12 |
| GF(8), length up to 130 | 7,202 | 1,408 | 62 |
| GF(9), length up to 130 | 7,265 | 916 | 48 |

A base entry is one the method proves directly. The other improved entries follow from base entries by the standard rules listed below.

- [F] Every direct proof is an exact certificate. There are 1,519 certificate entries in all. All 1,519 pass three exact checkers: the two written with the scan, and the checker written earlier for the science pass (`checks/delsarte_independent.py` on draft PR 51).
- [F] Nine entries chosen at random were looked up live a second time. All nine match the values the scan used.
- [F] All 18 statements in the repository appear in the scan with the same bounds.
- [I] The counts are lower limits. The floating-point search returned nothing usable for several thousand entries, and those were not pursued.

For GF(9) the scan lists 1,377 entries. In 531 of them the table is not consistent with its own neighbours, so the improvement there needs no new method. The 916 above are what remains.

## New base entries over GF(7)

[F] No linear code exists with these parameters over GF(7), written as [length, dimension, distance]:

[55,10,40], [56,12,39], [66,23,38], [74,10,56], [92,8,73], [93,13,69], [94,16,67], [95,18,66], [98,8,78], [98,11,75], [99,13,74], [100,16,72].

The first and fourth are the repository's two base facts. The other ten are new here. [F] Entries [56,12,39] and [57,12,40] lie inside the range the repository says it swept (`results/gf7-upper-bounds/PROOF.md`) and are not in its list.

## Is it already known?

- [F] The table's own page says its upper bounds come from Brouwer's tables, except GF(7) above length 50, where "the upper bounds are rather weak". It names Daskalov for small dimensions. It does not name the linear programming bound.
- [F] Maruta's published tables cover dimension 4 only for these fields. The base entries above have dimension 8 or more.
- [I] No earlier report of these exclusions was found. The search was about ten web queries. Two papers by Daskalov and co-authors could not be read. So this is "no earlier report found", not a priority claim.

The method is fifty years old. What is new, if anything, is that nobody has run it across these tables and sent in the result.

## The rules used to extend a base entry

Write u(n,k) for the largest possible distance at length n and dimension k. [F] The scan uses four standard facts and repeats them until nothing changes: u(n,k) is at most u(n-1,k)+1 (puncture), at most u(n-1,k-1) (shorten), at most u(n,k-1) (subcode), and at most u(n+1,k) (pad with a zero).

## Rerun

```
# save the three whole-table pages as sources/t7.html, t8.html, t9.html, from
#   http://www.codetables.de/BKLC/Tables.php?q=7&n0=1&n1=100&k0=1&k1=100   (130 for q = 8 and 9)
python3 parse.py && python3 scan2.py 7 && python3 build_certs.py 7 && python3 analyze.py
python3 -I -O verify_certs.py certs/gf7_certs.json
python3 -I -O verify_binomial.py certs/gf7_certs.json
python3 verify_codes.py <path to delsarte_independent.py> .
```

The scan needs NumPy and SciPy. The three checkers need only the standard library. `improved_cells.csv` lists every improved entry and `base_cells.csv` the 122 base entries.

## Not verified

- Whether any of these bounds is already in a paper not found here.
- The entries where the floating-point search failed.
- The theorem is used as published. It is not formalised.

## Next steps

1. Send the base entries to the table's maintainer. A draft message is in the comment on the repository's contact issue. A person should send it.
2. Run the search in exact or high-precision arithmetic to pick up the failed entries.
3. Add the constraints that hold only for linear codes. They can only strengthen the bounds.
