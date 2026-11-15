#!/bin/sh
P=../../../work/pc-venv/bin/python
for c in shape cell region; do
  echo "== corrupt $c" ; $P -O verify_arb3.py out/c3_equi 10 $c 2>&1 | tail -1
done
