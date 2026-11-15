#!/bin/sh
# Certify several fixed triangles (exact dyadic vertices), two at a time.
P=../../../work/pc-venv/bin/python
run() { $P run_cert3.py $1 $1 $2 $2 out/c3_$3 5 8 2 6 > out/c3_$3.log 2>&1; }
run 0.0 1.0 right_isosceles &
run 0.25 0.25 obtuse &
wait
run 0.375 0.625 scalene &
run 0.5 0.125 flat8 &
wait
