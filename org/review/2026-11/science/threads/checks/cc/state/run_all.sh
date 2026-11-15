#!/bin/sh
# Rerun everything from the thread directory (S/threads/cc).  Run at most two censuses at a time.
# Censuses are floating point and only find candidates; cert_arb.py and verify_rational.py are the proofs.
P=../../work/pc-venv/bin/python
cd "$(dirname "$0")"
# 1. censuses (seconds of wall clock as 2nd argument, seed as 3rd)
$P census.py 8 1200 11 census_out/census_n8.json
$P census.py 9 1800 12 census_out/census_n9.json
$P census.py 10 1500 13 census_out/census_n10.json
MODE=newton STARTS=cluster $P census.py 8 900 21 census_out/census_n8_newton_cluster.json
MODE=newton STARTS=cluster $P census.py 9 900 22 census_out/census_n9_newton_cluster.json
TIGHT=1 $P census.py 8 600 31 census_out/census_n8_tight.json
TIGHT=1 $P census.py 9 600 32 census_out/census_n9_tight.json
TIGHT=1 $P census.py 10 600 33 census_out/census_n10_tight.json
TIGHT=1 STARTS=decagon $P census.py 10 20 8 census_out/test_n10_dec.json
# 2. union of runs, certificate (Arb), independent verifier (exact rationals, also under -O), comparison
$P merge_census.py census_out/merged_n8.json census_out/census_n8.json census_out/census_n8_newton_cluster.json census_out/census_n8_tight.json > merge_n8.out
$P merge_census.py census_out/merged_n9.json census_out/census_n9.json census_out/census_n9_newton_cluster.json census_out/census_n9_tight.json > merge_n9.out
$P merge_census.py census_out/merged_n10.json census_out/census_n10.json census_out/census_n10_tight.json census_out/test_n10_dec.json > merge_n10.out
for n in 8 9 10; do
  $P cert_arb.py census_out/merged_n$n.json cert_n$n.json > cert_n$n.out
  $P -I verify_rational.py cert_n$n.json > verify_n$n.out
  $P -I -O verify_rational.py cert_n$n.json > verify_n${n}_O.out
  $P compare_lit.py cert_n$n.json sources/ferrario.txt > compare_n$n.out
done
# 3. corruption tests (each line must be FAIL or REJECT)
sh corrupt_tests.sh > corrupt_tests.out 2>&1
