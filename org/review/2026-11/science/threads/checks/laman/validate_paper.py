import re, time, sys
from laman_count import *
# Maximal-Laman-number graphs as drawn in the paper's final figure (edge lists from the TeX source)
tex = open('sources/paper.tex').read()
fig = tex[tex.index(r'\section{Laman graphs with maximal Laman number}'):]
blocks = re.findall(r'% n ?= ?(\d+)\n(.*?)\\end\{tikzpicture\}', fig, re.S)
paper = {}
for n, body in blocks:
    verts = re.findall(r'\\vertex \((\w+)\)', body)
    idx = {v: i for i, v in enumerate(verts)}
    es = re.findall(r'\((\w)\)edge\((\w)\)', body)
    paper[int(n)] = [(idx[a], idx[b]) for a, b in es]
EXPECT = {6: 24, 7: 56, 8: 136, 9: 344, 10: 880, 11: 2288, 12: 6180}
maxn = int(sys.argv[1]) if len(sys.argv) > 1 else 10
for n in sorted(paper):
    if n > maxn: continue
    e = paper[n]
    t = time.time()
    L = laman_number(e)
    print(n, 'edges', len(e), 'laman?', is_laman(n, e), 'code', encode(e), 'L =', L, 'expected', EXPECT[n], 'OK' if L == EXPECT[n] else 'MISMATCH', '%.1fs' % (time.time() - t), flush=True)
