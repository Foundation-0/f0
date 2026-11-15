#!/usr/bin/env python3
"""Independent (arb) re-check of phase B on a random sample of NON-TRIVIAL leaf pairs (pairs whose
leaf-level rho enclosures overlap), each refined recursively (split both boxes) until every sub-pair is
shown disjoint in rho or contained in a certified region of one of the two leaves.
Uses only verify_arb3.py (independent of the primary engine).
usage: verify_pairs_arb3.py prefix nsample maxdepth"""
import sys, json, random
import numpy as np
import verify_arb3 as V
from verify_arb3 import Iv, arb


def inside(T, X, r):
    if int(r[4]) == 1:
        NB = r[5:9]
        return NB[0] <= X[0] and X[1] <= NB[1] and NB[2] <= X[2] and X[3] <= NB[3]
    cc = r[9:17]
    A = lambda k: Iv(float(cc[k]))
    return V.box_in_cell(T, X, (A(0), A(1)), (A(2), A(3)), (A(4), A(5)), A(6), A(7))


def resolve(T, X, Y, LX, LY, depth, cnt):
    cnt[0] += 1
    RX = V.rho_centered(T, X); RY = V.rho_centered(T, Y)
    if any(not RX[k].overlaps(RY[k]) for k in range(2)):
        return True
    if inside(T, X, LY) or inside(T, Y, LX):
        return True
    if depth == 0:
        return False
    kx = [c for c in V.split4(X) if c[0] + c[2] < 1.0 and not V.excluded(T, c)]
    ky = [c for c in V.split4(Y) if c[0] + c[2] < 1.0 and not V.excluded(T, c)]
    return all(resolve(T, a, b, LX, LY, depth - 1, cnt) for a in kx for b in ky)


def main(argv):
    pre = argv[1]; ns = int(argv[2]); md = int(argv[3])
    meta = json.load(open(pre + '.json')); L = np.load(pre + '_leaves.npy')
    T = V.Tri(meta['shape'])
    R = [V.rho_centered(T, tuple(r[:4])) for r in L]
    rng = random.Random(7)
    got = 0; ok = 0; nodes = 0; trials = 0
    while got < ns:
        i, j = rng.randrange(len(L)), rng.randrange(len(L))
        trials += 1
        if i == j or any(not R[i][k].overlaps(R[j][k]) for k in range(2)):
            continue
        got += 1
        cnt = [0]
        res = resolve(T, tuple(L[i, :4]), tuple(L[j, :4]), L[i], L[j], md, cnt)
        nodes += cnt[0]; ok += res
        if got % 20 == 0:
            print('pairs %d ok %d nodes %d' % (got, ok, nodes), flush=True)
    print(json.dumps(dict(sampled_nontrivial_pairs=got, resolved=ok, nodes=nodes, trials=trials)))
    print('PHASE-B SAMPLE', 'ALL RESOLVED' if ok == got else 'SOME UNRESOLVED')


if __name__ == '__main__':
    main(sys.argv)
