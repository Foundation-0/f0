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
