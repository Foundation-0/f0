"""Independent brute force. Enumerates every array of the literal shape (rows x cols) of the OEIS definition and counts
(element, neighbour) pairs directly from cell coordinates. Shares no code with fsm.py or the verifier.
Neighbour relations in literal coordinates: H right (0,+1), V down (+1,0), D down-right (+1,+1), A down-left (+1,-1)."""
import numpy as np
OFFS = {'H': (0, 1), 'V': (1, 0), 'D': (1, 1), 'A': (1, -1)}

def count_literal(q, nbrs, total, rows, cols, chunk=1 << 20):
    """Return (exactly_one, at_most_one) over all q^(rows*cols) arrays."""
    cells = rows * cols
    N = q ** cells
    exact = atmost = 0
    for lo in range(0, N, chunk):
        idx = np.arange(lo, min(N, lo + chunk), dtype=np.int64)
        digits = []
        x = idx.copy()
        for _ in range(cells):
            digits.append((x % q).astype(np.int8)); x //= q
        pairs = np.zeros(len(idx), dtype=np.int8)
        for r in range(rows):
            for c in range(cols):
                for d in nbrs:
                    dr, dc = OFFS[d]
                    r2, c2 = r + dr, c + dc
                    if 0 <= r2 < rows and 0 <= c2 < cols:
                        pairs += ((digits[r * cols + c] + digits[r2 * cols + c2]) == total)
        exact += int((pairs == 1).sum()); atmost += int((pairs <= 1).sum())
    return exact, atmost

def literal_terms(spec, max_cells=22):
    """Brute-force values a(n) for n = 1.. while q^(cells) is small. Literal orientation of the definition."""
    out = []
    n = 1
    while True:
        rows, cols = (n, spec['k']) if spec['orient'] == 'nxk' else (spec['k'], n)
        if rows * cols * np.log2(spec['q']) > max_cells: break
        e, a = count_literal(spec['q'], spec['nbrs'], spec['total'], rows, cols)
        out.append(e if spec['mode'] == 'exact' else a)
        n += 1
    return out
