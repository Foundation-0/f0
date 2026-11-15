#!/bin/sh
cd "$(dirname "$0")"
P=../../work/pc-venv/bin/python
until [ -f chain.done ]; do sleep 10; done
TIGHT=1 $P census.py 9 600 32 census_out/census_n9_tight.json > census_out/n9t.nohup 2>&1 &
until grep -q '^done' census_out/census_n8_tight.json.log 2>/dev/null; do sleep 10; done
TIGHT=1 $P census.py 10 600 33 census_out/census_n10_tight.json > census_out/n10t.nohup 2>&1
wait
date > chain2.done
