#!/bin/sh
# Re-run the exact counts from this folder. Run it from checks/charges/. Needs python-flint and NumPy.
#   sh rerun.sh            the five repository counts (3 to 7 charges) and the three new configurations
# Each line of output ends with the count and whether it agrees with the count stored in the input file.
PY=${PY:-python3}
status=0
for f in certificates/n3-triangle.json certificates/n4-triangle-plus-centre.json certificates/n5-abk-bipyramid.json certificates/n6-abk-plus-centre.json certificates/n7-abk-second-pair.json configs/n4-second-family.json configs/n8.json configs/n9.json; do
  $PY -I -O indep_count.py "$f" | grep -E "RESULT|AGREES|MISMATCH|FAILURE" || status=1
done
# the repository's own verifier, in its corrected form, on the four-charge certificates in repository format
for f in ../four/verify/n4_eleven_short.repo.json ../four/verify/n4_eleven_flat.repo.json ../four/jet-route/n4_eleven_b12.repo.json; do
  $PY -O repo_verifier/verify_arb.py "$f" | tail -1 || status=1
done
exit $status
