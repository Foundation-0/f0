#!/bin/sh
# Run the independent checker under python -O on corrupted inputs. Exit codes: 0 agree, 2 mismatch, 3 proof failure.
for f in n7_count43 n5_q5_441 n6_site_moved n5_hints_garbage n7_q7_136000; do
  echo "=== $f"
  S/work/pc-venv/bin/python -I -O S/threads/charges/indep_count.py S/threads/charges/corrupt/$f.json S/threads/charges/out/corrupt_$f.json > S/threads/charges/out/corrupt_$f.log 2>/dev/null
  echo "exit=$?"
  grep -E "RESULT|MISMATCH|AGREES|FAILURE" S/threads/charges/out/corrupt_$f.log
done
