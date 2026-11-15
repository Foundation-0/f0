"""Laman number of the exact 1-based edge list in graph12.json, using S/threads/laman/laman_count.py (imported, not copied)."""
import json, sys, time
sys.path.insert(0, sys.argv[1])
from laman_count import laman_number, is_laman
g = json.load(open("graph12.json"))
E = [tuple(e) for e in g["edges"]]
t = time.time()
E0 = [(a - 1, b - 1) for a, b in E]
print("is_laman (0-based copy):", is_laman(g["n"], E0))
print("Laman number of the 1-based edge list:", laman_number(E), f"({time.time()-t:.1f}s)")
