"""Lead's own proof of a sample of the recurrences, sharing no code with the thread's builder or verifier.
For each chosen entry: read the OEIS name and the claimed coefficients from the certificate, build a row-by-row
machine straight from the name (state = last row and the number of qualifying pairs so far, capped), compute a(n)
with exact integers, compare with the OEIS data terms, then check the recurrence residual is zero for D consecutive
n, where D is the dimension of this machine. By Cayley-Hamilton that proves it for every later n."""
import json, re, sys, itertools, glob, os
WORDS = {"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12}
def parse(name):
    m = re.match(r"Number of\s+(n|\d+)\s*X\s*(n|\d+)\s+(binary|0\.\.(\d+)) arrays with some element plus some (.+?) adjacent neighbor totalling (\w+) (no more than once|not more than once|exactly once)\.?$", name)
    if not m: return None
    a, b, alpha, top, nb, tot, mode = m.groups()
    q = 2 if alpha == "binary" else int(top) + 1
    kinds = set()
    for w in re.split(r"[ ,]+", nb.replace(" or ", " ")):
        w = w.strip()
        if w == "horizontally": kinds.add("H")
        elif w == "vertically": kinds.add("V")
        elif w == "diagonally": kinds.add("D")
        elif w == "antidiagonally": kinds.add("A")
        elif w: return None
    if a == "n": k = int(b)                       # n rows, k columns
    else:                                         # k rows, n columns: transpose, which swaps H and V
        k = int(a); kinds = {{"H":"V","V":"H"}.get(x, x) for x in kinds}
    return dict(k=k, q=q, kinds=kinds, total=WORDS[tot], exact=(mode == "exactly once"))
