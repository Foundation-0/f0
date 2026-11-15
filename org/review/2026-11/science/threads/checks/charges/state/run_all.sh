#!/bin/sh
# Final run of the independent checker on all five certificates (plain python and python -O).
P=S/work/pc-venv/bin/python
C=S/repos/point-charges/certificates
for c in n3-triangle:n3 n4-triangle-plus-centre:n4 n5-abk-bipyramid:n5 n6-abk-plus-centre:n6 n7-abk-second-pair:n7; do
  f=${c%%:*}; o=${c##*:}
  $P -I -O S/threads/charges/indep_count.py $C/$f.json S/threads/charges/out/$o.json > S/threads/charges/out/$o.log 2>&1
  echo "$o exit=$?"; grep -E "RESULT|AGREES|MISMATCH|FAILURE" S/threads/charges/out/$o.log
done
