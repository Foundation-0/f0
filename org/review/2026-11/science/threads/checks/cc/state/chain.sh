#!/bin/sh
# One sequential chain, so that with the n=10 census at most 2 worker processes run at once.
cd "$(dirname "$0")"
P=../../work/pc-venv/bin/python
cert() { n=$1
  $P cert_arb.py census_out/census_n$n.json cert_n$n.json > cert_n$n.out 2>&1
  $P -I verify_rational.py cert_n$n.json > verify_n$n.out 2>&1
  $P -I -O verify_rational.py cert_n$n.json > verify_n${n}_O.out 2>&1
  $P compare_lit.py cert_n$n.json sources/ferrario.txt > compare_n$n.out 2>&1; }
until grep -q '^done' census_out/census_n9.json.log; do sleep 10; done
cert 9
MODE=newton STARTS=cluster $P census.py 8 900 21 census_out/census_n8_newton_cluster.json > census_out/n8nc.nohup 2>&1
until grep -q '^done' census_out/census_n10.json.log; do sleep 10; done
cert 10
MODE=newton STARTS=cluster $P census.py 9 900 22 census_out/census_n9_newton_cluster.json > census_out/n9nc.nohup 2>&1
date > chain.done
