import sys, random, time, importlib.util
sys.path.insert(0, 'repo_copy')
import verify_capco_laman as rv
from laman_count import *
import crosscheck_gen as cg
from validate_paper_graphs import paper
rng = random.Random(7)
rows = []
graphs = [('paper max n=%d' % n, e, n) for n, e in sorted(paper.items()) if n <= 11]
for t in (4778440734593, 18120782205838348):
    n, e = decode(t); graphs.append(('code %d' % t, e, n))
for n in range(4, 10):
    for i in range(12):
        graphs.append(('random n=%d #%d' % (n, i), cg.henneberg(n, rng), n))
bad = 0
for name, e, n in graphs:
    a = laman_number(e)
    t = time.time(); b = rv.compute_c2([(x+1, y+1) for x, y in e]); dt = time.time() - t
    if a != b: bad += 1
    if name.startswith('paper') or name.startswith('code'):
        print(name, 'mine', a, 'repo', b, 'repo time %.1fs' % dt, flush=True)
print('graphs compared:', len(graphs), 'disagreements:', bad)
