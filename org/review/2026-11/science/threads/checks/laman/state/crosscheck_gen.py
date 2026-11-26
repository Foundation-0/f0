import random
def henneberg(n, rng):
    E = {(0, 1)}; k = 2
    while k < n:
        V = list(range(k))
        if rng.random() < 0.5 or len(E) < 2:
            u, v = rng.sample(V, 2); E |= {(min(u, k), max(u, k)), (min(v, k), max(v, k))}
        else:
            u, v = rng.choice(sorted(E)); w = rng.choice([x for x in V if x not in (u, v)])
            E.discard((u, v)); E |= {(u, k), (v, k), (w, k)}
        k += 1
    return sorted(E)
