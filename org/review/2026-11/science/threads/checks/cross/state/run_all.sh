#!/bin/sh
# Rerun everything in this thread (numerical). Run from this directory. About 1 hour on 2 cores.
PY=${PY:-../../work/pc-venv/bin/python}
mkdir -p out
# 1. complex counts: monodromy (several seeds) and total-degree homotopy
for s in 1 2 3 4; do $PY monodromy.py 3 2 $s 15 | tail -1; done > out/mono_n3.log
for s in 1 2 3; do $PY monodromy.py 4 3 $s 15 | tail -1; done > out/mono_n4.log
$PY tdh.py out/mono_n3_D2_s1.npz > out/tdh_n3.log
$PY tdh.py out/mono_n4_D3_s1.npz 4096 > out/tdh_n4.log
# 2. random real configurations (class split, orthant statistics)
$PY sample.py 3 2 3000 31 n3 > out/sample_n3.log
$PY sample.py 4 3 500 32 n4 > out/sample_n4.log
# 3. pushes (stage 1)
$PY push.py 3 2 triangle 20 11 n3_tri 150 > out/push_n3.log
$PY push.py 3 2 random 200 12 n3_rand 150 >> out/push_n3.log
$PY push.py 4 3 centre 10 21 n4_centre 80 > out/push_n4.log
$PY push.py 4 3 random 40 22 n4_rand 80 >> out/push_n4.log
# 4. pushes (stage 2; start files are written from stage-1 output, see NOTES.md section 7)
$PY push2.py 3 2 out/starts_n3_four.json 41 n3_four 300 8 > out/push2_n3.log
$PY push2.py 3 2 out/starts_n3_rand2.json 91 n3_rand2 300 8 > out/push2_n3_rand2.log
$PY push2.py 4 3 out/starts_n4_a.json 51 n4_a 120 4 > out/push2_n4_a.log
$PY push2.py 4 3 out/starts_n4_b.json 61 n4_b 250 6 > out/push2_n4_b.log
$PY push2.py 4 3 out/starts_n4_c.json 81 n4_c 250 6 > out/push2_n4_c.log
$PY push2.py 4 3 out/starts_n4_rand2.json 71 n4_rand2 150 4 > out/push2_n4_rand2.log
# 5. analysis
$PY orthant.py 3 2 out/thetas_n3_all.json n3push > out/orthant_n3.log
$PY orthant.py 4 3 out/thetas_n4_all.json n4push > out/orthant_n4.log
$PY diag.py 4 3 out/th_n4b_minT.json 2 > out/diag_n4b2.txt
$PY diag.py 4 3 out/th_n4c_minT.json 0 > out/diag_n4c0.txt
$PY summarize.py > out/summary_all.txt
