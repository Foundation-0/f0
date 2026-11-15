import mpmath as mp
mp.mp.dps = 30
# Short certificate as printed in four-charges-eleven.md (5 decimals)
cfg = [
    (mp.mpf("0.26712"), (mp.mpf("-0.35180"), mp.mpf("-0.27373"), mp.mpf("-0.20165"))),
    (mp.mpf("0.28010"), (mp.mpf("-0.05642"), mp.mpf("0.44608"), mp.mpf("-0.21436"))),
    (mp.mpf("1"),       (mp.mpf("-0.00274"), mp.mpf("0.00705"), mp.mpf("0.84585"))),
    (mp.mpf("0.26274"), (mp.mpf("0.40862"), mp.mpf("-0.17404"), mp.mpf("-0.19749"))),
]
printed = [
    ((-0.00021, 0.00022, 0.00155), 2), ((-0.00540, 0.00212, -0.00514), 2),
    ((0.00014, -0.00055, -0.00251), 1), ((0.00583, -0.00243, 0.00455), 1),
    ((0.00041, -0.00328, -0.00342), 2), ((0.01945, -0.00805, 0.01529), 2),
    ((0.00395, 0.00287, -0.00454), 2), ((-0.01747, -0.01312, 0.01561), 2),
    ((-0.00487, -0.00360, 0.00427), 1), ((-0.00307, 0.02304, 0.01606), 2),
    ((-0.00088, 0.00615, 0.00431), 1),
]

def field(p):
    E = [mp.mpf(0)] * 3
    for q, s in cfg:
        d = [p[i] - s[i] for i in range(3)]
        r2 = sum(x * x for x in d)
        r = mp.sqrt(r2)
        for i in range(3):
            E[i] += q * d[i] / r**3
    return E

def hess(p):  # Hessian of potential U=sum q/r ; grad U = -E
    H = mp.matrix(3, 3)
    for q, s in cfg:
        d = [p[i] - s[i] for i in range(3)]
        r2 = sum(x * x for x in d)
        r = mp.sqrt(r2)
        for i in range(3):
            for j in range(3):
                H[i, j] += q * (3 * d[i] * d[j] / r**5 - (1 if i == j else 0) / r**3)
    return H

def newton(p):
    p = [mp.mpf(x) for x in p]
    for _ in range(60):
        E = field(p)
        if max(abs(x) for x in E) < mp.mpf("1e-25"):
            break
        J = -hess(p)  # dE/dp
        step = mp.lu_solve(J, mp.matrix([-x for x in E]))
        p = [p[i] + step[i] for i in range(3)]
    return p

roots = []
for seed, idx_claim in printed:
    r = newton(seed)
    res = max(abs(x) for x in field(r))
    ev = mp.eigsy(hess(r), eigvals_only=True)
    neg = sum(1 for e in ev if e < 0)  # index convention check below
    roots.append(r)
    print(f"seed->root res={mp.nstr(res,2)} eig={[mp.nstr(e,3) for e in ev]} neg={neg} claimed_idx={idx_claim} shift={mp.nstr(mp.sqrt(sum((r[i]-seed[i])**2 for i in range(3))),2)}")
mind = min(mp.sqrt(sum((roots[a][i]-roots[b][i])**2 for i in range(3)))
           for a in range(11) for b in range(a+1, 11))
print("min pairwise root distance:", mp.nstr(mind, 3))
print("charges all positive:", all(q > 0 for q, _ in cfg))
