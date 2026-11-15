# Recurrence proofs beyond A268881: full report

15 November 2026. Repository head pinned by the report: finite-state-proofs at 9eeb3da.

Short note for this thread: `../recurrences.md`.

S is the working folder of this thread. It is archived outside the repository. Paths that start with S/ point into it. Where a file was copied into the repository, its repository path is listed at the end.

---

# Recurrence proofs beyond A268881: how far the finite-state method goes

Thread directory: S/threads/oeis/. Date of the OEIS fetches: 2026-11-15.
Marks: [F] fact read or produced by a run I made. [I] my inference.

## 0. Result in six lines

- [F] I proved 211 OEIS "Empirical" recurrences for all n from an explicit start index, with exact integer arithmetic. 200 are new, 11 are the repository's own entries redone as controls.
- [F] They fall in 34 families (alphabet, neighbour set, sum, "exactly once" or "not more than once"). Widths 1 to 7, both "n X k" and "k X n" orientation.
- [F] No recurrence was false. Every range written in an OEIS line ("for n>7") equals the proved minimal start (121 cases). The 90 lines with no range hold from the first index where they can be written.
- [F] One verifier (verify_all.py) checks all 211 certificates in 25 s and rejects 105 of 105 corruptions, also under `python -O`.
- [F] The repository's zero-vector test is sufficient but not necessary. 8 of the 211 true recurrences never reach a zero vector. They need a scalar test over D consecutive indices (D = state count).
- [F] Limit: 25 more entries were skipped because the state graph is too big for my verifier (up to 24192 states, 158 million transitions). 27 strip entries have no recurrence to test. 43 diagonal "n X n" entries and 36 tables are outside the method.

## 1. What the counting problem is (task 1)

[F] Source: finite-state-proofs@9eeb3da:PROOF.md:8-42 and :44-86.

Take an array with n rows and w columns of binary cells. Call a neighbouring pair "occupied" if both cells are 1. Count each horizontal pair and each antidiagonal pair once. Antidiagonal pairs join cell (r,c+1) to cell (r+1,c). A268881 to A268885 count arrays with exactly one occupied pair (w = 3..7). A268989 to A268994 count arrays with at most one (w = 2..7).

Machine, as the repository builds it: a state is (k, last row), with k in {0,1} the number of occupied pairs so far.

Appending a row adds the pairs inside the new row and the antidiagonal pairs between the old and new row. A transition exists only if the total stays at most 1. The matrix T has the destination state as row index. The first-row vector v holds 1 for each state (k, r) with k = pairs inside r.

Proof argument in the repository: the array is the same thing as a path through the states, so the count for n rows is a sum of entries of T^(n-1) v.

Then the vector z_0 = q(T)v is formed, with q the characteristic polynomial of the recurrence, and z_(j+1) = T z_j. The scalar L(z_j) is exactly the recurrence residual at index d+1+j. If z_m = 0 for some m, the residuals vanish for all later j. The remaining finitely many residuals are computed.

[F] My own check of that argument: it is correct. The bijection is the only step that is not a computation. I did not machine-check it. [I] It is sound, because every pair of neighbouring cells lies in one row or in two consecutive rows, and the transition counts exactly those.

### The exact number of terms needed (worked out here, not taken from the repository)

Setting. a(n) = u M^(n-o) v for n >= o (o = first index), M an integer D X D matrix. A claimed recurrence of order d has p(t) = t^d - c_1 t^(d-1) - ... - c_d. Define the residual r_n = a(n) - sum c_i a(n-i) for n >= o+d (the first n where all the terms exist). Then:

1. r_n = u M^(n-o-d) w with w = p(M) v. This is plain expansion.
2. The sequence j -> u M^j w satisfies the order-D recurrence of the characteristic polynomial of M (Cayley-Hamilton). So if D consecutive residuals vanish, all later residuals vanish. By induction.
3. Hence: the recurrence holds for all n >= s if and only if r_n = 0 for s <= n <= s+D-1. It needs a(o) up to a(s+D-1), which is s+D-o terms.
4. D may be replaced by the dimension of the smallest M-invariant space containing w (the Krylov dimension of w). This is at most D.
5. The number cannot be lowered in general. Example (D = 3, a cyclic shift): the residuals are 0, 0, 1, 0, 0, 1, ... So D-1 zeros do not suffice.
6. Special case used by the repository: if the vector z_m = M^m w is zero, then the Krylov dimension is at most m, and no scalar window is needed. The residuals for n >= o+d+m vanish with no further check.
7. "Enough initial terms" is therefore not the OEIS data. The data section has 11 to 31 terms. The state counts are 7 to 2048. The terms needed come from the machine, not from the entry. The OEIS data only confirms that the definition was read correctly.

[F] scripts/lemma_check.py checks steps 1, 2 and 5 on 300 random integer systems with exact integers (output lemma_check.log).

How I applied it. Per sequence I compute z_0 and iterate. If z reaches 0 (vector chain), done. Otherwise I iterate until D consecutive scalar residuals are zero (scalar window), and then conclude by step 2. I use D = number of states, not the Krylov dimension, so scalar windows are longer than needed.

### Reproduction of the repository's eleven (control)

[F] My code gives the same state counts (12, 21, 36, 62, 106 for w = 3..7) and the same minimal start indices (5, 8, 10, 13, 17) as the repository. [F] I ran the repository's two verifiers unchanged: both pass. This is a reproduction of its numbers by my code built to the same design. The independent halves are the direct enumeration and the OEIS data (section 4).

## 2. Are the eleven still empirical? (task 2)

[F] Yes. Fetched on 2026-11-15 with `https://oeis.org/search?q=id:A268881&fmt=json` and its siblings, at most one request per second, cached in sources/. Output: check_eleven.log. For A268881-A268885 and A268989-A268994 the entry still has an "Empirical: a(n) = ..." line. The coefficients and initial terms equal finite-state-proofs sources.json. A268882 and A268991 carry "for n>7", which matches the proved start 8.

## 3. How I found candidates (task 3)

[F] Scanned ids A268870 to about A269111 one by one. Then ran 11 OEIS searches built on the phrase "adjacent neighbor totalling" and related words (each search returns at most about 110 entries, see harvest.log). Found 344 entries with that phrase in the name.

| group | count |
|---|---:|
| tables T(n,k) | 36 |
| diagonal "n X n" and others the parser does not read | 43 |
| strip entries (n X k or k X n) | 265 |
| of which with a recurrence in the entry text | 214 |
| of which with a recurrence only in Hardin's linked file | 24 (all complete, read and used) |
| of which with no recurrence anywhere | 27 |

Final accounting for the 238 strip entries with a recurrence: 211 proved, 25 skipped for cost, 2 skipped for cost in advance (A269095, A269107: q = 4, width 6, 3564 states).

[I] The list is not complete for the whole OEIS. It covers one family of definitions ("some element plus some neighbor totalling t"). Other Hardin families ("no 2 X 2 subblock ...") are also finite-state, but I did not write parsers for them. I stopped after those searches.

The goal said 20 to 40. I did all the cheap ones because the pipeline is automatic. If a smaller batch is wanted, the first 40 rows of table.md are enough.

## 4. What I built (task 4)

All in this directory. Three codes share no code with each other.

- scripts/fsm.py: the machine builder (numpy digit arrays). Writes the certificates.
- verify_all.py: the verifier. Rebuilds each machine from the stored definition with bitmasks, in standard-library Python. It does not read a graph from the certificate.
- scripts/brute.py: direct enumeration of every array of the literal shape of the OEIS definition (k rows, n columns for "k X n"), counting pairs from cell coordinates. For "k X n" the builder transposes the neighbour set and the brute force does not, so the transposition is checked too. verify_all.py also contains a small pure-Python enumeration of its own.

Per sequence I did:

1. Parsed the definition and the recurrence from the entry (own regex, spec.py).
2. [F] Machine terms equal all OEIS data terms, for all 211 (11 to 31 terms each).
3. [F] Direct enumeration equals the machine and the OEIS data for every size that fits in 2^22 boards (n from 1 to 11 depending on width, field brute_n in summary.json). The verifier repeats this for boards up to 12000 cases per size.
4. [F] Proof as in section 1: 203 vector chains, 8 scalar windows.
5. [F] The recurrence fails at start-1 whenever start is later than o+d. This is checked by a nonzero residual in the verifier.

## 5. Table (task 5)

- table.md and table.csv: one row per sequence: A-number, one-line definition, recurrence order, states, terms matched, start n, stated start, proof file, status. 211 rows.
- families.md: the same, by family.
- certs/A######.json: one certificate per sequence. It holds the definition, the OEIS terms with the entry hash, the coefficients, the graph digest, the residual chain or residual list, the start index.

Summary by number: orders 2 to 68. States 7 to 2048. Alphabets 2 to 7 values (binary 72, 0..2 70, 0..3 53, larger 16).

## 6. Findings

1. [F] No false recurrence among 211. The negative result is exact: for each, the proved start equals the stated start (121) or the first writable index (90).
2. [F] 61 of the 211 recurrences have order at least the number of terms printed in the entry. Those cannot be tested by the printed data. [I] They were found from the b-file (210 terms). I did not fetch b-files.
3. [F] Eight recurrences are true but have p(M)v nonzero: A268627, A268636, A268748, A268763, A268771, A268778, A268909, A268976. The repository's zero-vector certificate would not certify them.
   [F] Their scalar residuals are zero for D consecutive indices, which proves them.
   [I] The cause is probably symmetry: the machine is bigger than the sequence needs (value swap x -> t-x, or mirror), so p kills only what the counting vector sees.
4. [F] The definitions have one reading that fits all the data: count unordered neighbouring pairs whose values sum to t, once each. I found no ambiguity. "k X n" means k rows, matched with the literal orientation.
5. [F] The repository's claim that recurrences hold "from n = s" is confirmed by my independent minimal start computation for all 11 entries.

## 7. What limits the method

- [F] State growth. Rows kept are those with at most one pair inside. States for the binary "horizontal+antidiagonal" family: 12, 21, 36, 62, 106 for w = 3..7 (about x1.7 per column).
- [F] For 0..2 (n X k): 15 to 960 states (w = 2..7). For 0..3, width 5 gives 1080 to 2048 states. Width 6 gives 3564 or 8192 and width 7 gives 11664.
- [F] Transitions grow like the square of the row count: 0.2 million at 1080 states, 12.8 million at 11664 states. The check costs (order + chain length) sweeps over all transitions.
- [F] Skipped for cost (25 entries, list in table_summary.log). The largest was 24192 states and 158 million transitions (A269899).
- [I] Lumping states by symmetry (exact quotient, checked by the lumping rule) would shrink many of these by 2 to 8 times. I did not build it.
- [F] The method needs the definition to be a local rule on a strip of fixed width. The "n X n" entries and the table entries T(n,k) are out of scope. Entries with no explicit recurrence (27) give nothing to prove. Entries with "order 68 (see link)" needed the linked file, which I read.
- [F] The proof is for the sequence as defined. It says nothing about whether the recurrence order is minimal. I did not test minimality.
- [F] One more limit: wide strips are exactly where the OEIS has too few terms to test the recurrence, and the proof helps most there, but cost is highest there too.

## 8. Not verified

- The bijection between arrays and paths (section 1) is an argument. It is not machine-checked and not in Lean. The finite checks that support it are the direct enumeration and the OEIS data.
- Direct enumeration covers n up to 11 at most. For the widest strips it covers only n = 1 or 2, because the board count is exponential.
- b-files were not fetched. The 25 skipped entries are not proved. No priority claim: I did not search the literature for earlier proofs of these entries.
- Nothing was submitted to the OEIS. The comment drafts are in comments_draft.md and are not sent.

## 9. Rerun

```sh
cd S/threads/oeis
PY=S/work/pc-venv/bin/python
$PY -O verify_all.py certs            # 211 PASS, about 25 s
$PY verify_all.py certs               # same without -O
$PY test_corrupt.py                   # 105 of 105 rejected
$PY -O test_corrupt.py                # same under -O
$PY scripts/lemma_check.py            # the lemma on random systems
$PY scripts/check_eleven.py           # the eleven are still empirical
$PY scripts/build_certs.py            # rebuild all certificates from sources/ (about 6 min, no network)
$PY scripts/make_table.py             # rebuild table.md, table.csv
```

The network scripts are scripts/oeisfetch.py, harvest.py and fetch_links.py. They keep to one request per second and cache under sources/. Raw logs: build.log, verify_all.log, census.log, probe8.log, harvest.log.

## 10. Next concrete step

Build the exact lumping quotient with a checked lumpability condition. It is the cheapest way to clear the 25 skipped entries, and it should also give the true minimal order. Then have a human read the proof and decide where the certificates are published.

## Files

- table.md and table.csv: the 211-row table.
- families.md: the same table, by family.
- certs/A######.json: one certificate per sequence.
- verify_all.py and test_corrupt.py: the verifier and its corruption tests.
- comments_draft.md: OEIS comment drafts, not sent. The prose check was clean.
- scripts/: builder, brute force, fetchers and the lemma check.
- sources/: cached OEIS fetches.
- Logs: build.log, verify_all.log, check_eleven.log, lemma_check.log, probe8.log, harvest.log, census.log, table_summary.log.

## Where the named files are in the repository

Paths are relative to `org/review/2026-11/science/threads/`. Names that are not listed were not copied. `checks/STATE-NOTES.md` says why.

| Name in this report | Repository path |
|---|---|
| `build.log` | `checks/oeis/state/build.log` |
| `census.log` | `checks/oeis/state/census.log` |
| `certs/A######.json` | 211 files in `checks/oeis/certs/` |
| `check_eleven.log` | `checks/oeis/state/check_eleven.log` |
| `comments_draft.md` | `checks/oeis/comments_draft.md` |
| `families.md` | `checks/oeis/families.md` |
| `fetch_links.py` | `checks/oeis/scripts/fetch_links.py` |
| `harvest.log` | `checks/oeis/state/harvest.log` |
| `harvest.py` | `checks/oeis/scripts/harvest.py` |
| `lemma_check.log` | `checks/oeis/state/lemma_check.log` |
| `probe8.log` | `checks/oeis/state/probe8.log` |
| `scripts/` | `checks/oeis/scripts/` (13 files) |
| `scripts/brute.py` | `checks/oeis/scripts/brute.py` |
| `scripts/build_certs.py` | `checks/oeis/scripts/build_certs.py` |
| `scripts/check_eleven.py` | `checks/oeis/scripts/check_eleven.py` |
| `scripts/fsm.py` | `checks/oeis/scripts/fsm.py` |
| `scripts/lemma_check.py` | `checks/oeis/scripts/lemma_check.py` |
| `scripts/make_table.py` | `checks/oeis/scripts/make_table.py` |
| `scripts/oeisfetch.py` | `checks/oeis/scripts/oeisfetch.py` |
| `spec.py` | `checks/oeis/scripts/spec.py` |
| `summary.json` | `checks/oeis/state/summary.json` |
| `table.csv` | `checks/oeis/table.csv` |
| `table.md` | `checks/oeis/table.md` |
| `table_summary.log` | `checks/oeis/state/table_summary.log` |
| `test_corrupt.py` | `checks/oeis/test_corrupt.py` |
| `verify_all.log` | `checks/oeis/state/verify_all.log` |
| `verify_all.py` | `checks/oeis/verify_all.py` |
