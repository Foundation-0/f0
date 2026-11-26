#!/bin/sh
# Rerun everything in this thread (from this directory). Python 3.12 venv with numpy, scipy, python-flint, matplotlib.
P=../../../work/pc-venv/bin/python
# C. exploration (floating point)
$P scan_shapes.py 0 2 out/scan_shapes_0.json & $P scan_shapes.py 1 2 out/scan_shapes_1.json; wait   # ~1 h on 2 cores
$P summarize_scan.py                                   # -> out/scan_shapes_summary.txt
$P cusp_scan.py 200                                    # -> out/cusp_samples.npy (cusp type over the cusp surface)
$P l8_model.py                                         # -> out/l8_model.png (two charges in a uniform field)
$P l7_check.py                                         # numerical check of Lemma L7
$P plot_rmin.py "[(0.5,0.866),(0.5,0.1),(0.0,1.0),(1.5,0.5),(0.5,0.05),(0.9,0.2)]" out/rmin_examples.png
# D. rigorous certificates (primary engine: numpy intervals with outward rounding)
$P run_cert3.py 0.5 0.5 0.8660254037844385 0.8660254037844387 out/c3_equi 5 8 2 6       # equilateral, ~6 min
$P run_cert3.py 0.0 0.0 1.0 1.0 out/c3_right_isosceles 5 8 2 6                          # right isosceles
$P run_cert3.py 0.25 0.25 0.25 0.25 out/c3_obtuse 5 8 2 6                               # obtuse
# independent re-checks (python-flint arb; shares no code with the primary engine)
$P -O verify_arb3.py out/c3_equi 3000             # coverage + every leaf certificate (~25 min)
$P -O verify_pairs_arb3.py out/c3_equi 200 12     # phase B on 200 random non-trivial pairs
./run_corrupt.sh                                  # three corrupted certificates must be REJECTED
